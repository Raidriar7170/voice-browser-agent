from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote, quote_plus
from uuid import uuid4

from voice_browser_agent.config import RuntimeConfig, load_config
from voice_browser_agent.executor import BrowserExecutorAdapter, BrowserExecutorConfig
from voice_browser_agent.models import (
    BrowserIntentType,
    BrowserTaskRequest,
    ExecutionMode,
    ExecutionStatus,
    PublicTaskContract,
    PublicTaskCompletionState,
    PublicReadonlyUsefulTask,
)
from voice_browser_agent.public_readonly import (
    RELIABILITY_OUTCOMES,
    ReliabilityMatrixError,
    load_public_readonly_useful_task_pack,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runtime/public-readonly-task-pack"
MANIFEST_VERSION = "public_readonly_task_pack_run.v1"


class TaskPackRunnerError(RuntimeError):
    pass


def run_task_pack(
    *,
    project_root: Path = PROJECT_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    task_ids: list[str] | None = None,
    mode: str = "deterministic",
    run_all: bool = False,
    run_id: str | None = None,
    config: RuntimeConfig | None = None,
    agent_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root)
    output_dir = Path(output_dir)
    selected_mode = _validate_mode(mode)
    if selected_mode == "live" and not task_ids and not run_all:
        raise TaskPackRunnerError("live mode requires --task-id or --all")
    pack = load_public_readonly_useful_task_pack(
        project_root / "fixtures/public-readonly-useful-task-pack.json"
    )
    selected_tasks = _select_tasks(pack.tasks, task_ids=task_ids, run_all=run_all)
    run_id = run_id or f"run-{uuid4().hex[:12]}"
    started_at = _utc_now()
    config = config or RuntimeConfig()

    rows: list[dict[str, Any]] = []
    live_network_attempted = False
    for task in selected_tasks:
        if selected_mode == "deterministic":
            rows.append(_deterministic_row(task))
            continue
        if not config.public_readonly_enabled:
            rows.append(_blocked_row(task, reason="public_readonly_disabled"))
            continue
        live_network_attempted = True
        rows.append(
            _run_live_task(
                task=task,
                config=config,
                output_dir=output_dir,
                run_id=run_id,
                agent_factory=agent_factory,
            )
        )

    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": _utc_now(),
        "runner_mode": selected_mode,
        "live_network_attempted": live_network_attempted,
        "task_count": len(pack.tasks),
        "selected_task_ids": [task.task_id for task in selected_tasks],
        "selected_task_count": len(selected_tasks),
        "configuration_summary": _configuration_summary(config),
        "outcome_counts": _outcome_counts(rows),
        "privacy_state": "local_private",
        "sanitizer_status": "pending",
        "export_state": "local_private",
        "limitation_notes": [
            "Task-pack runner output is local/private reviewer evidence.",
            "Raw public runtime traces, screenshots, page text, session data, and browser profile data are not exported.",
            "Live mode is opt-in and limited to validated public-readonly task contracts.",
        ],
        "rows": rows,
    }
    manifest_path = output_dir / "runs" / run_id / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def _validate_mode(mode: str) -> str:
    if mode not in {"deterministic", "live"}:
        raise TaskPackRunnerError(f"unsupported runner mode: {mode}")
    return mode


def _select_tasks(
    tasks: list[PublicReadonlyUsefulTask],
    *,
    task_ids: list[str] | None,
    run_all: bool,
) -> list[PublicReadonlyUsefulTask]:
    by_id = {task.task_id: task for task in tasks}
    if task_ids:
        unknown = [task_id for task_id in task_ids if task_id not in by_id]
        if unknown:
            raise TaskPackRunnerError(f"unknown task id: {', '.join(unknown)}")
        return [by_id[task_id] for task_id in task_ids]
    if run_all:
        return list(tasks)
    return list(tasks)


def _deterministic_row(task: PublicReadonlyUsefulTask) -> dict[str, Any]:
    evidence = task.task_pack_attempt_evidence
    return _base_row(
        task,
        outcome=evidence.outcome.value,
        final_status=evidence.final_status.value,
        observed_proof_summary=dict(evidence.observed_proof_summary),
        unmet_criteria=list(evidence.unmet_criteria),
        stop_or_failure_reason=evidence.stop_or_failure_reason,
        route_or_execution_reason=(
            evidence.stop_or_failure_reason
            or f"deterministic_{evidence.outcome.value}_task_pack_evidence"
        ),
        visible_result_state=evidence.visible_result_state,
        sanitizer_status=evidence.sanitizer_status.value,
        evidence_privacy_state=evidence.evidence_privacy_state.value,
        export_state=evidence.export_state,
    )


def _blocked_row(task: PublicReadonlyUsefulTask, *, reason: str) -> dict[str, Any]:
    return _base_row(
        task,
        outcome=PublicTaskCompletionState.BLOCKED.value,
        final_status=ExecutionStatus.BLOCKED.value,
        observed_proof_summary={},
        unmet_criteria=list(task.completion_criteria.required_proof),
        stop_or_failure_reason=reason,
        route_or_execution_reason=reason,
        visible_result_state="not_captured",
        sanitizer_status="pending",
        evidence_privacy_state="local_private",
        export_state="local_private",
    )


def _run_live_task(
    *,
    task: PublicReadonlyUsefulTask,
    config: RuntimeConfig,
    output_dir: Path,
    run_id: str,
    agent_factory: Callable[..., Any] | None,
) -> dict[str, Any]:
    target_url = _target_url(task)
    contract = _contract_for_task(task)
    request = _request_for_task(task)
    executor = BrowserExecutorAdapter(
        BrowserExecutorConfig(
            local_browser=True,
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            browser_channel="chromium",
            max_steps=task.limits["max_steps"],
            public_target_url=target_url,
            public_target_label=task.target_label,
            public_target_class=task.target_class,
            public_origin=_origin_for_url(target_url),
            public_allowlist_id=task.allowlist_id,
            public_task_contract=contract,
            public_task_slots=dict(task.requested_slots),
            public_timeout_seconds=task.limits["timeout_seconds"],
            public_sanitizer_required=config.public_readonly_sanitizer_required,
            public_visual_artifacts_dir=output_dir / "artifacts" / run_id,
            public_headed_debug=config.public_readonly_headed_debug,
        ),
        agent_factory=agent_factory,
    )
    result = asyncio.run(executor.execute(request, execution_id=f"{run_id}-{task.task_id}"))
    runtime_row = result.runtime.get("public_reliability_matrix_row")
    if not isinstance(runtime_row, dict):
        return _base_row(
            task,
            outcome=PublicTaskCompletionState.FAILED.value,
            final_status=result.final_status.value,
            observed_proof_summary={},
            unmet_criteria=list(task.completion_criteria.required_proof),
            stop_or_failure_reason=result.stop_reason or result.failure_reason or "public_readonly_missing_evidence",
            route_or_execution_reason=result.stop_reason or result.failure_reason or "public_readonly_missing_evidence",
            visible_result_state="not_captured",
            sanitizer_status="pending",
            evidence_privacy_state="local_private",
            export_state="local_private",
        )
    return {
        **_base_row(
            task,
            outcome=runtime_row.get("outcome") or PublicTaskCompletionState.FAILED.value,
            final_status=runtime_row.get("final_status") or result.final_status.value,
            observed_proof_summary=runtime_row.get("observed_proof_summary") or {},
            unmet_criteria=runtime_row.get("unmet_criteria") or [],
            stop_or_failure_reason=runtime_row.get("stop_or_failure_reason"),
            route_or_execution_reason=runtime_row.get("stop_or_failure_reason")
            or result.stop_reason
            or result.failure_reason
            or "public_readonly_live_attempt",
            visible_result_state=runtime_row.get("visible_result_state") or "not_captured",
            sanitizer_status=runtime_row.get("sanitizer_status") or "pending",
            evidence_privacy_state=runtime_row.get("evidence_privacy_state") or "local_private",
            export_state=runtime_row.get("export_state") or "local_private",
        ),
        "browser_context": result.runtime.get(
            "browser_context",
            {
                "isolation": "fresh_ephemeral",
                "persistent_profile": False,
                "cookies_reused": False,
                "storage_state_reused": False,
            },
        ),
    }


def _base_row(
    task: PublicReadonlyUsefulTask,
    *,
    outcome: str,
    final_status: str,
    observed_proof_summary: dict[str, Any],
    unmet_criteria: list[str],
    stop_or_failure_reason: str | None,
    route_or_execution_reason: str,
    visible_result_state: str,
    sanitizer_status: str,
    evidence_privacy_state: str,
    export_state: str,
) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "task_category": task.task_category,
        "task_kind": task.task_kind,
        "target_class": task.target_class,
        "target_label": task.target_label,
        "sanitized_origin": _origin_for_url(_target_url(task)),
        "completion_criteria_id": task.completion_criteria.criteria_id,
        "completion_criteria_summary": list(task.completion_criteria.required_proof),
        "outcome": outcome,
        "final_status": final_status,
        "observed_proof_summary": observed_proof_summary,
        "unmet_criteria": unmet_criteria,
        "stop_or_failure_reason": stop_or_failure_reason,
        "route_or_execution_reason": route_or_execution_reason,
        "visible_result_state": visible_result_state,
        "evidence_privacy_state": evidence_privacy_state,
        "sanitizer_status": sanitizer_status,
        "export_state": export_state,
        "browser_context": {
            "isolation": "fresh_ephemeral",
            "persistent_profile": False,
            "cookies_reused": False,
            "storage_state_reused": False,
        },
    }


def _contract_for_task(task: PublicReadonlyUsefulTask) -> PublicTaskContract:
    return PublicTaskContract(
        task_id=task.task_id,
        task_kind=task.task_kind,
        allowlist_id=task.allowlist_id,
        target_class=task.target_class,
        task_category=task.task_category,
        target_url=task.target_url,
        target_url_template=task.target_url_template,
        allowed_actions=list(task.allowed_actions),
        slots=list(task.safe_slots),
        completion_criteria=task.completion_criteria,
        max_steps=task.limits["max_steps"],
        timeout_seconds=task.limits["timeout_seconds"],
        privacy_policy=task.privacy_policy,
    )


def _request_for_task(task: PublicReadonlyUsefulTask) -> BrowserTaskRequest:
    intent = (
        BrowserIntentType.SEARCH_OPEN
        if "search" in (task.browser_intent_type or task.task_kind)
        else BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO
    )
    return BrowserTaskRequest(
        task=task.command or f"Run public-readonly task {task.task_id}",
        intent_type=intent,
        constraints=["public_readonly", "read-only", "no login", "no upload/download"],
        requires_confirmation=False,
        stop_conditions=list(task.safety_boundaries),
        safety_flags=[],
        public_task_slots=dict(task.requested_slots),
    )


def _target_url(task: PublicReadonlyUsefulTask) -> str:
    if task.target_url:
        return task.target_url
    if not task.target_url_template:
        raise TaskPackRunnerError(f"task {task.task_id} missing target URL")
    try:
        return task.target_url_template.format(**_format_url_slots(task.requested_slots))
    except KeyError as exc:
        raise TaskPackRunnerError(f"task {task.task_id} missing URL slot: {exc}") from exc


def _format_url_slots(slots: dict[str, Any]) -> dict[str, str]:
    formatted: dict[str, str] = {}
    for key, value in slots.items():
        text = str(value)
        if key == "search_query":
            formatted[key] = quote_plus(text)
        elif key in {"owner", "repo"}:
            formatted[key] = quote(text, safe="")
        else:
            formatted[key] = text
    return formatted


def _origin_for_url(url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc.lower()}"


def _configuration_summary(config: RuntimeConfig) -> dict[str, Any]:
    return {
        "public_readonly_enabled": config.public_readonly_enabled,
        "max_steps": config.public_readonly_max_steps,
        "timeout_seconds": config.public_readonly_timeout_seconds,
        "private_traces": config.public_readonly_private_traces,
        "sanitizer_required": config.public_readonly_sanitizer_required,
        "browser_context": {
            "isolation": "fresh_ephemeral",
            "persistent_profile": False,
        },
    }


def _outcome_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {outcome.value: 0 for outcome in RELIABILITY_OUTCOMES}
    for row in rows:
        outcome = str(row.get("outcome") or "")
        if outcome in counts:
            counts[outcome] += 1
    return counts


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the public-readonly useful task pack.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument("--all", action="store_true", dest="run_all")
    parser.add_argument("--mode", choices=("deterministic", "live"), default="deterministic")
    parser.add_argument("--run-id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = run_task_pack(
            project_root=args.project_root,
            output_dir=args.output_dir,
            task_ids=args.task_ids,
            mode=args.mode,
            run_all=args.run_all,
            run_id=args.run_id,
            config=load_config(),
        )
    except (TaskPackRunnerError, ReliabilityMatrixError) as exc:
        print(f"error: {exc}")
        return 1
    print(f"wrote {args.output_dir / 'runs' / manifest['run_id'] / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
