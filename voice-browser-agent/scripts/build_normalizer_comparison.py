from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from voice_browser_agent.config import RuntimeConfig
from voice_browser_agent.normalizer import MockLLMNormalizerClient, StructuredOutputNormalizer
from voice_browser_agent.normalizer import normalizer_from_config
from voice_browser_agent.trace_writer import sanitize_trace_dict
from voice_browser_agent.validator import NormalizerValidator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACE_ROOT = PROJECT_ROOT / "fixtures/traces"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runtime/normalizer-comparison"
DEFAULT_SEED_SET_OVERLAY = PROJECT_ROOT / "fixtures/seed-set/reviewed-variants.json"
DEFAULT_MANIFEST_FILE = "manifest.json"
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
    "raw_prompt",
    "raw_provider_response",
    "provider_response",
    "request_header",
    "request_headers",
    "api_key",
    "authorization",
    "file:///Users/",
)
TRACE_DIR_BY_EVIDENCE_MODE = {
    "demo_preview": "sanitized",
    "live_controlled": "live-sanitized",
    "agentic_live_controlled": "agentic-sanitized",
    "real_vision_controlled": "real-vision-sanitized",
}


class NormalizerComparisonError(RuntimeError):
    pass


def build_comparison(
    project_root: Path = PROJECT_ROOT,
    trace_root: Path = DEFAULT_TRACE_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    seed_set: bool = False,
    include_real_provider: bool = False,
) -> dict[str, Any]:
    project_root = Path(project_root)
    trace_root = Path(trace_root)
    output_dir = Path(output_dir)
    inputs = collect_fixture_inputs(project_root)
    if seed_set:
        inputs.extend(collect_reviewed_variant_inputs(project_root=project_root, trace_root=trace_root))
    inputs = dedupe_inputs(inputs)

    rows: list[dict[str, Any]] = []
    mode_counts = {"rule": 0, "mock_llm": 0}
    schema_status_counts: dict[str, int] = {}
    validator_outcome_counts: dict[str, int] = {}
    fallback_counts = {"rule": 0, "mock_llm": 0}
    safety_outcome_counts: dict[str, int] = {}
    normalizers = {
        "rule": StructuredOutputNormalizer(),
        "mock_llm": StructuredOutputNormalizer(
            llm_client=MockLLMNormalizerClient(),
            provider_mode="mock_llm",
        ),
    }
    if include_real_provider:
        config = RuntimeConfig()
        if config.normalizer_provider not in {"openai_compatible", "generic_http"}:
            raise NormalizerComparisonError("real provider comparison requires an explicit real normalizer provider")
        if not config.normalizer_endpoint_url:
            raise NormalizerComparisonError("real provider comparison requires VOICE_BROWSER_NORMALIZER_ENDPOINT_URL")
        normalizers[config.normalizer_provider] = normalizer_from_config(config)
    validator = NormalizerValidator()

    for input_row in inputs:
        scan_payload_for_private_markers(input_row, path=Path(input_row["source_path"]))
        for mode, normalizer in normalizers.items():
            result = normalizer.normalize_with_provenance(input_row["transcript_text"])
            decision = validator.validate(result.output)
            validator_outcome = _validator_outcome(result.output.kind, decision.accepted)
            route_readiness = _route_readiness(result.output.kind, decision.accepted, decision.requires_confirmation)
            fallback_reason = result.provenance.fallback_reason
            row = {
                "input_id": input_row["input_id"],
                "input_source": input_row["input_source"],
                "source_trace_id": input_row.get("source_trace_id"),
                "source_path": input_row["source_path"],
                "variant_status": input_row.get("variant_status", "none"),
                "normalizer_mode": mode,
                "provider_name": result.provenance.provider_name,
                "output_source": result.provenance.output_source,
                "output_kind": result.provenance.output_kind,
                "schema_status": result.provenance.schema_status,
                "fallback_reason": fallback_reason,
                "validator_outcome": validator_outcome,
                "validator_reason": decision.reason,
                "route_readiness": route_readiness,
                "safety_flags": getattr(result.output, "safety_flags", []),
                "privacy_scan": "passed",
            }
            scan_payload_for_private_markers(row, path=Path(input_row["source_path"]))
            rows.append(row)
            mode_counts[mode] += 1
            schema_status_counts[row["schema_status"]] = schema_status_counts.get(row["schema_status"], 0) + 1
            validator_outcome_counts[validator_outcome] = (
                validator_outcome_counts.get(validator_outcome, 0) + 1
            )
            if fallback_reason:
                fallback_counts[mode] += 1
            safety_outcome_counts[route_readiness] = safety_outcome_counts.get(route_readiness, 0) + 1

    manifest = {
        "manifest_version": "normalizer_comparison.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Voice-to-Browser Agent",
        "status": "available",
        "privacy_state": "local_private",
        "export_state": "local_private",
        "positioning": "structured_output_comparison_not_model_training",
        "description": (
            "Local structured-output normalizer comparison evidence; "
            "no training, checkpoints, benchmark ranking, SOTA, production automation, or broad autonomy."
        ),
        "privacy_scan": {"status": "passed"},
        "normalizer_modes": list(normalizers),
        "input_count": len(inputs),
        "row_count": len(rows),
        "mode_counts": mode_counts,
        "schema_status_counts": dict(sorted(schema_status_counts.items())),
        "validator_outcome_counts": dict(sorted(validator_outcome_counts.items())),
        "fallback_counts": fallback_counts,
        "safety_outcome_counts": dict(sorted(safety_outcome_counts.items())),
        "rows": rows,
    }
    manifest = sanitize_trace_dict(manifest)
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2)
    scan_text_for_private_markers(manifest_text, path=output_dir / DEFAULT_MANIFEST_FILE)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / DEFAULT_MANIFEST_FILE).write_text(manifest_text, encoding="utf-8")
    return manifest


def collect_fixture_inputs(project_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    fixture_dir = project_root / "fixtures/audio"
    for fixture_path in sorted(fixture_dir.glob("*.fixture.json")):
        payload = read_json_object(fixture_path)
        transcript_text = str(payload.get("expected_transcript") or payload.get("spoken_text") or "")
        if not transcript_text:
            raise NormalizerComparisonError(f"fixture lacks transcript text: {fixture_path}")
        rows.append(
            {
                "input_id": f"fixture:{payload.get('audio_id') or fixture_path.stem}",
                "input_source": "fixture",
                "source_path": _display_path(project_root, fixture_path),
                "transcript_text": transcript_text,
                "variant_status": "none",
            }
        )
    return rows


def collect_reviewed_variant_inputs(project_root: Path, trace_root: Path) -> list[dict[str, Any]]:
    overlay_path = project_root / DEFAULT_SEED_SET_OVERLAY.relative_to(PROJECT_ROOT)
    if not overlay_path.exists():
        return []
    payload = read_json_object(overlay_path)
    variants = payload.get("variants")
    if not isinstance(variants, list):
        raise NormalizerComparisonError(f"malformed variant overlay: {overlay_path}")
    rows: list[dict[str, Any]] = []
    for record in variants:
        if not isinstance(record, dict):
            raise NormalizerComparisonError("malformed variant: expected object")
        example_id = record.get("example_id")
        variant_id = record.get("variant_id")
        if not example_id or not variant_id:
            raise NormalizerComparisonError("malformed variant: missing example_id or variant_id")
        evidence_mode, execution_id = str(example_id).split(":", 1)
        directory = TRACE_DIR_BY_EVIDENCE_MODE.get(evidence_mode)
        if directory is None:
            raise NormalizerComparisonError(f"unsupported variant evidence mode: {evidence_mode}")
        trace_path = trace_root / directory / f"{execution_id}.json"
        trace_payload = read_json_object(trace_path)
        transcript = trace_payload.get("transcript") or {}
        transcript_text = transcript.get("text") if isinstance(transcript, dict) else None
        if not transcript_text:
            raise NormalizerComparisonError(f"variant source lacks transcript text: {trace_path}")
        rows.append(
            {
                "input_id": f"reviewed_variant:{variant_id}",
                "input_source": "reviewed_variant",
                "source_trace_id": trace_payload.get("execution_id"),
                "source_path": _display_path(project_root, trace_path),
                "transcript_text": str(transcript_text),
                "variant_status": "reviewed",
            }
        )
    return rows


def dedupe_inputs(inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for row in inputs:
        input_id = row["input_id"]
        if input_id in seen:
            raise NormalizerComparisonError(f"duplicate comparison input id: {input_id}")
        seen.add(input_id)
        deduped.append(row)
    return deduped


def _validator_outcome(output_kind: str, accepted: bool) -> str:
    if output_kind == "clarification_request":
        return "clarification"
    return "accepted" if accepted else "rejected"


def _route_readiness(output_kind: str, accepted: bool, requires_confirmation: bool) -> str:
    if output_kind == "clarification_request":
        return "clarification_required"
    if not accepted:
        return "blocked"
    if requires_confirmation:
        return "confirmation_required"
    return "ready"


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise NormalizerComparisonError(f"malformed JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise NormalizerComparisonError(f"malformed JSON object: {path}")
    scan_payload_for_private_markers(payload, path=path)
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
            raise NormalizerComparisonError(f"private marker '{marker}' found in {path}")


def _display_path(project_root: Path, path: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build local normalizer comparison evidence.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--trace-root", type=Path, default=DEFAULT_TRACE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed-set", action="store_true")
    parser.add_argument("--include-real-provider", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = build_comparison(
            project_root=args.project_root,
            trace_root=args.trace_root,
            output_dir=args.output_dir,
            seed_set=args.seed_set,
            include_real_provider=args.include_real_provider,
        )
    except NormalizerComparisonError as exc:
        print(f"error: {exc}")
        return 1
    print(f"wrote {args.output_dir}")
    print(f"inputs: {manifest['input_count']}")
    print(f"rows: {manifest['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
