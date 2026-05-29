from __future__ import annotations

import argparse
import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from voice_browser_agent.demo_tasks import selected_live_fixture_ids
from voice_browser_agent.public_readonly import (
    ReliabilityMatrixError,
    build_public_readonly_reliability_row,
    build_public_readonly_useful_task_pack_summary,
    load_public_readonly_smoke_set,
    read_latest_public_readonly_task_pack_run,
    summarize_reliability_matrix,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACE_ROOT = PROJECT_ROOT / "fixtures/traces"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runtime/demo-evidence-release-pack"
DEFAULT_NORMALIZER_COMPARISON_PATH = PROJECT_ROOT / "runtime/normalizer-comparison/manifest.json"
FORBIDDEN_MARKERS = (
    "raw_page_text",
    "raw_page_html",
    "raw_visible_text",
    "visible_text",
    "unsanitized_runtime",
    "raw_runtime",
    "local_file_uri",
    "raw_audio_path",
    "raw_screenshot",
    "browser_profile",
    "browser_profile_path",
    "profile_path",
    "storage_state",
    "storage_state_path",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "password",
    "token",
    "private_url",
    "raw_prompt",
    "raw_provider_response",
    "provider_response",
    "request_header",
    "request_headers",
    "api_key",
    "authorization",
    "remote_host",
    "remote_vision_backend_url",
    "controlled_target_url",
    "file:///Users/",
    "file:///users/",
    "/Users/",
    "/users/",
)
TRACE_GROUPS = (
    ("sanitized", "demo_preview", "demo-*.json"),
    ("live-sanitized", "live_controlled", "live-*.json"),
    ("agentic-sanitized", "agentic_live_controlled", "agentic-*.json"),
    ("real-vision-sanitized", "real_vision_controlled", "real-vision-*.json"),
    ("real-voice-sanitized", "real_voice_controlled", "real-voice-*.json"),
    ("real-use-sanitized", "real_use_failure", "usage-*.json"),
)


class EvidencePackError(RuntimeError):
    pass


def build_release_pack(
    project_root: Path = PROJECT_ROOT,
    trace_root: Path = DEFAULT_TRACE_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    task_pack_run_root: Path | None = None,
    normalizer_comparison_path: Path | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root)
    trace_root = Path(trace_root)
    output_dir = Path(output_dir)
    artifacts = collect_artifacts(project_root=project_root, trace_root=trace_root)
    local_private_exclusions = collect_local_private_exclusions(trace_root=trace_root)
    check_completeness(project_root=project_root, artifacts=artifacts)
    reliability_matrix = build_public_readonly_reliability_matrix(project_root)
    useful_task_pack = build_public_readonly_useful_task_pack_summary(
        project_root / "fixtures/public-readonly-useful-task-pack.json"
    )
    scan_payload_for_private_markers(useful_task_pack, path=project_root / "fixtures/public-readonly-useful-task-pack.json")
    live_task_pack_runner = build_public_readonly_live_task_pack_runner_summary(
        task_pack_run_root
        or project_root / "runtime/public-readonly-task-pack/runs"
    )
    normalizer_comparison = build_normalizer_comparison_summary(normalizer_comparison_path)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir / "traces").mkdir(parents=True, exist_ok=True)

    for artifact in artifacts:
        target = output_dir / artifact["packaged_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact["_source_abs"], target)
        del artifact["_source_abs"]

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Voice-to-Browser Agent",
        "description": "Bounded demo evidence pack for reproducible reviewer handoff.",
        "privacy_scan": {"status": "passed"},
        "artifacts": artifacts,
        "local_private_exclusions": local_private_exclusions,
        "public_readonly_reliability_matrix": reliability_matrix,
        "public_readonly_useful_task_pack": useful_task_pack,
        "public_readonly_live_task_pack_runner": live_task_pack_runner,
        "normalizer_comparison": normalizer_comparison,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    html_path = output_dir / "index.html"
    html_path.write_text(render_html(manifest), encoding="utf-8")
    scan_text_for_private_markers(html_path.read_text(encoding="utf-8"), path=html_path)
    scan_text_for_private_markers(manifest_path.read_text(encoding="utf-8"), path=manifest_path)
    return manifest


def build_public_readonly_reliability_matrix(project_root: Path) -> dict[str, Any]:
    smoke_path = project_root / "fixtures/public-readonly-smoke.json"
    try:
        smoke_set = load_public_readonly_smoke_set(smoke_path)
        rows = []
        for task in smoke_set.tasks:
            evidence = task.reliability_attempt_evidence
            scan_payload_for_private_markers(evidence.model_dump(mode="json"), path=smoke_path)
            rows.append(
                build_public_readonly_reliability_row(
                    task_id=task.task_id,
                    target_label=task.target_label,
                    target_class=task.target_class,
                    task_kind=task.task_kind,
                    completion_criteria_id=task.completion_criteria.criteria_id,
                    completion_criteria_summary=task.completion_criteria.required_proof,
                    outcome=evidence.outcome,
                    final_status=evidence.final_status,
                    observed_proof_summary=evidence.observed_proof_summary,
                    unmet_criteria=evidence.unmet_criteria,
                    stop_or_failure_reason=evidence.stop_or_failure_reason,
                    evidence_privacy_state=evidence.evidence_privacy_state,
                    sanitizer_status=evidence.sanitizer_status,
                    visible_result_state=evidence.visible_result_state,
                    export_state=evidence.export_state,
                    regression_coverage=evidence.regression_coverage
                    or task.regression_coverage
                    or [f"{evidence.outcome.value}_coverage"],
                )
            )
        return summarize_reliability_matrix(rows).model_dump(mode="json")
    except ReliabilityMatrixError as exc:
        raise EvidencePackError(str(exc)) from exc


def build_public_readonly_live_task_pack_runner_summary(run_root: Path) -> dict[str, Any]:
    try:
        summary = read_latest_public_readonly_task_pack_run(run_root)
    except ReliabilityMatrixError as exc:
        raise EvidencePackError(str(exc)) from exc
    scan_payload_for_private_markers(summary, path=Path(run_root) / "manifest.json")
    return summary


def build_normalizer_comparison_summary(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"status": "not_provided"}
    path = Path(path)
    if not path.exists():
        return {"status": "missing", "manifest_path": str(path)}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvidencePackError(f"malformed normalizer comparison manifest: {path}") from exc
    if not isinstance(payload, dict):
        raise EvidencePackError(f"malformed normalizer comparison manifest: {path}")
    scan_payload_for_private_markers(payload, path=path)
    if payload.get("manifest_version") != "normalizer_comparison.v1":
        raise EvidencePackError(f"normalizer comparison manifest missing version: {path}")
    if payload.get("status") != "available":
        raise EvidencePackError(f"normalizer comparison manifest unavailable: {path}")
    if payload.get("privacy_state") != "local_private" or payload.get("export_state") != "local_private":
        raise EvidencePackError(f"normalizer comparison manifest must remain local/private: {path}")
    if not isinstance(payload.get("normalizer_modes"), list):
        raise EvidencePackError(f"normalizer comparison manifest missing modes: {path}")
    if not isinstance(payload.get("schema_status_counts"), dict):
        raise EvidencePackError(f"normalizer comparison manifest missing schema counts: {path}")
    if not isinstance(payload.get("validator_outcome_counts"), dict):
        raise EvidencePackError(f"normalizer comparison manifest missing validator counts: {path}")
    if (payload.get("privacy_scan") or {}).get("status") != "passed":
        raise EvidencePackError(f"normalizer comparison privacy scan did not pass: {path}")
    return {
        "status": "available",
        "manifest_version": payload["manifest_version"],
        "privacy_state": payload["privacy_state"],
        "export_state": payload["export_state"],
        "positioning": payload.get("positioning"),
        "input_count": payload.get("input_count"),
        "row_count": payload.get("row_count"),
        "normalizer_modes": payload["normalizer_modes"],
        "schema_status_counts": payload["schema_status_counts"],
        "validator_outcome_counts": payload["validator_outcome_counts"],
        "fallback_counts": payload.get("fallback_counts") or {},
        "safety_outcome_counts": payload.get("safety_outcome_counts") or {},
        "privacy_scan": payload["privacy_scan"],
    }


def collect_local_private_exclusions(trace_root: Path) -> list[dict[str, Any]]:
    exclusions: list[dict[str, Any]] = []
    for trace_path in sorted(trace_root.rglob("*.json")):
        payload = read_trace(trace_path)
        runtime = payload.get("execution_runtime") or {}
        route = payload.get("route_decision") or runtime.get("route_decision") or {}
        evidence_mode = (
            payload.get("evidence_mode")
            or runtime.get("evidence_mode")
            or route.get("evidence_mode")
            or payload.get("execution_mode")
        )
        route_type = route.get("route_type")
        if evidence_mode != "live_public_readonly" and route_type != "public_readonly":
            continue
        sanitizer_status = payload.get("sanitizer_status") or route.get("sanitizer_status")
        privacy_state = payload.get("evidence_privacy_state") or route.get("evidence_privacy_state")
        if privacy_state == "public_safe" and sanitizer_status == "passed":
            continue
        exclusions.append(
            {
                "execution_id": payload.get("execution_id"),
                "evidence_mode": "live_public_readonly",
                "reason": "public_readonly_trace_not_public_safe",
                "sanitizer_status": sanitizer_status or "unknown",
                "target_label": route.get("public_target_label"),
                "public_origin": route.get("public_origin"),
                "public_task_id": route.get("public_task_id") or runtime.get("public_task_id"),
                "public_task_kind": route.get("public_task_kind")
                or runtime.get("public_task_kind"),
                "completion_state": runtime.get("public_completion_state")
                or route.get("public_completion_state"),
            }
        )
    return exclusions


def collect_artifacts(project_root: Path, trace_root: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for directory, evidence_mode, pattern in TRACE_GROUPS:
        group_dir = trace_root / directory
        for trace_path in sorted(group_dir.glob(pattern)):
            payload = read_trace(trace_path)
            scan_payload_for_private_markers(payload, path=trace_path)
            runtime = payload.get("execution_runtime") or {}
            fixture_id = fixture_id_for_payload(
                payload=payload,
                runtime=runtime,
                evidence_mode=evidence_mode,
                trace_path=trace_path,
            )
            if not fixture_id:
                raise EvidencePackError(f"malformed trace missing fixture id: {trace_path}")
            agentic_steps = payload.get("agentic_steps") or []
            grounding_refs = payload.get("grounding_evidence_refs") or []
            route = payload.get("route_decision") or runtime.get("route_decision") or {}
            artifact = {
                "fixture_id": fixture_id,
                "execution_id": payload.get("execution_id"),
                "evidence_mode": evidence_mode,
                "execution_mode": payload.get("execution_mode") or "demo_preview",
                "source_path": f"fixtures/traces/{directory}/{trace_path.name}",
                "packaged_path": f"traces/{evidence_mode}/{trace_path.name}",
                "final_status": payload.get("final_status"),
                "stop_reason": payload.get("stop_reason"),
                "failure_reason": payload.get("failure_reason"),
                "grounding_evidence_refs": grounding_refs,
                "agentic_step_count": len(agentic_steps),
                "provider": runtime.get("provider"),
                "adapter": runtime.get("adapter"),
                "asr": runtime.get("asr"),
                "transcript_review": runtime.get("transcript_review"),
                "input_source": runtime.get("input_source"),
                "privacy_scan": (runtime.get("privacy_scan") or {}).get("status", "passed"),
                "route_type": route.get("route_type"),
                "route_evidence_mode": route.get("evidence_mode"),
                "live_evidence_eligible": route.get("live_evidence_eligible"),
                "_source_abs": trace_path,
            }
            validate_artifact(artifact, trace_path)
            artifacts.append(artifact)
    return artifacts


def fixture_id_for_payload(
    payload: dict[str, Any],
    runtime: dict[str, Any],
    evidence_mode: str,
    trace_path: Path,
) -> str | None:
    if evidence_mode == "real_use_failure":
        return payload.get("execution_id")
    if evidence_mode == "real_voice_controlled":
        return runtime.get("controlled_fixture_id")
    transcript = payload.get("transcript") or {}
    if not isinstance(transcript, dict):
        raise EvidencePackError(f"malformed trace transcript in {trace_path}")
    metadata = transcript.get("metadata") or {}
    return metadata.get("input_audio_id")


def read_trace(trace_path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(trace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvidencePackError(f"malformed trace JSON: {trace_path}") from exc
    if not isinstance(payload, dict):
        raise EvidencePackError(f"malformed trace is not an object: {trace_path}")
    return payload


def validate_artifact(artifact: dict[str, Any], trace_path: Path) -> None:
    if artifact["final_status"] not in {
        "succeeded",
        "failed",
        "stopped",
        "cancelled",
        "pending_confirmation",
        "clarification_required",
        "blocked",
    }:
        raise EvidencePackError(f"malformed trace final status in {trace_path}")
    if artifact["evidence_mode"] == "demo_preview" and not artifact["source_path"].endswith(".json"):
        raise EvidencePackError(f"malformed preview artifact path: {trace_path}")
    if artifact["evidence_mode"] == "live_controlled" and artifact["execution_mode"] != "live_controlled":
        raise EvidencePackError(f"live_controlled trace has wrong execution mode: {trace_path}")
    if artifact["evidence_mode"] == "agentic_live_controlled":
        if artifact["execution_mode"] != "live_controlled":
            raise EvidencePackError(f"agentic trace has wrong execution mode: {trace_path}")
        if artifact["agentic_step_count"] < 1:
            raise EvidencePackError(f"agentic trace has no agentic steps: {trace_path}")
    if artifact["evidence_mode"] == "real_vision_controlled":
        if artifact["execution_mode"] != "live_controlled":
            raise EvidencePackError(f"real-vision trace has wrong execution mode: {trace_path}")
        provider = artifact.get("provider") or {}
        adapter = artifact.get("adapter") or {}
        if provider.get("package") != "browser-use-vision":
            raise EvidencePackError(f"real-vision trace missing provider metadata: {trace_path}")
        if adapter.get("api") != "browser_use_vision.som.annotate_screenshot":
            raise EvidencePackError(f"real-vision trace missing adapter metadata: {trace_path}")
        if not artifact["grounding_evidence_refs"]:
            raise EvidencePackError(f"real-vision trace has no grounding refs: {trace_path}")
    if artifact["evidence_mode"] == "real_voice_controlled":
        if artifact["execution_mode"] != "live_controlled":
            raise EvidencePackError(f"real-voice trace has wrong execution mode: {trace_path}")
        if artifact.get("input_source") != "audio":
            raise EvidencePackError(f"real-voice trace is not audio-sourced: {trace_path}")
        asr = artifact.get("asr") or {}
        if not asr.get("adapter_name"):
            raise EvidencePackError(f"real-voice trace missing ASR adapter metadata: {trace_path}")
        review = artifact.get("transcript_review") or {}
        if review.get("status") not in {"edited", "accepted"}:
            raise EvidencePackError(f"real-voice trace missing transcript review: {trace_path}")
        if not artifact["grounding_evidence_refs"] and artifact["agentic_step_count"] < 1:
            raise EvidencePackError(f"real-voice trace has no grounding or step evidence: {trace_path}")
        if artifact.get("privacy_scan") != "passed":
            raise EvidencePackError(f"real-voice privacy scan did not pass: {trace_path}")
    if artifact["evidence_mode"] == "real_use_failure":
        if artifact.get("input_source") != "audio":
            raise EvidencePackError(f"real-use trace is not audio-sourced: {trace_path}")
        if artifact.get("privacy_scan") != "passed":
            raise EvidencePackError(f"real-use privacy scan did not pass: {trace_path}")


def check_completeness(project_root: Path, artifacts: list[dict[str, Any]]) -> None:
    expected_preview = {
        path.name.removesuffix(".fixture.json")
        for path in sorted((project_root / "fixtures/audio").glob("*.fixture.json"))
    }
    selected_live = set(selected_live_fixture_ids())
    counts_by_mode: dict[str, dict[str, int]] = {}
    for item in artifacts:
        mode_counts = counts_by_mode.setdefault(item["evidence_mode"], {})
        mode_counts[item["fixture_id"]] = mode_counts.get(item["fixture_id"], 0) + 1
    for mode, mode_counts in sorted(counts_by_mode.items()):
        duplicates = sorted(fixture_id for fixture_id, count in mode_counts.items() if count > 1)
        if duplicates:
            raise EvidencePackError(f"ambiguous {mode} evidence for: {', '.join(duplicates)}")

    by_mode = {
        mode: {item["fixture_id"] for item in artifacts if item["evidence_mode"] == mode}
        for _, mode, _ in TRACE_GROUPS
    }
    missing_preview = sorted(expected_preview - by_mode["demo_preview"])
    missing_live = sorted(selected_live - by_mode["live_controlled"])
    missing_agentic = sorted(selected_live - by_mode["agentic_live_controlled"])
    missing_real_vision = sorted({"icon-search"} - by_mode["real_vision_controlled"])
    missing_real_voice = sorted({"icon-search"} - by_mode["real_voice_controlled"])
    required_usage = {
        "usage-asr-unavailable",
        "usage-clarification-required",
        "usage-confirmation-pending",
        "usage-confirmation-cancelled",
        "usage-ambiguous-visual-target",
    }
    missing_usage = sorted(required_usage - by_mode["real_use_failure"])
    if missing_preview:
        raise EvidencePackError(f"missing demo_preview evidence for: {', '.join(missing_preview)}")
    if missing_live:
        raise EvidencePackError(f"missing live_controlled evidence for: {', '.join(missing_live)}")
    if missing_agentic:
        raise EvidencePackError(
            f"missing agentic_live_controlled evidence for: {', '.join(missing_agentic)}"
        )
    if missing_real_vision:
        raise EvidencePackError(
            "missing real_vision_controlled evidence for: "
            + ", ".join(missing_real_vision)
        )
    if missing_real_voice:
        raise EvidencePackError(
            "missing real_voice_controlled evidence for: "
            + ", ".join(missing_real_voice)
        )
    if missing_usage:
        raise EvidencePackError(
            "missing real_use_failure evidence for: "
            + ", ".join(missing_usage)
        )


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
            raise EvidencePackError(f"private marker '{marker}' found in {path}")


def render_html(manifest: dict[str, Any]) -> str:
    rows = "\n".join(render_row(item) for item in manifest["artifacts"])
    matrix_rows = "\n".join(
        render_matrix_row(item)
        for item in manifest.get("public_readonly_reliability_matrix", {}).get("rows", [])
    )
    useful_rows = "\n".join(
        render_useful_task_pack_row(item)
        for item in manifest.get("public_readonly_useful_task_pack", {}).get("rows", [])
    )
    runner = manifest.get("public_readonly_live_task_pack_runner", {})
    runner_rows = "\n".join(render_task_pack_runner_row(item) for item in runner.get("rows", []))
    normalizer = manifest.get("normalizer_comparison", {})
    normalizer_rows = render_normalizer_comparison_rows(normalizer)
    generated_at = html.escape(manifest["generated_at"])
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Voice-to-Browser Agent Evidence Pack</title>
    <style>
      body {{ font-family: system-ui, sans-serif; margin: 32px; color: #172026; }}
      table {{ border-collapse: collapse; width: 100%; }}
      th, td {{ border: 1px solid #d6dde2; padding: 8px; text-align: left; vertical-align: top; }}
      th {{ background: #f1f4f6; }}
      code {{ background: #f1f4f6; padding: 2px 4px; }}
    </style>
  </head>
  <body>
    <h1>Voice-to-Browser Agent Evidence Pack</h1>
    <p>Bounded demo evidence pack for reproducible reviewer handoff.</p>
    <p>Generated at <code>{generated_at}</code>. Privacy scan: <strong>passed</strong>.</p>
    <h2>Public-readonly reliability matrix</h2>
    <p>Bounded local read-only matrix; raw public runtime traces, screenshots, and page text remain local/private.</p>
    <table>
      <thead>
        <tr>
          <th>Task</th>
          <th>Target</th>
          <th>Class</th>
          <th>Kind</th>
          <th>Outcome</th>
          <th>Criteria</th>
          <th>Reason</th>
          <th>Export</th>
        </tr>
      </thead>
      <tbody>
{matrix_rows}
      </tbody>
    </table>
    <h2>Public-readonly useful task pack</h2>
    <p>Reviewer-readable task-pack summary for stable documentation, reference, package metadata, release notes, and public repository read/search tasks. Raw public runtime artifacts remain local/private unless sanitizer-approved.</p>
    <table>
      <thead>
        <tr>
          <th>Task</th>
          <th>Category</th>
          <th>Target</th>
          <th>Outcome</th>
          <th>Proof</th>
          <th>Unmet</th>
          <th>Reason</th>
          <th>Export</th>
        </tr>
      </thead>
      <tbody>
{useful_rows}
      </tbody>
    </table>
    <h2>Public-readonly live task-pack runner</h2>
    <p>Latest local/private runner summary: <code>{html.escape(runner.get("run_id") or "not available")}</code>; mode <code>{html.escape(runner.get("runner_mode") or "n/a")}</code>; sanitizer <code>{html.escape(runner.get("sanitizer_status") or "n/a")}</code>.</p>
    <table>
      <thead>
        <tr>
          <th>Task</th>
          <th>Class</th>
          <th>Kind</th>
          <th>Outcome</th>
          <th>Proof</th>
          <th>Unmet</th>
          <th>Reason</th>
          <th>Export</th>
        </tr>
      </thead>
      <tbody>
{runner_rows}
      </tbody>
    </table>
    <h2>Normalizer comparison</h2>
    <p>Local structured-output comparison, not model training; status <code>{html.escape(normalizer.get("status") or "not_provided")}</code>; export <code>{html.escape(normalizer.get("export_state") or "n/a")}</code>.</p>
    <table>
      <thead>
        <tr>
          <th>Modes</th>
          <th>Inputs</th>
          <th>Rows</th>
          <th>Schema</th>
          <th>Validator</th>
          <th>Fallback</th>
          <th>Safety</th>
        </tr>
      </thead>
      <tbody>
{normalizer_rows}
      </tbody>
    </table>
    <h2>Packaged evidence</h2>
    <table>
      <thead>
        <tr>
          <th>Fixture</th>
          <th>Evidence Mode</th>
          <th>Status</th>
          <th>Reason</th>
          <th>Trace</th>
          <th>Grounding</th>
          <th>Provider</th>
          <th>ASR</th>
          <th>Review</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </body>
</html>
"""


def render_row(item: dict[str, Any]) -> str:
    reason = item.get("stop_reason") or item.get("failure_reason") or ""
    refs = ", ".join(item.get("grounding_evidence_refs") or [])
    provider = item.get("provider") or {}
    provider_label = provider.get("package") or ""
    asr = item.get("asr") or {}
    review = item.get("transcript_review") or {}
    return (
        "        <tr>"
        f"<td>{html.escape(item['fixture_id'])}</td>"
        f"<td>{html.escape(item['evidence_mode'])}</td>"
        f"<td>{html.escape(item.get('final_status') or '')}</td>"
        f"<td>{html.escape(reason)}</td>"
        f"<td><code>{html.escape(item['packaged_path'])}</code></td>"
        f"<td>{html.escape(refs)}</td>"
        f"<td>{html.escape(provider_label)}</td>"
        f"<td>{html.escape(asr.get('adapter_name') or '')}</td>"
        f"<td>{html.escape(review.get('status') or '')}</td>"
        "</tr>"
    )


def render_matrix_row(item: dict[str, Any]) -> str:
    reason = item.get("stop_or_failure_reason") or ""
    criteria = ", ".join(item.get("completion_criteria_summary") or [])
    return (
        "        <tr>"
        f"<td>{html.escape(item.get('task_id') or '')}</td>"
        f"<td>{html.escape(item.get('target_label') or '')}</td>"
        f"<td>{html.escape(item.get('target_class') or '')}</td>"
        f"<td>{html.escape(item.get('task_kind') or '')}</td>"
        f"<td>{html.escape(item.get('outcome') or '')}</td>"
        f"<td>{html.escape(criteria)}</td>"
        f"<td>{html.escape(reason)}</td>"
        f"<td>{html.escape(item.get('export_state') or '')}</td>"
        "</tr>"
    )


def render_useful_task_pack_row(item: dict[str, Any]) -> str:
    reason = item.get("stop_or_failure_reason") or ""
    proof = format_observed_proof(item.get("observed_proof_summary") or {})
    unmet = ", ".join(item.get("unmet_criteria") or [])
    return (
        "        <tr>"
        f"<td>{html.escape(item.get('task_id') or '')}</td>"
        f"<td>{html.escape(item.get('task_category') or '')}</td>"
        f"<td>{html.escape(item.get('target_label') or '')}</td>"
        f"<td>{html.escape(item.get('outcome') or '')}</td>"
        f"<td>{html.escape(proof)}</td>"
        f"<td>{html.escape(unmet)}</td>"
        f"<td>{html.escape(reason)}</td>"
        f"<td>{html.escape(item.get('export_state') or '')}</td>"
        "</tr>"
    )


def render_task_pack_runner_row(item: dict[str, Any]) -> str:
    reason = item.get("stop_or_failure_reason") or item.get("route_or_execution_reason") or ""
    proof = format_observed_proof(item.get("observed_proof_summary") or {})
    unmet = ", ".join(item.get("unmet_criteria") or [])
    return (
        "        <tr>"
        f"<td>{html.escape(item.get('task_id') or '')}</td>"
        f"<td>{html.escape(item.get('target_class') or '')}</td>"
        f"<td>{html.escape(item.get('task_kind') or '')}</td>"
        f"<td>{html.escape(item.get('outcome') or '')}</td>"
        f"<td>{html.escape(proof)}</td>"
        f"<td>{html.escape(unmet)}</td>"
        f"<td>{html.escape(reason)}</td>"
        f"<td>{html.escape(item.get('export_state') or '')}</td>"
        "</tr>"
    )


def render_normalizer_comparison_rows(item: dict[str, Any]) -> str:
    modes = ", ".join(item.get("normalizer_modes") or [])
    schema = format_observed_proof(item.get("schema_status_counts") or {})
    validator = format_observed_proof(item.get("validator_outcome_counts") or {})
    fallback = format_observed_proof(item.get("fallback_counts") or {})
    safety = format_observed_proof(item.get("safety_outcome_counts") or {})
    return (
        "        <tr>"
        f"<td>{html.escape(modes)}</td>"
        f"<td>{html.escape(str(item.get('input_count') or ''))}</td>"
        f"<td>{html.escape(str(item.get('row_count') or ''))}</td>"
        f"<td>{html.escape(schema)}</td>"
        f"<td>{html.escape(validator)}</td>"
        f"<td>{html.escape(fallback)}</td>"
        f"<td>{html.escape(safety)}</td>"
        "</tr>"
    )


def format_observed_proof(observed_proof: dict[str, Any]) -> str:
    return ", ".join(
        f"{key}: {value}"
        for key, value in observed_proof.items()
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Voice-to-Browser demo evidence pack.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--trace-root", type=Path, default=DEFAULT_TRACE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--task-pack-run-root", type=Path)
    parser.add_argument("--normalizer-comparison-path", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = build_release_pack(
            project_root=args.project_root,
            trace_root=args.trace_root,
            output_dir=args.output_dir,
            task_pack_run_root=args.task_pack_run_root,
            normalizer_comparison_path=args.normalizer_comparison_path,
        )
    except EvidencePackError as exc:
        print(f"error: {exc}")
        return 1
    print(f"wrote {args.output_dir}")
    print(f"artifacts: {len(manifest['artifacts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
