from __future__ import annotations

import argparse
import ipaddress
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runtime/reliability-snapshot"
TRACE_GROUPS = (
    ("sanitized", "demo_preview", "demo-*.json"),
    ("live-sanitized", "live_controlled", "live-*.json"),
    ("agentic-sanitized", "agentic_live_controlled", "agentic-*.json"),
    ("real-use-sanitized", "real_use_failure", "usage-*.json"),
    ("real-vision-sanitized", "real_vision_controlled", "real-vision-*.json"),
    ("real-voice-sanitized", "real_voice_controlled", "real-voice-*.json"),
)
VISUAL_OUTCOMES = ("passed", "failed", "uncertain")
RELIABILITY_OUTCOMES = ("completed", "partial", "stopped", "failed", "blocked")
FORBIDDEN_KEYS = {
    "raw_audio_path",
    "raw_screenshot",
    "browser_profile",
    "browser_profile_path",
    "profile_path",
    "storage_state",
    "storage_state_path",
    "cookie",
    "cookies",
    "credentials",
    "credential",
    "password",
    "token",
    "api_key",
    "authorization",
    "raw_prompt",
    "raw_provider_prompt",
    "raw_provider_payload",
    "raw_provider_response",
    "provider_private_payload",
    "provider_private_response",
    "local_file_uri",
    "private_url",
    "remote_host",
    "raw_public_page_text",
    "raw_page_text",
    "raw_page_html",
    "raw_visible_text",
    "unsanitized_runtime",
    "raw_runtime",
    "checkpoint_path",
}
FORBIDDEN_TEXT_MARKERS = (
    ("raw_audio_path", "raw_audio_path"),
    ("raw_audio_path", "recordings/private"),
    ("raw_screenshot", "raw_screenshot"),
    ("raw_screenshot", "screenshots/raw"),
    ("browser_profile", "browser_profile"),
    ("browser_profile", ".chromium-profile"),
    ("raw_prompt", "raw_prompt"),
    ("raw_provider_response", "raw_provider_response"),
    ("local_file_uri", "file://"),
    ("private_url", "http://127."),
    ("private_url", "http://localhost"),
    ("private_url", "http://10."),
    ("private_url", "http://192.168."),
    ("remote_host", "remote_host"),
    ("remote_host", "ssh://"),
    ("raw_public_page_text", "raw_public_page_text"),
    ("unsanitized_runtime", "unsanitized_runtime"),
    ("checkpoint_path", "checkpoint_path"),
    ("checkpoint_path", ".ckpt"),
    ("checkpoint_path", ".safetensors"),
    ("checkpoint_path", "checkpoints/"),
)
URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
LOCAL_PATH_MARKERS = ("/users/", "\\users\\")


class ReliabilitySnapshotError(RuntimeError):
    pass


def build_reliability_snapshot(
    project_root: Path = PROJECT_ROOT,
    output_dir: Path | None = None,
    normalizer_comparison_path: Path | None = None,
    adaptation_eval_path: Path | None = None,
    task_pack_run_root: Path | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root)
    output_dir = Path(output_dir) if output_dir else project_root / "runtime/reliability-snapshot"
    trace_root = project_root / "fixtures/traces"
    normalizer_comparison_path = (
        Path(normalizer_comparison_path)
        if normalizer_comparison_path
        else project_root / "runtime/normalizer-comparison/manifest.json"
    )
    adaptation_eval_path = (
        Path(adaptation_eval_path)
        if adaptation_eval_path
        else project_root / "runtime/speech-to-task-adaptation-eval/manifest.json"
    )
    task_pack_run_root = (
        Path(task_pack_run_root)
        if task_pack_run_root
        else project_root / "runtime/public-readonly-task-pack/runs"
    )

    manifest = {
        "manifest_version": "reliability_snapshot.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Voice-to-Browser Agent",
        "positioning": "generated local reliability summary, not committed raw evidence",
        "output": {
            "path": safe_display_path(output_dir / "manifest.json", project_root),
            "git_policy": "ignored_runtime_artifact",
        },
        "demo_trace_coverage": summarize_trace_coverage(trace_root, project_root),
        "visual_verification": summarize_visual_verification(trace_root, project_root),
        "public_readonly": {
            "smoke_matrix": summarize_public_readonly_matrix(
                project_root / "fixtures/public-readonly-smoke.json",
                project_root=project_root,
                evidence_key="reliability_attempt_evidence",
            ),
            "useful_task_pack": summarize_public_readonly_matrix(
                project_root / "fixtures/public-readonly-useful-task-pack.json",
                project_root=project_root,
                evidence_key="task_pack_attempt_evidence",
            ),
            "live_task_pack_runner": summarize_latest_task_pack_run(
                task_pack_run_root,
                project_root,
            ),
        },
        "normalizer_comparison": summarize_normalizer_comparison(
            normalizer_comparison_path,
            project_root,
        ),
        "speech_to_task_adaptation_eval": summarize_adaptation_eval(
            adaptation_eval_path,
            project_root,
        ),
        "validation_command_provenance": validation_command_provenance(),
        "privacy_scan": {"status": "passed"},
    }

    scan_payload_for_private_markers(manifest, path=output_dir / "manifest.json")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def summarize_trace_coverage(trace_root: Path, project_root: Path) -> dict[str, Any]:
    evidence_mode_counts: Counter[str] = Counter()
    final_status_counts: Counter[str] = Counter()
    source_trace_paths: list[str] = []

    for directory, evidence_mode, pattern in TRACE_GROUPS:
        for trace_path in sorted((trace_root / directory).glob(pattern)):
            payload = read_json(trace_path)
            scan_payload_for_private_markers(payload, path=trace_path)
            evidence_mode_counts[evidence_mode] += 1
            final_status = payload.get("final_status")
            if isinstance(final_status, str):
                final_status_counts[final_status] += 1
            source_trace_paths.append(safe_display_path(trace_path, project_root))

    return {
        "status": "available" if source_trace_paths else "unavailable",
        "total_trace_count": len(source_trace_paths),
        "evidence_mode_counts": dict(sorted(evidence_mode_counts.items())),
        "final_status_counts": dict(sorted(final_status_counts.items())),
        "source_trace_paths": source_trace_paths,
    }


def summarize_visual_verification(trace_root: Path, project_root: Path) -> dict[str, Any]:
    outcome_counts: Counter[str] = Counter({outcome: 0 for outcome in VISUAL_OUTCOMES})
    verified_fixture_ids: set[str] = set()
    source_trace_paths: list[str] = []
    recovery_count = 0
    failed_or_uncertain_reasons: list[dict[str, str]] = []

    for trace_path in sorted((trace_root / "agentic-sanitized").glob("agentic-*.json")):
        payload = read_json(trace_path)
        scan_payload_for_private_markers(payload, path=trace_path)
        fixture_id = fixture_id_for_payload(payload)
        source_trace_paths.append(safe_display_path(trace_path, project_root))
        for step in payload.get("agentic_steps") or []:
            if not isinstance(step, dict):
                continue
            recovery = step.get("recovery_decision") or {}
            if isinstance(recovery, dict) and recovery.get("kind") in {"reobserve", "clarify"}:
                recovery_count += 1
            verification = step.get("visual_verification_result")
            if not isinstance(verification, dict):
                continue
            scan_payload_for_private_markers(verification, path=trace_path)
            outcome = verification.get("outcome")
            if outcome in VISUAL_OUTCOMES:
                outcome_counts[outcome] += 1
                if outcome == "passed" and fixture_id:
                    verified_fixture_ids.add(fixture_id)
                if outcome in {"failed", "uncertain"}:
                    failed_or_uncertain_reasons.append(
                        {
                            "fixture_id": fixture_id or "unknown",
                            "outcome": outcome,
                            "reason": str(verification.get("reason") or ""),
                            "source_trace_path": safe_display_path(trace_path, project_root),
                        }
                    )

    status = "available" if source_trace_paths else "unavailable"
    return {
        "status": status,
        "outcome_counts": dict(outcome_counts),
        "verified_fixture_ids": sorted(verified_fixture_ids),
        "recovery_count": recovery_count,
        "failed_or_uncertain_reasons": failed_or_uncertain_reasons,
        "source_trace_paths": source_trace_paths,
        "privacy_scan": {"status": "passed"} if status == "available" else {"status": "unavailable"},
    }


def summarize_public_readonly_matrix(
    path: Path,
    project_root: Path,
    evidence_key: str,
) -> dict[str, Any]:
    payload = read_json(path)
    scan_payload_for_private_markers(payload, path=path)
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise ReliabilitySnapshotError(f"public-readonly task set missing tasks: {path}")

    outcome_counts: Counter[str] = Counter({outcome: 0 for outcome in RELIABILITY_OUTCOMES})
    privacy_counts: Counter[str] = Counter()
    export_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    for task in tasks:
        if not isinstance(task, dict):
            raise ReliabilitySnapshotError(f"malformed public-readonly task in {path}")
        evidence = task.get(evidence_key)
        if not isinstance(evidence, dict):
            raise ReliabilitySnapshotError(f"public-readonly task missing evidence: {path}")
        scan_payload_for_private_markers(evidence, path=path)
        outcome = evidence.get("outcome")
        if isinstance(outcome, str):
            outcome_counts[outcome] += 1
        privacy = evidence.get("evidence_privacy_state")
        if isinstance(privacy, str):
            privacy_counts[privacy] += 1
        export_state = evidence.get("export_state")
        if isinstance(export_state, str):
            export_counts[export_state] += 1
        category = task.get("task_category") or task.get("target_class")
        if isinstance(category, str):
            category_counts[category] += 1

    return {
        "status": "available",
        "task_count": len(tasks),
        "outcome_counts": dict(outcome_counts),
        "category_counts": dict(sorted(category_counts.items())),
        "privacy_state_counts": dict(sorted(privacy_counts.items())),
        "export_state_counts": dict(sorted(export_counts.items())),
        "source_manifest_path": safe_display_path(path, project_root),
        "privacy_scan": {"status": "passed"},
    }


def summarize_latest_task_pack_run(run_root: Path, project_root: Path) -> dict[str, Any]:
    if not run_root.exists():
        return unavailable(run_root, project_root)
    candidates = sorted(run_root.glob("*/manifest.json"))
    if not candidates:
        return unavailable(run_root, project_root)
    path = max(candidates, key=lambda item: (item.stat().st_mtime, item.as_posix()))
    payload = read_json(path)
    scan_payload_for_private_markers(payload, path=path)
    require_local_private(payload, path)
    return {
        "status": "available",
        "source_manifest_path": safe_display_path(path, project_root),
        "run_id": payload.get("run_id"),
        "runner_mode": payload.get("runner_mode"),
        "selected_task_count": payload.get("selected_task_count"),
        "outcome_counts": payload.get("outcome_counts") or {},
        "privacy_state": payload.get("privacy_state"),
        "sanitizer_status": payload.get("sanitizer_status"),
        "export_state": payload.get("export_state"),
        "live_network_attempted": bool(payload.get("live_network_attempted")),
        "privacy_scan": {"status": "passed"},
    }


def summarize_normalizer_comparison(path: Path, project_root: Path) -> dict[str, Any]:
    if not path.exists():
        return unavailable(path, project_root)
    payload = read_json(path)
    scan_payload_for_private_markers(payload, path=path)
    require_local_private(payload, path)
    if payload.get("manifest_version") != "normalizer_comparison.v1":
        raise ReliabilitySnapshotError(f"normalizer comparison manifest missing version: {path}")
    if payload.get("status") != "available":
        raise ReliabilitySnapshotError(f"normalizer comparison manifest unavailable: {path}")
    return {
        "status": "available",
        "source_manifest_path": safe_display_path(path, project_root),
        "input_count": payload.get("input_count"),
        "row_count": payload.get("row_count"),
        "normalizer_modes": payload.get("normalizer_modes") or [],
        "schema_status_counts": payload.get("schema_status_counts") or {},
        "validator_outcome_counts": payload.get("validator_outcome_counts") or {},
        "fallback_counts": payload.get("fallback_counts") or {},
        "privacy_scan": payload.get("privacy_scan") or {"status": "unknown"},
    }


def summarize_adaptation_eval(path: Path, project_root: Path) -> dict[str, Any]:
    if not path.exists():
        return unavailable(path, project_root)
    payload = read_json(path)
    scan_payload_for_private_markers(payload, path=path)
    require_local_private(payload, path)
    if payload.get("manifest_version") != "speech_to_task_adaptation_eval.v1":
        raise ReliabilitySnapshotError(f"adaptation eval manifest missing version: {path}")
    if payload.get("status") != "available":
        raise ReliabilitySnapshotError(f"adaptation eval manifest unavailable: {path}")
    return {
        "status": "available",
        "source_manifest_path": safe_display_path(path, project_root),
        "split": payload.get("split"),
        "split_counts": payload.get("split_counts") or {},
        "candidate_modes": payload.get("candidate_modes") or [],
        "row_count": payload.get("row_count"),
        "metrics_by_mode": payload.get("metrics_by_mode") or {},
        "failure_slices": payload.get("failure_slices") or {},
        "privacy_scan": payload.get("privacy_scan") or {"status": "unknown"},
    }


def validation_command_provenance() -> list[dict[str, str]]:
    return [
        {
            "command": "OPENSPEC_TELEMETRY=0 openspec validate --all --strict",
            "scope": "repo_root",
            "provenance": "ci_and_local_validation_command",
            "snapshot_claim": "documented_command_only",
        },
        {
            "command": "python -m pytest $CI_SAFE_PYTEST_TARGETS",
            "scope": "voice-browser-agent",
            "provenance": "ci_safe_reliability_workflow_command",
            "snapshot_claim": "documented_command_only",
        },
        {
            "command": "uv run pytest",
            "scope": "voice-browser-agent",
            "provenance": "local_full_validation_command",
            "snapshot_claim": "documented_command_only",
        },
    ]


def unavailable(path: Path, project_root: Path) -> dict[str, str]:
    return {
        "status": "unavailable",
        "reason": "manifest_absent",
        "source_manifest_path": safe_display_path(path, project_root),
    }


def require_local_private(payload: dict[str, Any], path: Path) -> None:
    privacy = payload.get("privacy_state")
    export = payload.get("export_state")
    if privacy is not None and privacy != "local_private":
        raise ReliabilitySnapshotError(f"manifest must remain local/private: {path}")
    if export is not None and export != "local_private":
        raise ReliabilitySnapshotError(f"manifest must remain local/private: {path}")
    privacy_scan = payload.get("privacy_scan")
    if isinstance(privacy_scan, dict) and privacy_scan.get("status") not in {None, "passed"}:
        raise ReliabilitySnapshotError(f"privacy scan did not pass: {path}")


def fixture_id_for_payload(payload: dict[str, Any]) -> str | None:
    transcript = payload.get("transcript") or {}
    if isinstance(transcript, dict):
        metadata = transcript.get("metadata") or {}
        if isinstance(metadata, dict) and metadata.get("input_audio_id"):
            return str(metadata["input_audio_id"])
    runtime = payload.get("execution_runtime") or {}
    if isinstance(runtime, dict) and runtime.get("controlled_fixture_id"):
        return str(runtime["controlled_fixture_id"])
    execution_id = payload.get("execution_id")
    return str(execution_id) if execution_id else None


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReliabilitySnapshotError(f"malformed JSON: {path}") from exc
    except OSError as exc:
        raise ReliabilitySnapshotError(f"cannot read JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ReliabilitySnapshotError(f"JSON payload is not an object: {path}")
    return payload


def scan_payload_for_private_markers(payload: Any, path: Path) -> None:
    _scan_node(payload, path=path)
    text = json.dumps(payload, ensure_ascii=False).lower()
    scan_text_for_private_values(text, path=path)


def scan_text_for_private_values(text: str, path: Path) -> None:
    lowered = text.lower()
    for marker, needle in FORBIDDEN_TEXT_MARKERS:
        if needle.lower() in lowered:
            raise ReliabilitySnapshotError(f"{marker} is not allowed in reliability snapshot input: {path}")
    if any(marker in lowered for marker in LOCAL_PATH_MARKERS):
        raise ReliabilitySnapshotError(f"local_path is not allowed in reliability snapshot input: {path}")
    for raw_url in URL_PATTERN.findall(text):
        url = raw_url.rstrip(".,);]")
        parsed = urlparse(url)
        host = parsed.hostname
        if host and is_private_host(host):
            raise ReliabilitySnapshotError(f"private_url is not allowed in reliability snapshot input: {path}")


def is_private_host(host: str) -> bool:
    if host.lower() in {"localhost", "localhost.localdomain"}:
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_link_local


def _scan_node(value: Any, path: Path) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if key_lower in FORBIDDEN_KEYS:
                raise ReliabilitySnapshotError(
                    f"{key_text} is not allowed in reliability snapshot input: {path}"
                )
            _scan_node(child, path=path)
    elif isinstance(value, list):
        for child in value:
            _scan_node(child, path=path)


def safe_display_path(value: Path | str, project_root: Path) -> str:
    path = Path(value)
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--normalizer-comparison-path", type=Path, default=None)
    parser.add_argument("--adaptation-eval-path", type=Path, default=None)
    parser.add_argument("--task-pack-run-root", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_reliability_snapshot(
        project_root=args.project_root,
        output_dir=args.output_dir,
        normalizer_comparison_path=args.normalizer_comparison_path,
        adaptation_eval_path=args.adaptation_eval_path,
        task_pack_run_root=args.task_pack_run_root,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
