from __future__ import annotations

import ipaddress
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote_plus, urlparse

from pydantic import BaseModel, Field, ValidationError

from .config import RuntimeConfig
from .models import (
    BrowserTaskRequest,
    EvidencePrivacyState,
    ExecutionStatus,
    PublicTaskCompletionResult,
    PublicTaskCompletionState,
    PublicTaskContract,
    PublicReadonlyReliabilityMatrixRow,
    PublicReadonlyReliabilityMatrixSummary,
    PublicReadonlyReliabilitySmokeSet,
    PublicReadonlyUsefulTaskPack,
    USEFUL_TASK_PACK_REQUIRED_CATEGORIES,
    SanitizerStatus,
)


PUBLIC_TARGET_MARKERS = (
    "http://",
    "https://",
    "openai",
    "python",
    "mdn",
    "wikipedia",
    "github",
    "pypi",
    "npm",
    "package",
    "release",
    "releases",
    "repository",
    "repositories",
    "repo",
    "docs",
    "documentation",
    "public",
    "公开",
    "文档",
    "网站",
)

READONLY_ACTIONS = {"navigate", "search", "filter", "expand", "extract", "inspect", "observe", "read"}
RELIABILITY_OUTCOMES = (
    PublicTaskCompletionState.COMPLETED,
    PublicTaskCompletionState.PARTIAL,
    PublicTaskCompletionState.STOPPED,
    PublicTaskCompletionState.FAILED,
    PublicTaskCompletionState.BLOCKED,
)
PAGE_OPEN_ONLY_PROOF_KEYS = {"final_title", "url_path"}
TASK_PACK_RUN_MANIFEST_VERSION = "public_readonly_task_pack_run.v1"
TASK_PACK_RUN_REQUIRED_TOP_LEVEL_FIELDS = {
    "manifest_version",
    "run_id",
    "finished_at",
    "runner_mode",
    "selected_task_count",
    "outcome_counts",
    "privacy_state",
    "sanitizer_status",
    "export_state",
    "rows",
}
TASK_PACK_RUN_REQUIRED_ROW_FIELDS = {
    "task_id",
    "task_category",
    "task_kind",
    "target_class",
    "target_label",
    "sanitized_origin",
    "completion_criteria_id",
    "completion_criteria_summary",
    "outcome",
    "final_status",
    "observed_proof_summary",
    "unmet_criteria",
    "stop_or_failure_reason",
    "route_or_execution_reason",
    "visible_result_state",
    "evidence_privacy_state",
    "sanitizer_status",
    "export_state",
}
TASK_PACK_RUN_PRIVATE_MARKERS = (
    "raw_page_text",
    "raw_screenshot",
    "browser_profile",
    "storage_state",
    "cookies",
    "credential",
    "password",
    "token",
    "private_url",
    "remote_host",
    "file:///Users/",
    "file:///users/",
    "/Users/",
    "/users/",
)


class ReliabilityMatrixError(RuntimeError):
    pass


class PublicReadonlyTarget(BaseModel):
    allowlist_id: str
    label: str
    url: str
    origin: str
    keywords: list[str] = Field(default_factory=list)
    task_contracts: list[PublicTaskContract] = Field(default_factory=list)


class PublicReadonlyRoutingConfig(BaseModel):
    enabled: bool = False
    targets: list[PublicReadonlyTarget] = Field(default_factory=list)
    max_steps: int = 3
    timeout_seconds: int = 15
    private_traces: bool = True
    sanitizer_required: bool = True

    @classmethod
    def from_runtime_config(cls, config: RuntimeConfig) -> "PublicReadonlyRoutingConfig":
        return cls(
            enabled=config.public_readonly_enabled,
            targets=parse_public_readonly_targets(config),
            max_steps=config.public_readonly_max_steps,
            timeout_seconds=config.public_readonly_timeout_seconds,
            private_traces=config.public_readonly_private_traces,
            sanitizer_required=config.public_readonly_sanitizer_required,
        )

    @classmethod
    def from_executor_target(
        cls,
        *,
        target_url: str,
        target_label: str,
        public_origin: str,
        allowlist_id: str,
        max_steps: int,
        timeout_seconds: int,
        sanitizer_required: bool = True,
    ) -> "PublicReadonlyRoutingConfig":
        target = PublicReadonlyTarget(
            allowlist_id=allowlist_id,
            label=target_label,
            url=target_url,
            origin=public_origin,
            keywords=_default_keywords(allowlist_id, target_label, target_url),
        )
        return cls(
            enabled=True,
            targets=[target],
            max_steps=max_steps,
            timeout_seconds=timeout_seconds,
            private_traces=True,
            sanitizer_required=sanitizer_required,
        )


class PublicReadonlyPolicyDecision(BaseModel):
    allowed: bool
    reason: str
    detail: str | None = None


def load_public_readonly_smoke_set(path: str | Path) -> PublicReadonlyReliabilitySmokeSet:
    smoke_path = Path(path)
    try:
        payload = json.loads(smoke_path.read_text(encoding="utf-8"))
        _validate_completion_criteria_payload(payload)
        _validate_attempt_evidence_payload(payload)
        smoke_set = PublicReadonlyReliabilitySmokeSet.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        raise ReliabilityMatrixError(f"invalid public-readonly smoke set completion criteria: {exc}") from exc

    for task in smoke_set.tasks:
        if not set(task.allowed_actions).issubset(READONLY_ACTIONS):
            raise ReliabilityMatrixError(f"task {task.task_id} includes non-read-only action")
        if task.privacy_policy != "local_private":
            raise ReliabilityMatrixError(f"task {task.task_id} must keep privacy_policy local_private")
        if not task.completion_criteria.required_proof:
            raise ReliabilityMatrixError(f"task {task.task_id} missing task-specific completion criteria")
        evidence = task.reliability_attempt_evidence
        if evidence.outcome is not task.expected_matrix_coverage:
            raise ReliabilityMatrixError(
                f"ambiguous attempt evidence for task {task.task_id}: "
                "outcome does not match expected matrix coverage"
            )
        if evidence.outcome is PublicTaskCompletionState.COMPLETED:
            missing_proof = [
                proof
                for proof in task.completion_criteria.required_proof
                if proof not in evidence.observed_proof_summary
            ]
            if missing_proof:
                raise ReliabilityMatrixError(
                    f"task {task.task_id} missing observed proof: {', '.join(missing_proof)}"
                )

    outcomes = {task.reliability_attempt_evidence.outcome for task in smoke_set.tasks}
    missing = [outcome.value for outcome in RELIABILITY_OUTCOMES if outcome not in outcomes]
    if missing:
        raise ReliabilityMatrixError(f"missing outcome coverage: {', '.join(missing)}")
    return smoke_set


def load_public_readonly_useful_task_pack(path: str | Path) -> PublicReadonlyUsefulTaskPack:
    pack_path = Path(path)
    try:
        payload = json.loads(pack_path.read_text(encoding="utf-8"))
        _validate_useful_task_pack_payload(payload)
        task_pack = PublicReadonlyUsefulTaskPack.model_validate(payload)
    except ReliabilityMatrixError:
        raise
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        raise ReliabilityMatrixError(
            f"invalid public-readonly useful task pack completion criteria: {exc}"
        ) from exc

    _validate_useful_task_pack(task_pack)
    return task_pack


def _validate_completion_criteria_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ReliabilityMatrixError("invalid public-readonly smoke set payload")
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise ReliabilityMatrixError("invalid public-readonly smoke set tasks")
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ReliabilityMatrixError(f"task {index + 1} malformed completion criteria")
        task_id = task.get("id") or task.get("task_id") or f"task {index + 1}"
        criteria = task.get("completion_criteria")
        required_proof = criteria.get("required_proof") if isinstance(criteria, dict) else None
        if not required_proof:
            raise ReliabilityMatrixError(
                f"task {task_id} missing task-specific completion criteria"
            )


def _validate_attempt_evidence_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ReliabilityMatrixError("invalid public-readonly smoke set payload")
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise ReliabilityMatrixError("invalid public-readonly smoke set tasks")
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ReliabilityMatrixError(f"task {index + 1} malformed attempt evidence")
        task_id = task.get("id") or task.get("task_id") or f"task {index + 1}"
        evidence = task.get("reliability_attempt_evidence")
        if evidence is None:
            raise ReliabilityMatrixError(f"task {task_id} missing attempt evidence")
        if not isinstance(evidence, dict):
            raise ReliabilityMatrixError(f"task {task_id} malformed attempt evidence")


def _validate_useful_task_pack_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ReliabilityMatrixError("invalid public-readonly useful task pack payload")
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise ReliabilityMatrixError("invalid public-readonly useful task pack tasks")

    required_categories = payload.get("required_categories") or list(
        USEFUL_TASK_PACK_REQUIRED_CATEGORIES
    )
    task_categories = {
        task.get("task_category")
        for task in tasks
        if isinstance(task, dict) and task.get("task_category")
    }
    missing_categories = [
        category for category in required_categories if category not in task_categories
    ]
    if missing_categories:
        raise ReliabilityMatrixError(
            f"missing category coverage: {', '.join(missing_categories)}"
        )

    if len(tasks) < 8:
        raise ReliabilityMatrixError("fewer than 8 useful public-readonly tasks")
    if len(tasks) > 12:
        raise ReliabilityMatrixError("more than 12 useful public-readonly tasks")

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ReliabilityMatrixError(f"task {index + 1} malformed useful task")
        task_id = task.get("id") or task.get("task_id") or f"task {index + 1}"
        criteria = task.get("completion_criteria")
        required_proof = criteria.get("required_proof") if isinstance(criteria, dict) else None
        if not required_proof:
            raise ReliabilityMatrixError(
                f"task {task_id} missing task-specific completion criteria"
            )
        actions = task.get("allowed_actions")
        if not isinstance(actions, list) or not actions:
            raise ReliabilityMatrixError(f"task {task_id} missing read-only actions")
        if not set(actions).issubset(READONLY_ACTIONS):
            raise ReliabilityMatrixError(f"task {task_id} includes non-read-only action")
        evidence = task.get("task_pack_attempt_evidence")
        if evidence is None:
            raise ReliabilityMatrixError(f"task {task_id} missing task-pack attempt evidence")
        if not isinstance(evidence, dict):
            raise ReliabilityMatrixError(f"task {task_id} malformed task-pack attempt evidence")


def _validate_useful_task_pack(task_pack: PublicReadonlyUsefulTaskPack) -> None:
    category_counts = task_pack.category_counts
    missing_categories = [
        category
        for category in task_pack.required_categories
        if category_counts.get(category, 0) == 0
    ]
    if missing_categories:
        raise ReliabilityMatrixError(
            f"missing category coverage: {', '.join(missing_categories)}"
        )

    seen_task_ids: set[str] = set()
    for task in task_pack.tasks:
        if task.task_id in seen_task_ids:
            raise ReliabilityMatrixError(f"duplicate task id: {task.task_id}")
        seen_task_ids.add(task.task_id)
        if task.task_category not in task_pack.required_categories:
            raise ReliabilityMatrixError(
                f"missing category coverage: unsupported category {task.task_category}"
            )
        for candidate_url in (task.target_url, task.target_url_template):
            unsafe_target_reason = _useful_task_target_safety_reason(candidate_url)
            if unsafe_target_reason is not None:
                raise ReliabilityMatrixError(
                    f"task {task.task_id} unsafe public target: {unsafe_target_reason}"
                )
        requested_slot_names = set(task.requested_slots)
        unsafe_slots = sorted(requested_slot_names.difference(task.safe_slots))
        if unsafe_slots:
            raise ReliabilityMatrixError(
                f"task {task.task_id} requested slot outside safe_slots: "
                f"{', '.join(unsafe_slots)}"
            )
        if not set(task.allowed_actions).issubset(READONLY_ACTIONS):
            raise ReliabilityMatrixError(f"task {task.task_id} includes non-read-only action")
        if task.privacy_policy != "local_private":
            raise ReliabilityMatrixError(
                f"task {task.task_id} must keep privacy_policy local_private"
            )
        if task.artifact_status != "local_private_until_sanitized":
            raise ReliabilityMatrixError(
                f"task {task.task_id} must keep artifacts local_private_until_sanitized"
            )
        evidence = task.task_pack_attempt_evidence
        if evidence.outcome is not task.expected_task_pack_coverage:
            raise ReliabilityMatrixError(
                f"ambiguous attempt evidence for task {task.task_id}: "
                "outcome does not match expected task-pack coverage"
            )
        if (
            evidence.evidence_privacy_state is not EvidencePrivacyState.LOCAL_PRIVATE
            or evidence.sanitizer_status is not SanitizerStatus.PENDING
            or evidence.export_state != "local_private"
        ):
            raise ReliabilityMatrixError(
                f"task {task.task_id} must keep local/private attempt evidence"
            )
        if (
            evidence.outcome is PublicTaskCompletionState.COMPLETED
            and set(task.completion_criteria.required_proof).issubset(
                PAGE_OPEN_ONLY_PROOF_KEYS
            )
        ):
            raise ReliabilityMatrixError(
                f"task {task.task_id} has page-open-only completion criteria"
            )
        if evidence.outcome is PublicTaskCompletionState.COMPLETED:
            missing_proof = [
                proof
                for proof in task.completion_criteria.required_proof
                if proof not in evidence.observed_proof_summary
            ]
            if missing_proof:
                raise ReliabilityMatrixError(
                    f"task {task.task_id} missing observed proof: {', '.join(missing_proof)}"
                )

    outcomes = {task.task_pack_attempt_evidence.outcome for task in task_pack.tasks}
    missing_outcomes = [
        outcome.value for outcome in RELIABILITY_OUTCOMES if outcome not in outcomes
    ]
    if missing_outcomes:
        raise ReliabilityMatrixError(f"missing outcome coverage: {', '.join(missing_outcomes)}")


def _useful_task_target_safety_reason(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "unsafe_protocol"
    if parsed.username or parsed.password:
        return "credentialed_url"
    host = (parsed.hostname or "").lower()
    if not host:
        return "missing_public_host"
    if "{" in host or "}" in host:
        return "templated_public_host"
    if _is_private_host(host):
        return "private_network_target"
    return None


def summarize_reliability_matrix(
    rows: list[PublicReadonlyReliabilityMatrixRow],
) -> PublicReadonlyReliabilityMatrixSummary:
    if not rows:
        raise ReliabilityMatrixError("missing outcome coverage: no reliability matrix rows")
    seen_task_ids: set[str] = set()
    outcome_counts = {outcome.value: 0 for outcome in RELIABILITY_OUTCOMES}
    for row in rows:
        if row.task_id in seen_task_ids:
            raise ReliabilityMatrixError(f"ambiguous reliability matrix row for task {row.task_id}")
        seen_task_ids.add(row.task_id)
        outcome_counts[row.outcome.value] += 1
        if row.outcome is PublicTaskCompletionState.COMPLETED:
            if not row.observed_proof_summary or row.unmet_criteria:
                raise ReliabilityMatrixError(f"ambiguous completed reliability row for {row.task_id}")
        else:
            if not row.unmet_criteria and not row.stop_or_failure_reason:
                raise ReliabilityMatrixError(f"ambiguous incomplete reliability row for {row.task_id}")

    missing = [outcome for outcome, count in outcome_counts.items() if count == 0]
    if missing:
        raise ReliabilityMatrixError(f"missing outcome coverage: {', '.join(missing)}")
    public_ready = all(
        row.evidence_privacy_state is EvidencePrivacyState.PUBLIC_SAFE
        and row.sanitizer_status is SanitizerStatus.PASSED
        and row.export_state == "public_safe"
        for row in rows
    )
    return PublicReadonlyReliabilityMatrixSummary(
        task_count=len(rows),
        outcome_counts=outcome_counts,
        missing_outcomes=[],
        is_complete=True,
        public_ready=public_ready,
        rows=rows,
    )


def summarize_useful_task_pack(task_pack: PublicReadonlyUsefulTaskPack) -> dict[str, Any]:
    outcome_counts = {outcome.value: 0 for outcome in RELIABILITY_OUTCOMES}
    rows: list[dict[str, Any]] = []
    for task in task_pack.tasks:
        evidence = task.task_pack_attempt_evidence
        outcome_counts[evidence.outcome.value] += 1
        rows.append(
            {
                "task_id": task.task_id,
                "target_label": task.target_label,
                "target_class": task.target_class,
                "task_category": task.task_category,
                "task_kind": task.task_kind,
                "completion_criteria_id": task.completion_criteria.criteria_id,
                "completion_criteria_summary": list(task.completion_criteria.required_proof),
                "outcome": evidence.outcome.value,
                "final_status": evidence.final_status.value,
                "observed_proof_summary": dict(evidence.observed_proof_summary),
                "unmet_criteria": list(evidence.unmet_criteria),
                "stop_or_failure_reason": evidence.stop_or_failure_reason,
                "evidence_privacy_state": evidence.evidence_privacy_state.value,
                "sanitizer_status": evidence.sanitizer_status.value,
                "visible_result_state": evidence.visible_result_state,
                "export_state": evidence.export_state,
                "regression_coverage": list(
                    evidence.regression_coverage
                    or task.regression_coverage
                    or [f"{evidence.outcome.value}_coverage"]
                ),
            }
        )

    missing_categories = [
        category
        for category in task_pack.required_categories
        if task_pack.category_counts.get(category, 0) == 0
    ]
    missing_outcomes = [
        outcome for outcome, count in outcome_counts.items() if count == 0
    ]
    public_ready = all(
        row["evidence_privacy_state"] == EvidencePrivacyState.PUBLIC_SAFE.value
        and row["sanitizer_status"] == SanitizerStatus.PASSED.value
        and row["export_state"] == "public_safe"
        for row in rows
    )
    return {
        "summary_version": "public_readonly_useful_task_pack.v1",
        "task_count": len(task_pack.tasks),
        "required_categories": list(task_pack.required_categories),
        "category_counts": dict(task_pack.category_counts),
        "outcome_counts": outcome_counts,
        "missing_categories": missing_categories,
        "missing_outcomes": missing_outcomes,
        "is_complete": not missing_categories and not missing_outcomes,
        "public_ready": public_ready,
        "privacy_state": "local_private",
        "export_state": "local_private",
        "boundaries": list(task_pack.boundaries),
        "rows": rows,
    }


def build_public_readonly_useful_task_pack_summary(path: str | Path) -> dict[str, Any]:
    return summarize_useful_task_pack(load_public_readonly_useful_task_pack(path))


def read_latest_public_readonly_task_pack_run(run_root: str | Path) -> dict[str, Any]:
    run_root = Path(run_root)
    if not run_root.exists():
        return {
            "status": "unavailable",
            "rows": [],
            "detail": "No public-readonly task-pack runner manifest is available.",
            "privacy_state": "local_private",
            "export_state": "local_private",
        }
    manifest_paths = sorted(
        run_root.glob("*/manifest.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not manifest_paths:
        return {
            "status": "unavailable",
            "rows": [],
            "detail": "No public-readonly task-pack runner manifest is available.",
            "privacy_state": "local_private",
            "export_state": "local_private",
        }
    latest_path = manifest_paths[0]
    try:
        payload = json.loads(latest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReliabilityMatrixError(f"runner manifest malformed JSON: {latest_path.name}") from exc
    _validate_task_pack_run_manifest(payload)
    return _summarize_task_pack_run_manifest(payload)


def _validate_task_pack_run_manifest(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ReliabilityMatrixError("runner manifest missing object")
    missing = sorted(TASK_PACK_RUN_REQUIRED_TOP_LEVEL_FIELDS.difference(payload))
    if missing:
        raise ReliabilityMatrixError(f"runner manifest missing fields: {', '.join(missing)}")
    if payload.get("manifest_version") != TASK_PACK_RUN_MANIFEST_VERSION:
        raise ReliabilityMatrixError("runner manifest missing supported manifest_version")
    if (
        payload.get("privacy_state") != "local_private"
        or payload.get("export_state") != "local_private"
    ):
        raise ReliabilityMatrixError("runner manifest must remain local/private")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ReliabilityMatrixError("runner manifest missing rows")
    if not isinstance(payload.get("outcome_counts"), dict):
        raise ReliabilityMatrixError("runner manifest missing outcome_counts")
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ReliabilityMatrixError(f"runner manifest row {index} malformed")
        row_missing = sorted(TASK_PACK_RUN_REQUIRED_ROW_FIELDS.difference(row))
        if row_missing:
            raise ReliabilityMatrixError(
                f"runner manifest missing row fields for {row.get('task_id') or index}: "
                + ", ".join(row_missing)
            )
        if not isinstance(row.get("observed_proof_summary"), dict):
            raise ReliabilityMatrixError(
                f"runner manifest missing observed proof summary for {row['task_id']}"
            )
        if not isinstance(row.get("completion_criteria_summary"), list):
            raise ReliabilityMatrixError(
                f"runner manifest missing completion criteria summary for {row['task_id']}"
            )
        if not isinstance(row.get("unmet_criteria"), list):
            raise ReliabilityMatrixError(
                f"runner manifest missing unmet criteria for {row['task_id']}"
            )
        if (
            row.get("evidence_privacy_state") != "local_private"
            or row.get("export_state") != "local_private"
        ):
            raise ReliabilityMatrixError(
                f"runner manifest row {row['task_id']} must remain local/private"
            )
        if row.get("outcome") == PublicTaskCompletionState.COMPLETED.value:
            observed_proof = row.get("observed_proof_summary")
            missing_proof = [
                proof
                for proof in row["completion_criteria_summary"]
                if proof not in observed_proof
            ]
            if missing_proof:
                raise ReliabilityMatrixError(
                    f"completed runner row missing observed proof for {row['task_id']}: "
                    + ", ".join(missing_proof)
                )
    _scan_task_pack_run_private_markers(payload)


def _summarize_task_pack_run_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    rows = [
        {
            key: row.get(key)
            for key in sorted(TASK_PACK_RUN_REQUIRED_ROW_FIELDS)
            if key in row
        }
        for row in payload["rows"]
    ]
    return {
        "status": "available",
        "manifest_version": payload["manifest_version"],
        "run_id": payload["run_id"],
        "runner_mode": payload["runner_mode"],
        "selected_task_count": payload["selected_task_count"],
        "selected_task_ids": list(payload.get("selected_task_ids") or []),
        "outcome_counts": dict(payload["outcome_counts"]),
        "privacy_state": payload["privacy_state"],
        "sanitizer_status": payload["sanitizer_status"],
        "export_state": payload["export_state"],
        "finished_at": payload["finished_at"],
        "live_network_attempted": bool(payload.get("live_network_attempted")),
        "artifact_policy": "raw_public_runtime_artifacts_remain_local_private",
        "limitation_notes": list(payload.get("limitation_notes") or []),
        "rows": rows,
    }


def _scan_task_pack_run_private_markers(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key not in {"cookies_reused", "storage_state_reused"}:
                _scan_task_pack_run_private_markers(str(key))
            _scan_task_pack_run_private_markers(item)
    elif isinstance(value, list):
        for item in value:
            _scan_task_pack_run_private_markers(item)
    elif isinstance(value, str):
        lowered = value.lower()
        for marker in TASK_PACK_RUN_PRIVATE_MARKERS:
            if marker.lower() in lowered:
                raise ReliabilityMatrixError(f"runner manifest private marker detected: {marker}")


def build_public_readonly_reliability_row(
    *,
    task_id: str,
    target_label: str,
    target_class: str,
    task_kind: str,
    completion_criteria_id: str,
    completion_criteria_summary: list[str],
    outcome: PublicTaskCompletionState | str,
    final_status: ExecutionStatus | str,
    observed_proof_summary: dict[str, Any] | None = None,
    unmet_criteria: list[str] | None = None,
    stop_or_failure_reason: str | None = None,
    evidence_privacy_state: EvidencePrivacyState | str = EvidencePrivacyState.LOCAL_PRIVATE,
    sanitizer_status: SanitizerStatus | str = SanitizerStatus.PENDING,
    visible_result_state: str = "not_captured",
    export_state: str = "local_private",
    regression_coverage: list[str] | None = None,
) -> PublicReadonlyReliabilityMatrixRow:
    return PublicReadonlyReliabilityMatrixRow(
        task_id=task_id,
        target_label=target_label,
        target_class=target_class,
        task_kind=task_kind,
        completion_criteria_id=completion_criteria_id,
        completion_criteria_summary=completion_criteria_summary,
        outcome=PublicTaskCompletionState(outcome),
        final_status=final_status.value if isinstance(final_status, ExecutionStatus) else str(final_status),
        observed_proof_summary=observed_proof_summary or {},
        unmet_criteria=unmet_criteria or [],
        stop_or_failure_reason=stop_or_failure_reason,
        evidence_privacy_state=EvidencePrivacyState(evidence_privacy_state),
        sanitizer_status=SanitizerStatus(sanitizer_status),
        visible_result_state=visible_result_state,
        export_state=export_state,
        regression_coverage=regression_coverage or [],
    )


class PublicReadonlyPolicy:
    def __init__(self, config: PublicReadonlyRoutingConfig):
        self.config = config

    @property
    def max_steps(self) -> int:
        return self.config.max_steps

    def check_url(self, url: str | None) -> PublicReadonlyPolicyDecision:
        if not url:
            return PublicReadonlyPolicyDecision(allowed=False, reason="missing_public_target")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return PublicReadonlyPolicyDecision(allowed=False, reason="unsafe_protocol")
        if parsed.username or parsed.password:
            return PublicReadonlyPolicyDecision(allowed=False, reason="credentialed_url")
        host = (parsed.hostname or "").lower()
        if not host:
            return PublicReadonlyPolicyDecision(allowed=False, reason="missing_public_host")
        if _is_private_host(host):
            return PublicReadonlyPolicyDecision(allowed=False, reason="private_network_target")
        if not any(_url_matches_target(url, target) for target in self.config.targets):
            return PublicReadonlyPolicyDecision(allowed=False, reason="target_not_allowlisted")
        return PublicReadonlyPolicyDecision(allowed=True, reason="allowlisted_public_target")

    def check_action(self, action_type: str, description: str = "") -> PublicReadonlyPolicyDecision:
        action = action_type.lower()
        haystack = f"{action} {description}".lower()
        mutation_markers = (
            "submit",
            "login",
            "sign in",
            "checkout",
            "payment",
            "purchase",
            "delete",
            "post",
            "publish",
            "upload",
            "download",
            "password",
            "credential",
            "private data",
            "提交",
            "登录",
            "上传",
            "下载",
            "付款",
            "发布",
        )
        if any(marker in haystack for marker in mutation_markers):
            return PublicReadonlyPolicyDecision(allowed=False, reason="mutation_action_blocked")
        allowed_actions = {"navigate", "search", "filter", "expand", "extract", "inspect", "observe", "read"}
        if action == "click" and any(marker in haystack for marker in ("expand", "navigation", "read-only")):
            return PublicReadonlyPolicyDecision(allowed=True, reason="readonly_action_allowed")
        if action not in allowed_actions:
            return PublicReadonlyPolicyDecision(allowed=False, reason="action_not_readonly")
        return PublicReadonlyPolicyDecision(allowed=True, reason="readonly_action_allowed")

    def check_browser_state(self, state: dict[str, object]) -> PublicReadonlyPolicyDecision:
        url = str(state.get("url") or "")
        if url:
            url_decision = self.check_url(url)
            if not url_decision.allowed:
                return url_decision
        haystack = " ".join(
            str(state.get(key, ""))
            for key in ("url", "title", "visible_text", "page_title")
        ).lower()
        checks = [
            ("file_transfer", ("upload", "download", "上传", "下载")),
            (
                "public_task_captcha_or_verification",
                (
                    "captcha",
                    "verify you are human",
                    "verification",
                    "are you a human",
                    "human verification",
                ),
            ),
            (
                "public_task_rate_limited",
                ("rate limit", "rate-limited", "abuse detection", "secondary rate limit"),
            ),
            (
                "public_task_private_or_permission_boundary",
                ("private repository", "permission denied", "access denied"),
            ),
            (
                "public_task_login_boundary",
                ("sign in to github", "you must be logged in", "login to github"),
            ),
            ("login_required", ("login", "log in", "登录", "账号", "密码")),
            ("payment_or_checkout", ("checkout", "payment", "pay", "结账", "付款", "支付")),
            ("deletion", ("delete", "删除", "remove account")),
            ("posting", ("post", "publish", "发布", "发送")),
            ("private_data_entry", ("address", "身份证", "手机号", "private")),
            ("irreversible_submit", ("submit", "提交", "confirm", "确认")),
        ]
        for reason, keywords in checks:
            if any(keyword in haystack for keyword in keywords):
                return PublicReadonlyPolicyDecision(allowed=False, reason=reason)
        return PublicReadonlyPolicyDecision(allowed=True, reason="browser_state_safe")


class PublicTaskCompletionVerifier:
    def __init__(self, contract: PublicTaskContract):
        self.contract = contract

    def verify(
        self,
        *,
        requested_slots: dict[str, Any],
        actions: list[dict[str, Any]],
    ) -> PublicTaskCompletionResult:
        observed = self._observed_proof(requested_slots, actions)
        unmet = [
            proof
            for proof in self.contract.completion_criteria.required_proof
            if proof not in observed
        ]
        if not unmet:
            return PublicTaskCompletionResult(
                completion_state=PublicTaskCompletionState.COMPLETED,
                observed_proof=observed,
                unmet_criteria=[],
            )
        return PublicTaskCompletionResult(
            completion_state=PublicTaskCompletionState.PARTIAL if actions else PublicTaskCompletionState.FAILED,
            observed_proof=observed,
            unmet_criteria=unmet,
            stop_reason="missing_public_task_completion" if actions else None,
            failure_reason=None if actions else "public_readonly_missing_evidence",
        )

    def classify_variance(self, reason: str) -> PublicTaskCompletionResult:
        mapping = {
            "timeout": (PublicTaskCompletionState.FAILED, None, "public_task_timeout"),
            "missing_selector": (PublicTaskCompletionState.PARTIAL, "public_task_missing_selector", None),
            "redirect_off_allowlist": (PublicTaskCompletionState.STOPPED, "target_not_allowlisted", None),
            "captcha": (
                PublicTaskCompletionState.STOPPED,
                "public_task_captcha_or_verification",
                None,
            ),
            "verification": (
                PublicTaskCompletionState.STOPPED,
                "public_task_captcha_or_verification",
                None,
            ),
            "login_required": (PublicTaskCompletionState.STOPPED, "login_required", None),
            "github_login_required": (
                PublicTaskCompletionState.STOPPED,
                "public_task_login_boundary",
                None,
            ),
            "rate_limited": (PublicTaskCompletionState.STOPPED, "public_task_rate_limited", None),
            "permission": (
                PublicTaskCompletionState.STOPPED,
                "public_task_private_or_permission_boundary",
                None,
            ),
            "network_error": (PublicTaskCompletionState.FAILED, None, "public_task_network_error"),
            "step_budget_exhausted": (
                PublicTaskCompletionState.PARTIAL,
                "public_readonly_step_budget_reached",
                None,
            ),
        }
        state, stop_reason, failure_reason = mapping.get(
            reason,
            (PublicTaskCompletionState.FAILED, None, f"public_task_{reason}"),
        )
        return PublicTaskCompletionResult(
            completion_state=state,
            unmet_criteria=list(self.contract.completion_criteria.required_proof),
            stop_reason=stop_reason,
            failure_reason=failure_reason,
        )

    def classify_blocked(self, reason: str) -> PublicTaskCompletionResult:
        return PublicTaskCompletionResult(
            completion_state=PublicTaskCompletionState.BLOCKED,
            unmet_criteria=list(self.contract.completion_criteria.required_proof),
            stop_reason=reason,
        )

    def _observed_proof(
        self,
        requested_slots: dict[str, Any],
        actions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        observed: dict[str, Any] = {}
        combined_parts: list[str] = []
        visible_parts: list[str] = []
        for action in actions:
            state = action.get("browser_state", {})
            state = state if isinstance(state, dict) else {}
            visible_parts.extend(
                [
                    str(state.get("page_title", "")),
                    str(state.get("title", "")),
                    str(state.get("visible_text", "")),
                ]
            )
            combined_parts.extend(
                [
                    str(action.get("type", "")),
                    str(action.get("description", "")),
                    str(state.get("page_title", "")),
                    str(state.get("visible_text", "")),
                    str(state.get("url", "")),
                ]
            )
        combined = " ".join(combined_parts).lower()
        visible_combined = " ".join(visible_parts).lower()
        query = str(requested_slots.get("search_query") or "").strip()
        if query and query.lower() in combined and any(action.get("type") == "search" for action in actions):
            observed["searched_query"] = query
        final_state = _last_browser_state(actions)
        title = str(final_state.get("page_title") or final_state.get("title") or "")
        expected_title = self.contract.completion_criteria.title_contains
        if title and (not expected_title or expected_title.lower() in title.lower()):
            observed["final_title"] = title
        url = str(final_state.get("url") or "")
        parsed = urlparse(url)
        path = parsed.path if parsed.scheme else ""
        expected_path = self.contract.completion_criteria.url_path_contains
        if path and (not expected_path or expected_path in path):
            observed["url_path"] = path
        markers = []
        for marker in self.contract.completion_criteria.visible_markers:
            try:
                markers.append(
                    marker.format(**{key: str(value) for key, value in requested_slots.items()})
                )
            except KeyError:
                continue
        if markers and any(marker.lower() in visible_combined for marker in markers):
            visible_marker = next(
                marker for marker in markers if marker.lower() in visible_combined
            )
            observed["result_heading"] = visible_marker
            observed["visible_marker"] = visible_marker
        if self.contract.task_kind == "github-repo-search":
            _observe_github_search(
                observed=observed,
                requested_slots=requested_slots,
                final_state=final_state,
                visible_combined=visible_combined,
            )
        if self.contract.task_kind == "github-public-repo-read":
            _observe_github_repo_read(
                observed=observed,
                requested_slots=requested_slots,
                final_state=final_state,
                combined=combined,
            )
        return observed


def parse_public_readonly_targets(config: RuntimeConfig) -> list[PublicReadonlyTarget]:
    entries = [
        entry.strip()
        for chunk in config.public_readonly_allowlist.splitlines()
        for entry in chunk.split(";")
        if entry.strip()
    ]
    targets: list[PublicReadonlyTarget] = []
    for entry in entries:
        parts = [part.strip() for part in entry.split("|")]
        if len(parts) < 3:
            continue
        allowlist_id, label, url = parts[:3]
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        origin = f"{parsed.scheme}://{parsed.netloc.lower()}"
        keywords = (
            [item.strip().lower() for item in parts[3].split(",") if item.strip()]
            if len(parts) > 3
            else _default_keywords(allowlist_id, label, url)
        )
        task_contracts = _parse_task_contracts(
            raw_contracts=parts[4:] if len(parts) > 4 else [],
            allowlist_id=allowlist_id,
        )
        targets.append(
            PublicReadonlyTarget(
                allowlist_id=allowlist_id,
                label=label,
                url=url,
                origin=origin,
                keywords=keywords,
                task_contracts=task_contracts,
            )
        )
    return targets


def match_public_readonly_task(
    request: BrowserTaskRequest,
    config: PublicReadonlyRoutingConfig,
) -> tuple[PublicReadonlyTarget, PublicTaskContract, dict[str, Any]] | None:
    target = match_public_readonly_target(request, config)
    if target is None:
        return None
    slots = normalized_public_task_slots(request)
    for contract in target.task_contracts:
        if _contract_matches_request(contract, request, slots):
            return target, contract, slots
    return None


def match_public_readonly_target(
    request: BrowserTaskRequest,
    config: PublicReadonlyRoutingConfig,
) -> PublicReadonlyTarget | None:
    text = _command_text(request)
    explicit_urls = _extract_urls(text)
    if explicit_urls:
        matched_target: PublicReadonlyTarget | None = None
        for url in explicit_urls:
            matches = [target for target in config.targets if _url_matches_target(url, target)]
            if not matches:
                return None
            if matched_target is None:
                matched_target = matches[0]
            elif matches[0].allowlist_id != matched_target.allowlist_id:
                return None
        return matched_target
    scored_targets = [
        (sum(1 for keyword in target.keywords if keyword and keyword in text), target)
        for target in config.targets
    ]
    scored_targets = [(score, target) for score, target in scored_targets if score > 0]
    if scored_targets:
        return max(scored_targets, key=lambda item: item[0])[1]
    return None


def request_looks_public(request: BrowserTaskRequest) -> bool:
    text = _command_text(request)
    return any(marker in text for marker in PUBLIC_TARGET_MARKERS)


def has_transcript_url(request: BrowserTaskRequest) -> bool:
    return bool(_extract_urls(_command_text(request)))


def rejected_public_url_reason(
    request: BrowserTaskRequest,
    config: PublicReadonlyRoutingConfig,
) -> str | None:
    urls = _extract_urls(_command_text(request))
    if not urls:
        return None
    policy = PublicReadonlyPolicy(config)
    for url in urls:
        decision = policy.check_url(url)
        if not decision.allowed:
            return decision.reason
    return None


def normalized_public_task_slots(request: BrowserTaskRequest) -> dict[str, Any]:
    slots = dict(request.public_task_slots)
    text = _command_text(request)
    mentions_docs = "doc" in text or "文档" in text
    if "target_site_hint" not in slots:
        if "python" in text and mentions_docs:
            slots["target_site_hint"] = "python docs"
        elif "openai" in text and mentions_docs:
            slots["target_site_hint"] = "openai docs"
        elif "mdn" in text:
            slots["target_site_hint"] = "mdn"
    elif "wikipedia" in text:
        slots["target_site_hint"] = "wikipedia"
    elif "github" in text:
        slots["target_site_hint"] = "github"
    elif "pypi" in text:
        slots["target_site_hint"] = "pypi"
    elif "npm" in text:
        slots["target_site_hint"] = "npm"
    package_name = _extract_package_name(text)
    if package_name:
        ecosystem = "pypi" if "pypi" in text else "npm" if "npm" in text else "package"
        slots["target_site_hint"] = ecosystem
        slots["task_category"] = "package_metadata"
        slots["package_ecosystem"] = ecosystem
        slots["package_name"] = package_name
    if "search_query" not in slots:
        query = _extract_search_query(text)
        if query:
            slots["search_query"] = query
            if "github" in text:
                slots["task_kind_hint"] = "github-repo-search"
    if "github" in text and not {"owner", "repo"}.issubset(slots):
        repo_slug = _extract_github_repo_slug(text)
        if repo_slug:
            owner, repo = repo_slug.split("/", 1)
            slots["target_site_hint"] = "github"
            slots["task_kind_hint"] = "github-public-repo-read"
            slots["repo_slug"] = repo_slug
            slots["owner"] = owner
            slots["repo"] = repo
    release_target = _extract_release_target(text)
    if release_target:
        owner, repo = release_target.split("/", 1)
        slots["target_site_hint"] = "github"
        slots["task_category"] = "release_notes"
        slots["task_kind_hint"] = "release_notes_read"
        slots["release_target"] = release_target
        slots["repo_slug"] = release_target
        slots["owner"] = owner
        slots["repo"] = repo
    if "read_only_intent" not in slots and request.safety_flags == []:
        slots["read_only_intent"] = True
    return slots


def public_readonly_readiness(config: RuntimeConfig) -> dict[str, object]:
    targets = parse_public_readonly_targets(config)
    task_contract_count = sum(len(target.task_contracts) for target in targets)
    if not config.public_readonly_enabled:
        status = "disabled"
        detail = "Public-readonly execution is disabled by default."
    elif not targets:
        status = "missing_allowlist"
        detail = "Set VOICE_BROWSER_PUBLIC_READONLY_ALLOWLIST before live public execution."
    elif task_contract_count == 0:
        status = "missing_task_contracts"
        detail = "Configured public-readonly targets need explicit public task contracts."
    else:
        status = "ready"
        detail = "Public-readonly execution is enabled for configured allowlist targets."
    return {
        "status": status,
        "enabled": config.public_readonly_enabled,
        "allowlist_count": len(targets),
        "task_contract_count": task_contract_count,
        "allowlist": [{"id": target.allowlist_id, "label": target.label} for target in targets],
        "max_steps": config.public_readonly_max_steps,
        "timeout_seconds": config.public_readonly_timeout_seconds,
        "private_traces": config.public_readonly_private_traces,
        "browser_isolation": {
            "status": "ready",
            "detail": "Uses a fresh ephemeral Playwright context per public-readonly run.",
        },
        "sanitizer": {
            "status": "required" if config.public_readonly_sanitizer_required else "optional",
            "detail": "Public-readonly traces remain local/private until sanitizer approval.",
        },
        "detail": detail,
    }


def public_target_class_for_contract(
    target: PublicReadonlyTarget | None,
    contract: PublicTaskContract | None,
) -> str:
    if contract is not None and contract.target_class:
        return contract.target_class
    allowlist_id = (target.allowlist_id if target else "").lower()
    label = (target.label if target else "").lower()
    task_kind = (contract.task_kind if contract else "").lower()
    if "github" in allowlist_id or "github" in label or "repo" in task_kind:
        return "public_repository"
    if "package" in task_kind or "pypi" in allowlist_id or "npm" in allowlist_id:
        return "package_metadata"
    if "release" in task_kind:
        return "release_notes"
    if "mdn" in allowlist_id or "wikipedia" in allowlist_id or "reference" in task_kind:
        return "reference"
    return "documentation"


def public_task_category_for_contract(
    target: PublicReadonlyTarget | None,
    contract: PublicTaskContract | None,
) -> str | None:
    if contract is None:
        return None
    if contract.task_category:
        return contract.task_category
    task_kind = contract.task_kind.lower()
    target_class = public_target_class_for_contract(target, contract)
    if "github-repo-search" in task_kind:
        return "public_repository_search"
    if "github-public-repo-read" in task_kind:
        return "public_repository_read"
    if "release" in task_kind:
        return "release_notes"
    if "package" in task_kind:
        return "package_metadata"
    return target_class


def public_completion_criteria_summary(contract: PublicTaskContract | None) -> list[str]:
    if contract is None:
        return []
    return list(contract.completion_criteria.required_proof)


def public_evidence_export_state(
    privacy_state: EvidencePrivacyState,
    sanitizer_status: SanitizerStatus,
) -> str:
    if privacy_state is EvidencePrivacyState.PUBLIC_SAFE and sanitizer_status is SanitizerStatus.PASSED:
        return "public_safe"
    if sanitizer_status is SanitizerStatus.FAILED:
        return "sanitizer_failed"
    if sanitizer_status is SanitizerStatus.PENDING:
        return "sanitizer_pending" if privacy_state is EvidencePrivacyState.PUBLIC_SAFE else "local_private"
    return "local_private" if privacy_state is EvidencePrivacyState.LOCAL_PRIVATE else "not_applicable"


def _request_text(request: BrowserTaskRequest) -> str:
    parts = [request.task, request.intent_type.value]
    parts.extend(request.constraints)
    parts.extend(request.safety_flags)
    parts.extend(ref.text for ref in request.visual_references)
    return " ".join(parts).lower()


def _command_text(request: BrowserTaskRequest) -> str:
    parts = [request.task]
    parts.extend(ref.text for ref in request.visual_references)
    return " ".join(parts).lower()


def _extract_urls(text: str) -> list[str]:
    return re.findall(r"(?:https?|file|data|javascript):[^\s，。；;]+", text)


def _extract_package_name(text: str) -> str | None:
    if "package" not in text and "pypi" not in text and "npm" not in text:
        return None
    patterns = (
        r"(?:pypi|npm)\s+package\s+metadata\s+for\s+([a-z0-9_.@/\-]+)",
        r"(?:package\s+metadata\s+for|metadata\s+for)\s+([a-z0-9_.@/\-]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip(".,")
    return None


def _extract_release_target(text: str) -> str | None:
    if "release" not in text and "releases" not in text:
        return None
    match = re.search(r"\b([a-z0-9_.-]+)/([a-z0-9_.-]+)\b", text, flags=re.IGNORECASE)
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2).removesuffix('.git')}"


def _parse_task_contracts(
    *,
    raw_contracts: list[str],
    allowlist_id: str,
) -> list[PublicTaskContract]:
    contracts: list[PublicTaskContract] = []
    for raw in raw_contracts:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payload.setdefault("allowlist_id", allowlist_id)
            contracts.append(PublicTaskContract.model_validate(payload))
        elif isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    item.setdefault("allowlist_id", allowlist_id)
                    contracts.append(PublicTaskContract.model_validate(item))
    return contracts


def _contract_matches_request(
    contract: PublicTaskContract,
    request: BrowserTaskRequest,
    slots: dict[str, Any],
) -> bool:
    if any(slot not in slots for slot in contract.slots):
        return False
    if contract.task_kind == "documentation_search":
        return bool(slots.get("search_query"))
    if contract.task_kind == "github-repo-search":
        return (
            _slot_matches_github(slots)
            and bool(slots.get("search_query"))
            and slots.get("task_kind_hint", "github-repo-search") == "github-repo-search"
        )
    if contract.task_kind == "github-public-repo-read":
        has_repo = bool(slots.get("owner") and slots.get("repo")) or bool(slots.get("repo_slug"))
        return (
            _slot_matches_github(slots)
            and has_repo
            and slots.get("task_kind_hint", "github-public-repo-read") == "github-public-repo-read"
        )
    if contract.task_kind in {"direct_reference_read", "visible_extraction"}:
        return bool(
            slots.get("read_target")
            or slots.get("extraction_target")
            or all(slot in slots for slot in contract.slots)
        )
    return request.intent_type.value in contract.task_kind or bool(slots)


def _extract_search_query(text: str) -> str | None:
    patterns = (
        r"(?:search|look up|find)\s+(?:(?:python|openai|mdn|wikipedia)\s+)?(?:docs?|documentation)?\s*for\s+([^,\n.]+)",
        r"(?:search|look up|find)\s+(?:[^.\n]*?\s+)?(?:for\s+)?([a-z0-9_.\- ]+?)(?:,|\.|\n|$)",
        r"(?:搜索|查找|查询)\s*([^，。；\n|]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            query = re.sub(r"\s+(?:do not log in|without login)$", "", query, flags=re.IGNORECASE)
            words = query.split()
            if len(words) > 1 and words[0] in {"python", "docs", "documentation"}:
                query = words[-1]
            query = _clean_github_search_query(query)
            return query[:80] if query else None
    return None


def _clean_github_search_query(query: str) -> str:
    return re.sub(
        r"^(?:github\s+)?(?:repositories|repository|repos|repo)\s+for\s+",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()


def _extract_github_repo_slug(text: str) -> str | None:
    if "github" not in text and "github.com/" not in text:
        return None
    url_match = re.search(
        r"github\.com/([a-z0-9_.-]+)/([a-z0-9_.-]+)",
        text,
        flags=re.IGNORECASE,
    )
    if url_match:
        return f"{url_match.group(1)}/{url_match.group(2).removesuffix('.git')}"
    match = re.search(r"\b([a-z0-9_.-]+)/([a-z0-9_.-]+)\b", text, flags=re.IGNORECASE)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2).removesuffix(".git")
    if owner in {"http:", "https:"}:
        return None
    return f"{owner}/{repo}"


def _slot_matches_github(slots: dict[str, Any]) -> bool:
    return str(slots.get("target_site_hint") or "").lower() in {"github", "github.com"}


def _observe_github_search(
    *,
    observed: dict[str, Any],
    requested_slots: dict[str, Any],
    final_state: dict[str, Any],
    visible_combined: str,
) -> None:
    query = str(requested_slots.get("search_query") or "").strip()
    url = str(final_state.get("url") or "")
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    searched = unquote_plus(" ".join(query_params.get("q", []))).strip()
    if parsed.hostname == "github.com" and parsed.path.startswith("/search"):
        observed["search_page_state"] = "github_repository_search"
    if query and (query.lower() == searched.lower() or query.lower() in visible_combined):
        observed["searched_query"] = query
    if _github_repository_results_visible(visible_combined):
        observed["repository_result_marker"] = "Repositories"


def _github_repository_results_visible(visible_combined: str) -> bool:
    return bool(
        re.search(r"\brepositories\b", visible_combined)
        or re.search(r"\brepository\s+results?\b", visible_combined)
    )


def _observe_github_repo_read(
    *,
    observed: dict[str, Any],
    requested_slots: dict[str, Any],
    final_state: dict[str, Any],
    combined: str,
) -> None:
    owner = str(requested_slots.get("owner") or "").strip()
    repo = str(requested_slots.get("repo") or "").strip()
    repo_slug = str(requested_slots.get("repo_slug") or f"{owner}/{repo}").strip("/")
    url = str(final_state.get("url") or "")
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) >= 2:
        observed_slug = f"{path_parts[0]}/{path_parts[1]}"
        if not repo_slug or observed_slug.lower() == repo_slug.lower():
            observed["repo_slug"] = repo_slug or observed_slug
    title = str(final_state.get("page_title") or final_state.get("title") or "")
    if repo and repo.lower() in title.lower():
        observed["repo_page_title"] = title
    for marker in ("README", "About", "Code"):
        if marker.lower() in combined:
            observed["readme_or_description_marker"] = marker
            break


def _last_browser_state(actions: list[dict[str, Any]]) -> dict[str, Any]:
    for action in reversed(actions):
        state = action.get("browser_state")
        if isinstance(state, dict):
            return state
    return {}


def _default_keywords(allowlist_id: str, label: str, url: str) -> list[str]:
    parsed = urlparse(url)
    host_parts = [part for part in (parsed.hostname or "").split(".") if part and part not in {"www", "com", "org"}]
    raw = re.split(r"[\s_\-/]+", f"{allowlist_id} {label}".lower())
    return sorted(set([item for item in raw + host_parts if item and len(item) > 2]))


def _url_matches_target(url: str, target: PublicReadonlyTarget) -> bool:
    parsed = urlparse(url)
    target_parsed = urlparse(target.url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if (parsed.hostname or "").lower() != (target_parsed.hostname or "").lower():
        return False
    target_path = target_parsed.path.rstrip("/")
    candidate_path = parsed.path.rstrip("/")
    return not target_path or candidate_path.startswith(target_path)


def _is_private_host(host: str) -> bool:
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
