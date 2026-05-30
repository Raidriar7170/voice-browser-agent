from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from voice_browser_agent.models import BrowserTaskRequest, ClarificationRequest
from voice_browser_agent.normalizer import MockLLMNormalizerClient, StructuredOutputNormalizer
from voice_browser_agent.trace_writer import sanitize_trace_dict
from voice_browser_agent.validator import NormalizerValidator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_MANIFEST = PROJECT_ROOT / "runtime/speech-to-task-adaptation-dataset/manifest.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runtime/speech-to-task-adaptation-eval"
DEFAULT_SPLIT = "test"
FORBIDDEN_MARKERS = (
    "raw_audio_path",
    "raw_screenshot",
    "browser_profile",
    "browser_profile_path",
    "cookie",
    "cookies",
    "raw_prompt",
    "raw_provider_prompt",
    "raw_provider_payload",
    "raw_provider_response",
    "provider_response",
    "provider_request",
    "credentials",
    "credential",
    "password",
    "token",
    "secret",
    "private_url",
    "request_header",
    "request_headers",
    "api_key",
    "authorization",
    "local_file_uri",
    "remote_host",
    "remote_vision_backend_url",
    "controlled_target_url",
    "checkpoint_path",
    "unsanitized_runtime",
    "raw_runtime",
    "file:///Users/",
    "file:///users/",
    "/Users/",
    "/users/",
)


class SpeechToTaskEvalError(RuntimeError):
    pass


def build_evaluation(
    dataset_manifest_path: Path = DEFAULT_DATASET_MANIFEST,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    split: str = DEFAULT_SPLIT,
    candidate_modes: list[str] | None = None,
    candidate_output_jsonl: dict[str, Path] | None = None,
) -> dict[str, Any]:
    dataset_manifest_path = Path(dataset_manifest_path)
    output_dir = Path(output_dir)
    examples = load_dataset_examples(dataset_manifest_path, split=split)
    dataset_manifest = read_json_object(dataset_manifest_path)
    split_counts = split_counts_from_manifest(dataset_manifest)
    rows: list[dict[str, Any]] = []
    modes = candidate_modes or ["rule", "mock_llm"]
    normalizers = build_normalizers(modes)
    validator = NormalizerValidator()

    for mode, normalizer in normalizers.items():
        for example in examples:
            transcript_text = str((example.get("input") or {}).get("transcript_text") or "")
            result = normalizer.normalize_with_provenance(transcript_text)
            decision = validator.validate(result.output)
            row = build_eval_row(
                example=example,
                candidate_mode=mode,
                candidate_output=result.output,
                schema_status=result.provenance.schema_status,
                fallback_reason=result.provenance.fallback_reason,
                validator_decision=decision.model_dump(mode="json"),
            )
            rows.append(row)

    for mode, path in (candidate_output_jsonl or {}).items():
        candidate_outputs = read_candidate_jsonl(path=Path(path), examples=examples)
        for example in examples:
            record = candidate_outputs[example["example_id"]]
            output_payload = record.get("output")
            candidate_output, schema_status, failure_reason = parse_candidate_output(output_payload)
            if candidate_output is None:
                row = build_schema_failure_row(
                    example=example,
                    candidate_mode=mode,
                    schema_failure_reason=failure_reason,
                )
            else:
                decision = validator.validate(candidate_output)
                row = build_eval_row(
                    example=example,
                    candidate_mode=mode,
                    candidate_output=candidate_output,
                    schema_status=schema_status,
                    fallback_reason=None,
                    validator_decision=decision.model_dump(mode="json"),
                )
            rows.append(row)

    rows = [sanitize_trace_dict(row) for row in rows]
    for row in rows:
        scan_payload_for_private_markers(row, path=Path("speech_to_task_eval_row"))
    metrics_by_mode = {
        mode: compute_metrics([row for row in rows if row["candidate_mode"] == mode])
        for mode in sorted({row["candidate_mode"] for row in rows})
    }
    manifest = {
        "manifest_version": "speech_to_task_adaptation_eval.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Voice-to-Browser Agent",
        "status": "available",
        "privacy_state": "local_private",
        "export_state": "local_private",
        "positioning": (
            "local adaptation-readiness evidence from a small sanitized seed set; "
            "not fine-tuning, checkpoint publication, ASR/TTS evaluation, public benchmark, "
            "SOTA, production readiness, or broad public-web autonomy evidence"
        ),
        "source_dataset_manifest_path": display_path(dataset_manifest_path),
        "split": split,
        "split_counts": split_counts,
        "candidate_modes": sorted(metrics_by_mode),
        "row_count": len(rows),
        "example_count": len(examples),
        "metrics_by_mode": metrics_by_mode,
        "failure_slices": build_failure_slices(rows),
        "privacy_scan": {"status": "passed"},
        "rows": rows,
    }
    summary = {
        "manifest_version": manifest["manifest_version"],
        "status": manifest["status"],
        "privacy_state": manifest["privacy_state"],
        "export_state": manifest["export_state"],
        "positioning": manifest["positioning"],
        "source_dataset_manifest_path": manifest["source_dataset_manifest_path"],
        "split": split,
        "split_counts": split_counts,
        "candidate_modes": manifest["candidate_modes"],
        "row_count": len(rows),
        "metrics_by_mode": metrics_by_mode,
        "failure_slices": manifest["failure_slices"],
        "privacy_scan": manifest["privacy_scan"],
    }
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2)
    summary_text = json.dumps(summary, ensure_ascii=False, indent=2)
    scan_text_for_private_markers(manifest_text, path=output_dir / "manifest.json")
    scan_text_for_private_markers(summary_text, path=output_dir / "summary.json")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "manifest.json").write_text(manifest_text, encoding="utf-8")
    (output_dir / "summary.json").write_text(summary_text, encoding="utf-8")
    return manifest


def load_dataset_examples(dataset_manifest_path: Path, split: str = DEFAULT_SPLIT) -> list[dict[str, Any]]:
    dataset_manifest_path = Path(dataset_manifest_path)
    manifest = read_json_object(dataset_manifest_path)
    split_meta = manifest.get("evaluation_splits")
    if not isinstance(split_meta, dict) or split_meta.get("status") != "available":
        raise SpeechToTaskEvalError("dataset manifest missing evaluation split metadata")
    examples_file = (manifest.get("files") or {}).get("examples_jsonl")
    if not isinstance(examples_file, str) or not examples_file:
        raise SpeechToTaskEvalError("dataset manifest missing examples_jsonl file")
    examples_path = dataset_manifest_path.parent / examples_file
    rows = read_jsonl_objects(examples_path)
    selected = [row for row in rows if row.get("split") == split]
    if not selected:
        raise SpeechToTaskEvalError(f"held-out split has no examples: {split}")
    for row in selected:
        scan_payload_for_private_markers(row, path=examples_path)
        if row.get("privacy_scan") != "passed":
            raise SpeechToTaskEvalError(f"example privacy scan did not pass: {row.get('example_id')}")
    return selected


def build_normalizers(modes: list[str]) -> dict[str, StructuredOutputNormalizer]:
    normalizers: dict[str, StructuredOutputNormalizer] = {}
    for mode in modes:
        if mode == "rule":
            normalizers[mode] = StructuredOutputNormalizer()
        elif mode == "mock_llm":
            normalizers[mode] = StructuredOutputNormalizer(
                llm_client=MockLLMNormalizerClient(),
                provider_mode="mock_llm",
            )
        else:
            raise SpeechToTaskEvalError(f"unsupported built-in candidate mode: {mode}")
    return normalizers


def read_candidate_jsonl(path: Path, examples: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    scan_text_for_private_markers(text, path=path)
    records: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SpeechToTaskEvalError(
                f"malformed candidate JSONL at {path}:{line_number}"
            ) from exc
        if not isinstance(record, dict):
            raise SpeechToTaskEvalError(f"malformed candidate row at {path}:{line_number}")
        scan_payload_for_private_markers(record, path=path)
        example_id = record.get("example_id")
        if not isinstance(example_id, str) or not example_id:
            raise SpeechToTaskEvalError(f"candidate row missing example_id at {path}:{line_number}")
        if example_id in records:
            raise SpeechToTaskEvalError(f"duplicate candidate id: {example_id}")
        records[example_id] = record
    expected_ids = {row["example_id"] for row in examples}
    actual_ids = set(records)
    missing = sorted(expected_ids - actual_ids)
    extra = sorted(actual_ids - expected_ids)
    if missing:
        raise SpeechToTaskEvalError("missing ids in candidate JSONL: " + ", ".join(missing))
    if extra:
        raise SpeechToTaskEvalError("extra ids in candidate JSONL: " + ", ".join(extra))
    return records


def build_eval_row(
    example: dict[str, Any],
    candidate_mode: str,
    candidate_output: BrowserTaskRequest | ClarificationRequest,
    schema_status: str,
    fallback_reason: str | None,
    validator_decision: dict[str, Any],
) -> dict[str, Any]:
    target = example["active_target_output"]
    candidate_payload = candidate_output.model_dump(mode="json")
    target_kind = target.get("kind")
    candidate_kind = candidate_payload.get("kind")
    target_intent = target.get("intent_type") if isinstance(target, dict) else None
    candidate_intent = candidate_payload.get("intent_type")
    target_category = safety_or_clarification_category(target)
    candidate_category = safety_or_clarification_category(candidate_payload, validator_decision)
    route_ready = route_readiness(candidate_kind, validator_decision)
    comparisons = {
        "output_kind_match": candidate_kind == target_kind,
        "intent_type_match": target_intent == candidate_intent if target_intent else None,
        "required_slot_match": required_slot_match(target, candidate_payload),
        "safety_or_clarification_decision_match": target_category == candidate_category,
    }
    return {
        "example_id": example["example_id"],
        "source_trace_id": example.get("source_execution_id")
        or (example.get("provenance") or {}).get("source_trace_id"),
        "source_trace_path": example.get("source_trace_path"),
        "split": example.get("split"),
        "evidence_mode": example.get("evidence_mode"),
        "provenance_kind": (example.get("provenance") or {}).get("kind"),
        "target_output_kind": target_kind,
        "candidate_mode": candidate_mode,
        "candidate_output_kind": candidate_kind,
        "target_intent_type": target_intent,
        "candidate_intent_type": candidate_intent,
        "schema_status": schema_status,
        "schema_valid": schema_status != "failed",
        "schema_failure_reason": None,
        "validator_outcome": validator_outcome(candidate_kind, bool(validator_decision.get("accepted"))),
        "validator_reason": validator_decision.get("reason"),
        "validator_issues": validator_decision.get("issues") or [],
        "route_readiness": route_ready,
        "route_ready": route_ready == "ready",
        "fallback": bool(fallback_reason),
        "fallback_reason": fallback_reason,
        "safety_or_clarification_category": candidate_category,
        "target_safety_or_clarification_category": target_category,
        "comparisons": comparisons,
        "privacy_scan": "passed",
    }


def build_schema_failure_row(
    example: dict[str, Any],
    candidate_mode: str,
    schema_failure_reason: str,
) -> dict[str, Any]:
    target = example["active_target_output"]
    return {
        "example_id": example["example_id"],
        "source_trace_id": example.get("source_execution_id")
        or (example.get("provenance") or {}).get("source_trace_id"),
        "source_trace_path": example.get("source_trace_path"),
        "split": example.get("split"),
        "evidence_mode": example.get("evidence_mode"),
        "provenance_kind": (example.get("provenance") or {}).get("kind"),
        "target_output_kind": target.get("kind"),
        "candidate_mode": candidate_mode,
        "candidate_output_kind": "malformed",
        "target_intent_type": target.get("intent_type"),
        "candidate_intent_type": None,
        "schema_status": "failed",
        "schema_valid": False,
        "schema_failure_reason": schema_failure_reason,
        "validator_outcome": "schema_failure",
        "validator_reason": schema_failure_reason,
        "validator_issues": ["schema_failure"],
        "route_readiness": "schema_failure",
        "route_ready": False,
        "fallback": False,
        "fallback_reason": None,
        "safety_or_clarification_category": "schema_failure",
        "target_safety_or_clarification_category": safety_or_clarification_category(target),
        "comparisons": {
            "output_kind_match": False,
            "intent_type_match": False if target.get("intent_type") else None,
            "required_slot_match": False,
            "safety_or_clarification_decision_match": False,
        },
        "privacy_scan": "passed",
    }


def parse_candidate_output(
    payload: Any,
) -> tuple[BrowserTaskRequest | ClarificationRequest | None, str, str | None]:
    try:
        if not isinstance(payload, dict):
            raise ValueError("expected object")
        kind = payload.get("kind")
        if kind == "browser_task_request":
            return BrowserTaskRequest.model_validate(payload), "passed", None
        if kind == "clarification_request":
            return ClarificationRequest.model_validate(payload), "passed", None
        raise ValueError(f"unknown kind {kind!r}")
    except Exception as exc:
        return None, "failed", str(exc)


def compute_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    row_count = len(rows)
    schema_valid = sum(1 for row in rows if row["schema_valid"])
    route_ready = sum(1 for row in rows if row["route_ready"])
    fallback = sum(1 for row in rows if row["fallback"])
    output_kind_matches = sum(
        1 for row in rows if row["comparisons"]["output_kind_match"] is True
    )
    intent_rows = [
        row for row in rows if row["comparisons"]["intent_type_match"] is not None
    ]
    intent_matches = sum(
        1 for row in intent_rows if row["comparisons"]["intent_type_match"] is True
    )
    slot_matches = sum(
        1 for row in rows if row["comparisons"]["required_slot_match"] is True
    )
    safety_matches = sum(
        1
        for row in rows
        if row["comparisons"]["safety_or_clarification_decision_match"] is True
    )
    return {
        "row_count": row_count,
        "schema_valid_count": schema_valid,
        "schema_valid_rate": rate(schema_valid, row_count),
        "output_kind_match_count": output_kind_matches,
        "output_kind_accuracy": rate(output_kind_matches, row_count),
        "intent_type_match_count": intent_matches,
        "intent_type_accuracy": rate(intent_matches, len(intent_rows)),
        "required_slot_match_count": slot_matches,
        "required_slot_match_rate": rate(slot_matches, row_count),
        "safety_or_clarification_decision_match_count": safety_matches,
        "safety_or_clarification_decision_accuracy": rate(safety_matches, row_count),
        "route_ready_count": route_ready,
        "route_ready_rate": rate(route_ready, row_count),
        "fallback_count": fallback,
        "fallback_rate": rate(fallback, row_count),
    }


def build_failure_slices(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, int]]]:
    slice_fields = {
        "candidate_mode": "candidate_mode",
        "split": "split",
        "evidence_mode": "evidence_mode",
        "target_output_kind": "target_output_kind",
        "intent_type": "target_intent_type",
        "schema_status": "schema_status",
        "safety_or_clarification_category": "safety_or_clarification_category",
    }
    slices: dict[str, dict[str, dict[str, int]]] = {}
    for slice_name, field in slice_fields.items():
        values: dict[str, dict[str, int]] = {}
        for row in rows:
            value = str(row.get(field) or "none")
            bucket = values.setdefault(value, {"row_count": 0, "failure_count": 0})
            bucket["row_count"] += 1
            if row_has_failure(row):
                bucket["failure_count"] += 1
        slices[slice_name] = dict(sorted(values.items()))
    return slices


def row_has_failure(row: dict[str, Any]) -> bool:
    if row["schema_status"] == "failed":
        return True
    comparisons = row.get("comparisons") or {}
    return any(value is False for value in comparisons.values())


def required_slot_match(target: dict[str, Any], candidate: dict[str, Any]) -> bool:
    target_slots = target.get("public_task_slots") if isinstance(target, dict) else {}
    if not isinstance(target_slots, dict) or not target_slots:
        return True
    candidate_slots = candidate.get("public_task_slots") if isinstance(candidate, dict) else {}
    if not isinstance(candidate_slots, dict):
        return False
    for key, value in target_slots.items():
        if candidate_slots.get(key) != value:
            return False
    return True


def safety_or_clarification_category(
    payload: dict[str, Any],
    validator_decision: dict[str, Any] | None = None,
) -> str:
    if payload.get("kind") == "clarification_request":
        return "clarification_required"
    if payload.get("kind") != "browser_task_request":
        return "schema_failure"
    if payload.get("requires_confirmation") or payload.get("safety_flags"):
        return "confirmation_required"
    if validator_decision and validator_decision.get("accepted") is False:
        return "blocked"
    return "route_ready"


def route_readiness(candidate_kind: str | None, validator_decision: dict[str, Any]) -> str:
    if candidate_kind == "clarification_request":
        return "clarification_required"
    if candidate_kind != "browser_task_request":
        return "schema_failure"
    if not validator_decision.get("accepted"):
        return "blocked"
    if validator_decision.get("requires_confirmation"):
        return "confirmation_required"
    return "ready"


def validator_outcome(output_kind: str | None, accepted: bool) -> str:
    if output_kind == "clarification_request":
        return "clarification"
    return "accepted" if accepted else "rejected"


def split_counts_from_manifest(manifest: dict[str, Any]) -> dict[str, int]:
    counts = (manifest.get("evaluation_splits") or {}).get("split_counts")
    if not isinstance(counts, dict):
        raise SpeechToTaskEvalError("dataset manifest missing split counts")
    return {str(key): int(value) for key, value in sorted(counts.items())}


def rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 6)


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SpeechToTaskEvalError(f"malformed JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise SpeechToTaskEvalError(f"malformed JSON object: {path}")
    scan_payload_for_private_markers(payload, path=path)
    return payload


def read_jsonl_objects(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    scan_text_for_private_markers(text, path=path)
    rows = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SpeechToTaskEvalError(f"malformed JSONL at {path}:{line_number}") from exc
        if not isinstance(payload, dict):
            raise SpeechToTaskEvalError(f"malformed JSONL object at {path}:{line_number}")
        rows.append(payload)
    return rows


def scan_payload_for_private_markers(value: Any, path: Path) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            scan_text_for_private_markers(str(key), path=path)
            scan_payload_for_private_markers(item, path=path)
    elif isinstance(value, list):
        for item in value:
            scan_payload_for_private_markers(item, path=path)
    elif isinstance(value, str):
        scan_text_for_private_markers(value, path=path)


def scan_text_for_private_markers(text: str, path: Path) -> None:
    lowered = text.lower()
    for marker in FORBIDDEN_MARKERS:
        if marker.lower() in lowered:
            raise SpeechToTaskEvalError(f"private marker '{marker}' found in {path}")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def parse_candidate_jsonl_args(values: list[str] | None) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for value in values or []:
        if "=" not in value:
            raise SpeechToTaskEvalError(
                "--candidate-output-jsonl must be formatted as mode=path.jsonl"
            )
        mode, raw_path = value.split("=", 1)
        if not mode or not raw_path:
            raise SpeechToTaskEvalError(
                "--candidate-output-jsonl must include non-empty mode and path"
            )
        if mode in parsed:
            raise SpeechToTaskEvalError(f"duplicate candidate mode: {mode}")
        parsed[mode] = Path(raw_path)
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local Speech-to-Task adaptation evaluation evidence."
    )
    parser.add_argument("--dataset-manifest", type=Path, default=DEFAULT_DATASET_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--split", default=DEFAULT_SPLIT, choices=("train", "dev", "test"))
    parser.add_argument(
        "--candidate-mode",
        action="append",
        choices=("rule", "mock_llm"),
        help="Built-in candidate mode to evaluate; repeatable. Defaults to rule and mock_llm.",
    )
    parser.add_argument(
        "--candidate-output-jsonl",
        action="append",
        default=[],
        help="External candidate outputs formatted as mode=path.jsonl.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = build_evaluation(
            dataset_manifest_path=args.dataset_manifest,
            output_dir=args.output_dir,
            split=args.split,
            candidate_modes=args.candidate_mode,
            candidate_output_jsonl=parse_candidate_jsonl_args(args.candidate_output_jsonl),
        )
    except SpeechToTaskEvalError as exc:
        print(f"error: {exc}")
        return 1
    print(f"wrote {args.output_dir}")
    print(f"split: {manifest['split']}")
    print(f"rows: {manifest['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
