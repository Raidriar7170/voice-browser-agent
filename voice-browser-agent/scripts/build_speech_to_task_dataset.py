from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from voice_browser_agent.models import ExecutionTrace
from voice_browser_agent.trace_writer import sanitize_trace_dict
from voice_browser_agent.training_examples import training_example_from_trace


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACE_ROOT = PROJECT_ROOT / "fixtures/traces"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runtime/speech-to-task-adaptation-dataset"
DEFAULT_SEED_SET_OVERLAY = PROJECT_ROOT / "fixtures/seed-set/reviewed-variants.json"
DEFAULT_EXAMPLES_FILE = "examples.jsonl"
FORBIDDEN_MARKERS = (
    "raw_audio_path",
    "raw_screenshot",
    "browser_profile",
    "browser_profile_path",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "password",
    "token",
    "secret",
    "private_url",
    "remote_host",
    "remote_vision_backend_url",
    "controlled_target_url",
    "file:///Users/",
)
TRACE_GROUPS = (
    ("sanitized", "demo_preview", "demo-*.json"),
    ("live-sanitized", "live_controlled", "live-*.json"),
    ("agentic-sanitized", "agentic_live_controlled", "agentic-*.json"),
    ("real-vision-sanitized", "real_vision_controlled", "real-vision-*.json"),
)


class DatasetBuildError(RuntimeError):
    pass


def build_dataset(
    project_root: Path = PROJECT_ROOT,
    trace_root: Path = DEFAULT_TRACE_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    release_pack_manifest: Path | None = None,
    correction_overlay: Path | None = None,
    seed_set: bool = False,
) -> dict[str, Any]:
    project_root = Path(project_root)
    trace_root = Path(trace_root)
    output_dir = Path(output_dir)

    trace_examples = collect_trace_examples(project_root=project_root, trace_root=trace_root)
    if seed_set and correction_overlay is None:
        correction_overlay = project_root / DEFAULT_SEED_SET_OVERLAY.relative_to(PROJECT_ROOT)
    corrections = resolve_corrections(
        correction_overlay=correction_overlay,
        trace_examples=trace_examples,
    )
    release_pack_context = read_release_pack_manifest(release_pack_manifest)

    examples: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    evidence_mode_counts: dict[str, int] = {}
    for trace_example in trace_examples:
        correction = corrections.get(trace_example["example_id"])
        row = build_jsonl_example(trace_example, correction)
        examples.append(row)
        evidence_mode_counts[trace_example["evidence_mode"]] = (
            evidence_mode_counts.get(trace_example["evidence_mode"], 0) + 1
        )
        manifest_rows.append(
            {
                "example_id": trace_example["example_id"],
                "source_execution_id": trace_example["source_execution_id"],
                "source_trace_path": trace_example["source_trace_path"],
                "evidence_mode": trace_example["evidence_mode"],
                "final_status": trace_example["training_example"].final_status,
                "validator_outcome": validator_outcome(trace_example["training_example"]),
                "safety_flags": trace_example["training_example"].safety_flags,
                "privacy_scan": "passed",
                "correction_status": row["correction"]["status"],
                "provenance": row["provenance"],
            }
        )

    variant_count = 0
    if seed_set:
        variants = resolve_variants(
            correction_overlay=correction_overlay,
            trace_examples=trace_examples,
        )
        for variant in variants:
            row = build_variant_example(variant)
            examples.append(row)
            variant_count += 1
            evidence_mode_counts[variant["evidence_mode"]] = (
                evidence_mode_counts.get(variant["evidence_mode"], 0) + 1
            )
            manifest_rows.append(
                {
                    "example_id": row["example_id"],
                    "source_execution_id": variant["source_execution_id"],
                    "source_trace_path": variant["source_trace_path"],
                    "evidence_mode": variant["evidence_mode"],
                    "final_status": variant["training_example"].final_status,
                    "validator_outcome": validator_outcome(variant["training_example"]),
                    "safety_flags": variant["training_example"].safety_flags,
                    "privacy_scan": "passed",
                    "correction_status": row["correction"]["status"],
                    "provenance": row["provenance"],
                }
            )

        if not 20 <= len(examples) <= 50:
            raise DatasetBuildError(
                f"seed set example count must be between 20 and 50, got {len(examples)}"
            )

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    examples_path = output_dir / DEFAULT_EXAMPLES_FILE
    examples_text = "\n".join(json.dumps(row, ensure_ascii=False) for row in examples) + "\n"
    scan_text_for_private_markers(examples_text, path=examples_path)
    examples_path.write_text(examples_text, encoding="utf-8")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Voice-to-Browser Agent",
        "description": "Local Speech-to-Task adaptation dataset from sanitized execution traces.",
        "source_trace_dirs": [f"fixtures/traces/{directory}" for directory, _, _ in TRACE_GROUPS],
        "privacy_scan": {"status": "passed"},
        "example_count": len(examples),
        "evidence_mode_counts": dict(sorted(evidence_mode_counts.items())),
        "correction_count": len(corrections),
        "files": {"examples_jsonl": DEFAULT_EXAMPLES_FILE},
        "examples": manifest_rows,
    }
    if seed_set:
        manifest["seed_set"] = {
            "status": "adaptation_preparation",
            "trace_derived_count": len(trace_examples),
            "reviewed_variant_count": variant_count,
            "positioning": (
                "small local Speech-to-Task adaptation preparation evidence; "
                "no training, checkpoints, ASR/TTS evaluation, or broad public-web automation"
            ),
        }
    if release_pack_context is not None:
        manifest.update(release_pack_context)

    manifest_path = output_dir / "manifest.json"
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2)
    scan_text_for_private_markers(manifest_text, path=manifest_path)
    manifest_path.write_text(manifest_text, encoding="utf-8")
    return manifest


def collect_trace_examples(project_root: Path, trace_root: Path) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for directory, evidence_mode, pattern in TRACE_GROUPS:
        group_dir = trace_root / directory
        for trace_path in sorted(group_dir.glob(pattern)):
            payload = read_json_object(trace_path)
            scan_payload_for_private_markers(payload, path=trace_path)
            source_path = f"fixtures/traces/{directory}/{trace_path.name}"
            execution_id = str(payload.get("execution_id") or trace_path.stem)
            example_id = f"{evidence_mode}:{execution_id}"
            if example_id in seen_ids:
                raise DatasetBuildError(f"duplicate example id {example_id}: {source_path}")
            seen_ids.add(example_id)
            trace = validate_trace(payload=payload, source_path=source_path)
            try:
                training_example = training_example_from_trace(trace)
            except ValueError as exc:
                raise DatasetBuildError(
                    f"trace lacks transcript or normalized output: {source_path}"
                ) from exc
            examples.append(
                {
                    "example_id": example_id,
                    "source_execution_id": trace.execution_id,
                    "source_trace_path": source_path,
                    "evidence_mode": evidence_mode,
                    "trace": trace,
                    "training_example": training_example,
                }
            )
    return examples


def validate_trace(payload: dict[str, Any], source_path: str) -> ExecutionTrace:
    try:
        trace = ExecutionTrace.model_validate(payload)
    except Exception as exc:
        raise DatasetBuildError(f"malformed trace: {source_path}") from exc
    if trace.transcript is None:
        raise DatasetBuildError(f"trace lacks transcript: {source_path}")
    if trace.normalized_output is None:
        raise DatasetBuildError(f"trace lacks normalized output: {source_path}")
    return trace


def read_release_pack_manifest(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    scan_text_for_private_markers(text, path=path)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DatasetBuildError(f"malformed release-pack manifest: {path}") from exc
    artifacts = payload.get("artifacts", []) if isinstance(payload, dict) else []
    if not isinstance(artifacts, list):
        raise DatasetBuildError(f"malformed release-pack manifest artifacts: {path}")
    return {
        "release_pack_manifest_path": str(path),
        "release_pack_artifact_count": len(artifacts),
    }


def resolve_corrections(
    correction_overlay: Path | None,
    trace_examples: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    if correction_overlay is None:
        return {}

    records = read_correction_records(Path(correction_overlay))
    by_example_id = {item["example_id"]: item for item in trace_examples}
    by_execution_id = {item["source_execution_id"]: item for item in trace_examples}
    resolved: dict[str, dict[str, Any]] = {}
    for record in records:
        example_id = record.get("example_id")
        source_execution_id = record.get("source_execution_id")
        if example_id:
            target = by_example_id.get(example_id)
            unknown = example_id
        elif source_execution_id:
            target = by_execution_id.get(source_execution_id)
            unknown = source_execution_id
        else:
            raise DatasetBuildError(
                "malformed correction missing example_id or source_execution_id"
            )
        if target is None:
            raise DatasetBuildError(f"unknown correction target: {unknown}")
        resolved_id = target["example_id"]
        if resolved_id in resolved:
            raise DatasetBuildError(f"duplicate correction for example id {resolved_id}")
        corrected_target = record["target_output"]
        scan_payload_for_private_markers(corrected_target, path=Path(correction_overlay))
        resolved[resolved_id] = {
            "target_output": sanitize_trace_dict(corrected_target),
            "reason": record.get("reason"),
            "note": record.get("note"),
        }
    return resolved


def resolve_variants(
    correction_overlay: Path | None,
    trace_examples: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if correction_overlay is None:
        raise DatasetBuildError("seed set requires a reviewed variant overlay")

    records = read_variant_records(Path(correction_overlay))
    by_example_id = {item["example_id"]: item for item in trace_examples}
    variants: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for record in records:
        source_id = record.get("example_id")
        source = by_example_id.get(source_id)
        if source is None:
            raise DatasetBuildError(f"unknown variant target: {source_id}")
        variant_id = record.get("variant_id")
        if not variant_id:
            raise DatasetBuildError(f"malformed variant for {source_id}: missing variant_id")
        example_id = f"reviewed_variant:{variant_id}"
        if example_id in seen_ids:
            raise DatasetBuildError(f"duplicate reviewed variant id {example_id}")
        seen_ids.add(example_id)
        target_output = record.get("target_output")
        if not isinstance(target_output, dict):
            raise DatasetBuildError(f"malformed variant {variant_id}: missing target_output")
        scan_payload_for_private_markers(target_output, path=Path(correction_overlay))
        variants.append(
            {
                **source,
                "example_id": example_id,
                "source_example_id": source["example_id"],
                "target_output": sanitize_trace_dict(target_output),
                "reason": record.get("reason"),
                "note": record.get("note"),
            }
        )
    return variants


def read_correction_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    scan_text_for_private_markers(text, path=path)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DatasetBuildError(f"malformed correction overlay: {path}") from exc
    records = payload.get("corrections") if isinstance(payload, dict) else None
    if records is None and isinstance(payload, dict) and "variants" in payload:
        return []
    if not isinstance(records, list):
        raise DatasetBuildError(f"malformed correction overlay: {path}")
    validated: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise DatasetBuildError(f"malformed correction #{index}: expected object")
        target_output = record.get("target_output")
        if not isinstance(target_output, dict):
            raise DatasetBuildError(f"malformed correction #{index}: missing target_output")
        if "example_id" not in record and "source_execution_id" not in record:
            raise DatasetBuildError(f"malformed correction #{index}: missing target id")
        validated.append(record)
    return validated


def read_variant_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    scan_text_for_private_markers(text, path=path)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DatasetBuildError(f"malformed variant overlay: {path}") from exc
    records = payload.get("variants") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise DatasetBuildError(f"malformed variant overlay: {path}")
    validated: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise DatasetBuildError(f"malformed variant #{index}: expected object")
        if "example_id" not in record:
            raise DatasetBuildError(f"malformed variant #{index}: missing example_id")
        if not isinstance(record.get("target_output"), dict):
            raise DatasetBuildError(f"malformed variant #{index}: missing target_output")
        validated.append(record)
    return validated


def build_jsonl_example(
    trace_example: dict[str, Any],
    correction: dict[str, Any] | None,
) -> dict[str, Any]:
    training_example = trace_example["training_example"]
    original_target = sanitize_trace_dict(training_example.target_output)
    active_target = original_target
    corrected_target = None
    correction_payload = {"status": "absent"}
    if correction is not None:
        corrected_target = correction["target_output"]
        active_target = corrected_target
        correction_payload = {
            "status": "applied",
            "reason": correction.get("reason"),
            "note": correction.get("note"),
        }
    transcript_metadata = sanitize_trace_dict(training_example.input.get("transcript_metadata", {}))
    return {
        "example_id": trace_example["example_id"],
        "source_execution_id": trace_example["source_execution_id"],
        "source_trace_path": trace_example["source_trace_path"],
        "evidence_mode": trace_example["evidence_mode"],
        "provenance": {
            "kind": "trace_derived",
            "source_trace_id": trace_example["source_execution_id"],
            "source_trace_path": trace_example["source_trace_path"],
            "evidence_mode": trace_example["evidence_mode"],
            "privacy_scan": "passed",
        },
        "input": sanitize_trace_dict(training_example.input),
        "language_metadata": {
            "adapter_name": transcript_metadata.get("adapter_name"),
            "input_audio_id": transcript_metadata.get("input_audio_id"),
            "language_mode": transcript_metadata.get("language_mode"),
            "confidence": transcript_metadata.get("confidence"),
        },
        "original_target_output": original_target,
        "active_target_output": active_target,
        "corrected_target_output": corrected_target,
        "validator_decision": sanitize_trace_dict(training_example.validator_decision),
        "final_status": training_example.final_status,
        "safety_flags": training_example.safety_flags,
        "correction": correction_payload,
        "privacy_scan": "passed",
    }


def build_variant_example(variant: dict[str, Any]) -> dict[str, Any]:
    training_example = variant["training_example"]
    original_target = sanitize_trace_dict(training_example.target_output)
    active_target = sanitize_trace_dict(variant["target_output"])
    transcript_metadata = sanitize_trace_dict(training_example.input.get("transcript_metadata", {}))
    return {
        "example_id": variant["example_id"],
        "source_execution_id": variant["source_execution_id"],
        "source_trace_path": variant["source_trace_path"],
        "evidence_mode": variant["evidence_mode"],
        "provenance": {
            "kind": "reviewed_variant",
            "source_example_id": variant["source_example_id"],
            "source_trace_id": variant["source_execution_id"],
            "source_trace_path": variant["source_trace_path"],
            "evidence_mode": variant["evidence_mode"],
            "overlay_status": "reviewed",
            "privacy_scan": "passed",
        },
        "input": sanitize_trace_dict(training_example.input),
        "language_metadata": {
            "adapter_name": transcript_metadata.get("adapter_name"),
            "input_audio_id": transcript_metadata.get("input_audio_id"),
            "language_mode": transcript_metadata.get("language_mode"),
            "confidence": transcript_metadata.get("confidence"),
        },
        "original_target_output": original_target,
        "active_target_output": active_target,
        "corrected_target_output": active_target,
        "validator_decision": sanitize_trace_dict(training_example.validator_decision),
        "final_status": training_example.final_status,
        "safety_flags": training_example.safety_flags,
        "correction": {
            "status": "reviewed_variant",
            "reason": variant.get("reason"),
            "note": variant.get("note"),
        },
        "privacy_scan": "passed",
    }


def validator_outcome(training_example: Any) -> str:
    decision = training_example.validator_decision
    if not isinstance(decision, dict):
        return "absent"
    if decision.get("accepted") is True:
        return "accepted"
    if decision.get("accepted") is False:
        return "rejected"
    return "absent"


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DatasetBuildError(f"malformed trace JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise DatasetBuildError(f"malformed trace is not an object: {path}")
    return payload


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
            raise DatasetBuildError(f"private marker '{marker}' found in {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Voice-to-Browser Speech-to-Task adaptation dataset."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--trace-root", type=Path, default=DEFAULT_TRACE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--release-pack-manifest", type=Path, default=None)
    parser.add_argument("--correction-overlay", type=Path, default=None)
    parser.add_argument("--seed-set", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = build_dataset(
            project_root=args.project_root,
            trace_root=args.trace_root,
            output_dir=args.output_dir,
            release_pack_manifest=args.release_pack_manifest,
            correction_overlay=args.correction_overlay,
            seed_set=args.seed_set,
        )
    except DatasetBuildError as exc:
        print(f"error: {exc}")
        return 1
    print(f"wrote {args.output_dir}")
    print(f"examples: {manifest['example_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
