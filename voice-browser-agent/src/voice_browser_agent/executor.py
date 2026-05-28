from __future__ import annotations

from contextlib import suppress
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field, model_serializer

from .models import (
    AgenticVisionStep,
    BrowserActionEvent,
    BrowserStateStop,
    BrowserTaskRequest,
    EvidencePrivacyState,
    ExecutionMode,
    ExecutionStatus,
    PublicTaskCompletionState,
    PublicTaskContract,
    PublicReadonlyVisualArtifact,
    SanitizerStatus,
)
from .public_readonly import (
    PublicTaskCompletionVerifier,
    PublicReadonlyPolicy,
    PublicReadonlyPolicyDecision,
    PublicReadonlyRoutingConfig,
    build_public_readonly_reliability_row,
    public_completion_criteria_summary,
    public_evidence_export_state,
    public_target_class_for_contract,
)
from .safety import detect_browser_state_stop


class BrowserExecutorConfig(BaseModel):
    local_browser: bool = True
    remote_vision_backend_url: str | None = None
    dry_run: bool = True
    execution_mode: ExecutionMode | None = None
    browser_channel: str = "chromium"
    max_steps: int = 8
    max_recoveries: int = 1
    agentic_execution: bool = False
    controlled_fixture_id: str | None = None
    controlled_target_ref: str | None = None
    controlled_target_url: str | None = None
    public_target_url: str | None = None
    public_target_label: str | None = None
    public_target_class: str | None = None
    public_origin: str | None = None
    public_allowlist_id: str | None = None
    public_task_contract: PublicTaskContract | dict[str, Any] | None = None
    public_task_slots: dict[str, Any] = Field(default_factory=dict)
    public_timeout_seconds: int = 15
    public_sanitizer_required: bool = True
    public_visual_artifacts_dir: Path | None = None
    public_headed_debug: bool = False

    def resolved_execution_mode(self) -> ExecutionMode:
        if self.execution_mode is not None:
            return self.execution_mode
        return ExecutionMode.DEMO_PREVIEW if self.dry_run else ExecutionMode.LIVE_CONTROLLED


class BrowserExecutionResult(BaseModel):
    execution_id: str
    execution_mode: ExecutionMode
    final_status: ExecutionStatus
    actions: list[BrowserActionEvent] = Field(default_factory=list)
    agentic_steps: list[AgenticVisionStep] = Field(default_factory=list)
    grounding_evidence_refs: list[str] = Field(default_factory=list)
    failure_reason: str | None = None
    stop_reason: str | None = None
    agent_task: str
    runtime: dict[str, Any] = Field(default_factory=dict)

    @model_serializer(mode="wrap")
    def _serialize_public_safe(self, handler):
        payload = handler(self)
        if self.execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY:
            from .trace_writer import sanitize_trace_dict

            return sanitize_trace_dict(payload)
        return payload


@dataclass
class BrowserExecutorAdapter:
    config: BrowserExecutorConfig
    agent_factory: Callable[..., Any] | None = None
    agentic_adapter_factory: Callable[..., Any] | None = None

    async def execute(self, request: BrowserTaskRequest, execution_id: str) -> BrowserExecutionResult:
        execution_mode = self.config.resolved_execution_mode()
        agent_task = self._build_agent_task(request)
        runtime = {
            "execution_mode": execution_mode.value,
            "local_browser": self.config.local_browser,
            "remote_vision_backend_url": self.config.remote_vision_backend_url,
            "browser_channel": self.config.browser_channel,
            "max_steps": self.config.max_steps,
            "max_recoveries": self.config.max_recoveries,
            "agentic_execution": self.config.agentic_execution,
            "controlled_fixture_id": self.config.controlled_fixture_id,
            "controlled_target_ref": self.config.controlled_target_ref or request.controlled_target_ref,
            "controlled_target_url": self.config.controlled_target_url,
            "visual_grounding_dependency": "browser-use-vision",
        }
        public_policy: PublicReadonlyPolicy | None = None
        if execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY:
            public_policy = self._public_readonly_policy()
            runtime.update(
                {
                    "public_target_label": self.config.public_target_label,
                    "public_target_class": self.config.public_target_class,
                    "public_origin": self.config.public_origin,
                    "public_allowlist_id": self.config.public_allowlist_id,
                    "public_task_slots": self.config.public_task_slots or request.public_task_slots,
                    "evidence_privacy_state": EvidencePrivacyState.LOCAL_PRIVATE.value,
                    "sanitizer_status": (
                        SanitizerStatus.PENDING.value
                        if self.config.public_sanitizer_required
                        else SanitizerStatus.NOT_REQUIRED.value
                    ),
                    "execution_limits": {
                        "max_steps": self.config.max_steps,
                        "timeout_seconds": self.config.public_timeout_seconds,
                    },
                    "browser_context": {
                        "isolation": "fresh_ephemeral",
                        "persistent_profile": False,
                        "cookies_reused": False,
                        "storage_state_reused": False,
                        "headed_debug": self.config.public_headed_debug,
                    },
                }
            )
            public_contract = self._public_task_contract(request)
            if public_contract is None:
                runtime.update(
                    {
                        "public_task_completion": {
                            "completion_state": PublicTaskCompletionState.BLOCKED.value,
                            "observed_proof": {},
                            "unmet_criteria": [],
                            "stop_reason": "public_task_contract_mismatch",
                            "failure_reason": None,
                        },
                        "public_completion_state": PublicTaskCompletionState.BLOCKED.value,
                        "public_observed_proof_summary": {},
                        "public_unmet_criteria": [],
                    }
                )
                return BrowserExecutionResult(
                    execution_id=execution_id,
                    execution_mode=execution_mode,
                    final_status=ExecutionStatus.BLOCKED,
                    actions=[],
                    stop_reason="public_task_contract_mismatch",
                    agent_task=agent_task,
                    runtime=runtime,
                )
            runtime.update(
                {
                    "public_task_id": public_contract.task_id,
                    "public_task_kind": public_contract.task_kind,
                    "public_completion_criteria_id": public_contract.completion_criteria.criteria_id,
                    "public_completion_criteria_summary": public_completion_criteria_summary(public_contract),
                    "public_matrix_eligible": True,
                    "public_evidence_export_state": public_evidence_export_state(
                        EvidencePrivacyState.LOCAL_PRIVATE,
                        SanitizerStatus.PENDING
                        if self.config.public_sanitizer_required
                        else SanitizerStatus.NOT_REQUIRED,
                    ),
                    "public_target_class": self.config.public_target_class
                    or _public_target_class_for_runtime(public_contract, self.config.public_allowlist_id),
                    "public_task_contract": public_contract.model_dump(mode="json"),
                }
            )
            url_decision = public_policy.check_url(self.config.public_target_url)
            if not url_decision.allowed:
                _record_public_blocked_completion(runtime, public_contract, url_decision.reason)
                _attach_public_reliability_matrix_row(
                    runtime=runtime,
                    final_status=ExecutionStatus.BLOCKED,
                    stop_reason=url_decision.reason,
                    failure_reason=None,
                )
                return BrowserExecutionResult(
                    execution_id=execution_id,
                    execution_mode=execution_mode,
                    final_status=ExecutionStatus.BLOCKED,
                    actions=[],
                    failure_reason=None,
                    stop_reason=url_decision.reason,
                    agent_task=agent_task,
                    runtime=runtime,
                )

        if self.config.dry_run:
            action = BrowserActionEvent(
                action_type="demo_preview",
                description=f"prepared bounded browser task without live browser execution: {request.task}",
                grounding_evidence_refs=[
                    ref.text for ref in request.visual_references if ref.text
                ],
            )
            return BrowserExecutionResult(
                execution_id=execution_id,
                execution_mode=execution_mode,
                final_status=ExecutionStatus.STOPPED,
                actions=[action],
                grounding_evidence_refs=action.grounding_evidence_refs,
                stop_reason="demo_preview_not_executed",
                agent_task=agent_task,
                runtime=runtime,
            )

        if execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY:
            factory = self.agent_factory or PublicReadonlyBrowserAgent
            agent = factory(
                task=agent_task,
                runtime=runtime,
                vision_backend_url=self.config.remote_vision_backend_url,
                target_url=self.config.public_target_url,
                timeout_seconds=self.config.public_timeout_seconds,
                policy=public_policy,
                execution_id=execution_id,
                visual_artifacts_dir=self.config.public_visual_artifacts_dir,
                headed_debug=self.config.public_headed_debug,
            )
            raw_result = await agent.run()
            return self._coerce_result(
                execution_id,
                execution_mode,
                agent_task,
                runtime,
                raw_result,
                public_policy=public_policy,
            )

        if self.config.agentic_execution:
            from .agentic import AgenticVisionExecutor, ControlledAgenticVisionAdapter

            adapter_factory = self.agentic_adapter_factory or ControlledAgenticVisionAdapter
            observation_adapter = adapter_factory(
                task=agent_task,
                runtime=runtime,
                vision_backend_url=self.config.remote_vision_backend_url,
            )
            return await AgenticVisionExecutor(
                config=self.config,
                observation_adapter=observation_adapter,
                agent_task=agent_task,
                runtime=runtime,
            ).execute(request, execution_id)

        factory = self.agent_factory or (
            ControlledLiveBrowserAgent
            if self.config.controlled_target_url
            else self._load_vision_enhanced_agent
        )
        agent = factory(task=agent_task, runtime=runtime, vision_backend_url=self.config.remote_vision_backend_url)
        raw_result = await agent.run()
        return self._coerce_result(execution_id, execution_mode, agent_task, runtime, raw_result)

    def _public_readonly_policy(self) -> PublicReadonlyPolicy:
        return PublicReadonlyPolicy(
            PublicReadonlyRoutingConfig.from_executor_target(
                target_url=self.config.public_target_url or "",
                target_label=self.config.public_target_label or "public target",
                public_origin=self.config.public_origin or "",
                allowlist_id=self.config.public_allowlist_id or "public-target",
                max_steps=min(self.config.max_steps, 5),
                timeout_seconds=self.config.public_timeout_seconds,
                sanitizer_required=self.config.public_sanitizer_required,
            )
        )

    def _public_task_contract(self, request: BrowserTaskRequest) -> PublicTaskContract | None:
        if self.config.public_task_contract is None:
            return None
        if isinstance(self.config.public_task_contract, PublicTaskContract):
            return self.config.public_task_contract
        return PublicTaskContract.model_validate(self.config.public_task_contract)

    def _build_agent_task(self, request: BrowserTaskRequest) -> str:
        parts = [
            request.task,
            f"intent_type={request.intent_type.value}",
            "constraints=" + "; ".join(request.constraints),
            "stop_conditions=" + "; ".join(request.stop_conditions),
        ]
        if request.visual_references:
            parts.append(
                "visual_references="
                + "; ".join(f"{ref.kind}: {ref.text}" for ref in request.visual_references)
            )
        if request.controlled_target_ref:
            parts.append(f"controlled_target_ref={request.controlled_target_ref}")
        return "\n".join(parts)

    def _load_vision_enhanced_agent(self, **kwargs):
        from browser_use_vision import VisionEnhancedAgent

        return VisionEnhancedAgent(**kwargs)

    def _coerce_result(
        self,
        execution_id: str,
        execution_mode: ExecutionMode,
        agent_task: str,
        runtime: dict[str, Any],
        raw_result: Any,
        public_policy: PublicReadonlyPolicy | None = None,
    ) -> BrowserExecutionResult:
        if isinstance(raw_result, BrowserExecutionResult):
            return raw_result
        payload = raw_result if isinstance(raw_result, dict) else {"status": "succeeded", "raw": str(raw_result)}
        status = ExecutionStatus(payload.get("status", "succeeded"))
        raw_action_items = [
            item
            for item in payload.get("actions", [])
            if isinstance(item, dict)
        ]
        actions = [
            BrowserActionEvent(
                action_type=item.get("type", "action"),
                description=item.get("description", ""),
                screenshot_ref=item.get("screenshot_ref"),
                grounding_evidence_refs=item.get("grounding_evidence_refs", []),
                browser_state=_sanitize_browser_state(item.get("browser_state", {})),
            )
            for item in raw_action_items
        ]
        budget_stop: BrowserStateStop | None = None
        if public_policy is not None and len(actions) > public_policy.max_steps:
            actions = actions[: public_policy.max_steps]
            raw_action_items = raw_action_items[: public_policy.max_steps]
            budget_stop = BrowserStateStop(
                reason="public_readonly_step_budget_reached",
                detail=f"public-readonly step budget reached at {public_policy.max_steps} steps",
            )
        grounding_refs: list[str] = []
        for action in actions:
            grounding_refs.extend(action.grounding_evidence_refs)
        grounding_refs.extend(payload.get("grounding_evidence_refs", []))
        visual_artifacts = _coerce_public_visual_artifacts(
            payload.get("visual_artifacts"),
            execution_id=execution_id,
        )
        if visual_artifacts:
            runtime["public_visual_artifacts"] = [
                artifact.model_dump(mode="json") for artifact in visual_artifacts
            ]
            final_artifact = next(
                (artifact for artifact in reversed(visual_artifacts) if artifact.is_final),
                visual_artifacts[-1],
            )
            runtime["public_final_visual_result"] = final_artifact.model_dump(mode="json")
        stop = budget_stop or _detect_stop(payload, actions, raw_action_items)
        failure_reason = payload.get("failure_reason")
        stop_reason = stop.reason if stop else payload.get("stop_reason")
        if public_policy is not None:
            public_stop = _detect_public_readonly_stop(
                public_policy,
                payload,
                actions,
                raw_action_items,
                public_task_contract=_public_task_contract_from_runtime(runtime),
            )
            stop = public_stop or stop
            stop_reason = stop.reason if stop else stop_reason
            completion = _verify_public_task_completion(runtime, raw_action_items)
            if completion is not None:
                variance_completion = _public_task_completion_from_runtime_issue(
                    runtime=runtime,
                    payload=payload,
                    observed_proof=completion.observed_proof,
                    stop_reason=stop_reason,
                    failure_reason=failure_reason,
                )
                if variance_completion is not None:
                    completion = variance_completion
                if stop is not None:
                    completion.completion_state = PublicTaskCompletionState.STOPPED
                    completion.stop_reason = stop.reason
                runtime["public_task_completion"] = completion.model_dump(mode="json")
                runtime["public_completion_state"] = completion.completion_state.value
                runtime["public_observed_proof_summary"] = completion.observed_proof
                runtime["public_unmet_criteria"] = completion.unmet_criteria
                _apply_visual_artifact_completion(runtime, completion.completion_state)
                if stop is not None:
                    status = ExecutionStatus.STOPPED
                    stop_reason = stop.reason
                elif completion.completion_state is PublicTaskCompletionState.PARTIAL:
                    status = ExecutionStatus.STOPPED
                    stop_reason = completion.stop_reason or "missing_public_task_completion"
                elif completion.completion_state is PublicTaskCompletionState.STOPPED:
                    status = ExecutionStatus.STOPPED
                    stop_reason = completion.stop_reason
                elif completion.completion_state is PublicTaskCompletionState.FAILED:
                    status = ExecutionStatus.FAILED
                    failure_reason = completion.failure_reason or "public_task_completion_failed"
                elif completion.completion_state is PublicTaskCompletionState.BLOCKED:
                    status = ExecutionStatus.BLOCKED
                    stop_reason = completion.stop_reason
        if stop is not None:
            status = ExecutionStatus.STOPPED
        if execution_mode is ExecutionMode.LIVE_CONTROLLED and not actions and not grounding_refs:
            status = ExecutionStatus.FAILED
            failure_reason = failure_reason or "live_controlled_missing_evidence"
        if (
            execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY
            and not actions
            and not grounding_refs
        ):
            status = ExecutionStatus.FAILED
            failure_reason = failure_reason or "public_readonly_missing_evidence"
        if execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY:
            _attach_public_reliability_matrix_row(
                runtime=runtime,
                final_status=status,
                stop_reason=stop_reason,
                failure_reason=failure_reason,
            )
        return BrowserExecutionResult(
            execution_id=execution_id,
            execution_mode=execution_mode,
            final_status=status,
            actions=actions,
            agentic_steps=[],
            grounding_evidence_refs=grounding_refs,
            failure_reason=failure_reason,
            stop_reason=stop_reason,
            agent_task=agent_task,
            runtime=runtime,
        )


def _coerce_public_visual_artifacts(
    value: Any,
    *,
    execution_id: str,
) -> list[PublicReadonlyVisualArtifact]:
    if not isinstance(value, list):
        return []
    artifacts: list[PublicReadonlyVisualArtifact] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        payload = dict(item)
        payload.setdefault("execution_id", execution_id)
        if payload.get("execution_id") != execution_id:
            continue
        try:
            artifacts.append(PublicReadonlyVisualArtifact.model_validate(payload))
        except Exception:
            continue
    return artifacts


def _apply_visual_artifact_completion(
    runtime: dict[str, Any],
    completion_state: PublicTaskCompletionState,
) -> None:
    artifacts = runtime.get("public_visual_artifacts")
    if not isinstance(artifacts, list):
        return
    for artifact in artifacts:
        if isinstance(artifact, dict):
            artifact["completion_state"] = completion_state.value
    final = runtime.get("public_final_visual_result")
    if isinstance(final, dict):
        final["completion_state"] = completion_state.value


def _verify_public_task_completion(
    runtime: dict[str, Any],
    raw_action_items: list[dict[str, Any]],
):
    contract = _public_task_contract_from_runtime(runtime)
    if contract is None:
        return None
    slots = runtime.get("public_task_slots")
    slots = slots if isinstance(slots, dict) else {}
    return PublicTaskCompletionVerifier(contract).verify(
        requested_slots=slots,
        actions=raw_action_items,
    )


def _public_task_contract_from_runtime(runtime: dict[str, Any]) -> PublicTaskContract | None:
    contract_payload = runtime.get("public_task_contract")
    if not isinstance(contract_payload, dict):
        return None
    return PublicTaskContract.model_validate(contract_payload)


def _public_target_class_for_runtime(
    contract: PublicTaskContract,
    allowlist_id: str | None,
) -> str:
    if contract.target_class:
        return contract.target_class
    allowlist = (allowlist_id or contract.allowlist_id).lower()
    task_kind = contract.task_kind.lower()
    if "github" in allowlist or "repo" in task_kind:
        return "public_repository"
    if "mdn" in allowlist or "wikipedia" in allowlist or "reference" in task_kind:
        return "reference"
    return "documentation"


def _attach_public_reliability_matrix_row(
    *,
    runtime: dict[str, Any],
    final_status: ExecutionStatus,
    stop_reason: str | None,
    failure_reason: str | None,
) -> None:
    completion_payload = runtime.get("public_task_completion")
    if not isinstance(completion_payload, dict):
        return
    task_id = runtime.get("public_task_id")
    task_kind = runtime.get("public_task_kind")
    criteria_id = runtime.get("public_completion_criteria_id")
    if not task_id or not task_kind or not criteria_id:
        return
    privacy_state = EvidencePrivacyState(runtime.get("evidence_privacy_state", EvidencePrivacyState.LOCAL_PRIVATE))
    sanitizer_status = SanitizerStatus(runtime.get("sanitizer_status", SanitizerStatus.PENDING))
    visible_result_state = _public_visible_result_state(runtime)
    export_state = public_evidence_export_state(privacy_state, sanitizer_status)
    runtime["public_evidence_export_state"] = export_state
    row = build_public_readonly_reliability_row(
        task_id=str(task_id),
        target_label=str(runtime.get("public_target_label") or "public target"),
        target_class=str(runtime.get("public_target_class") or "documentation"),
        task_kind=str(task_kind),
        completion_criteria_id=str(criteria_id),
        completion_criteria_summary=list(runtime.get("public_completion_criteria_summary") or []),
        outcome=completion_payload.get("completion_state", PublicTaskCompletionState.FAILED.value),
        final_status=final_status,
        observed_proof_summary=completion_payload.get("observed_proof") or {},
        unmet_criteria=completion_payload.get("unmet_criteria") or [],
        stop_or_failure_reason=(
            completion_payload.get("stop_reason")
            or completion_payload.get("failure_reason")
            or stop_reason
            or failure_reason
        ),
        evidence_privacy_state=privacy_state,
        sanitizer_status=sanitizer_status,
        visible_result_state=visible_result_state,
        export_state=export_state,
        regression_coverage=[f"{completion_payload.get('completion_state', 'unknown')}_coverage"],
    )
    runtime["public_reliability_matrix_row"] = row.model_dump(mode="json")


def _record_public_blocked_completion(
    runtime: dict[str, Any],
    contract: PublicTaskContract,
    reason: str,
) -> None:
    completion = PublicTaskCompletionVerifier(contract).classify_blocked(reason)
    runtime["public_task_completion"] = completion.model_dump(mode="json")
    runtime["public_completion_state"] = completion.completion_state.value
    runtime["public_observed_proof_summary"] = completion.observed_proof
    runtime["public_unmet_criteria"] = completion.unmet_criteria
    _apply_visual_artifact_completion(runtime, completion.completion_state)


def _public_visible_result_state(runtime: dict[str, Any]) -> str:
    final = runtime.get("public_final_visual_result")
    if not isinstance(final, dict):
        return "not_captured"
    if final.get("privacy_state") == EvidencePrivacyState.PUBLIC_SAFE.value:
        return "public_safe"
    if final.get("sanitizer_status") == SanitizerStatus.FAILED.value:
        return "sanitizer_failed"
    return "local_private"


def _public_task_completion_from_runtime_issue(
    *,
    runtime: dict[str, Any],
    payload: dict[str, Any],
    observed_proof: dict[str, Any],
    stop_reason: str | None,
    failure_reason: str | None,
):
    contract = _public_task_contract_from_runtime(runtime)
    if contract is None:
        return None
    verifier = PublicTaskCompletionVerifier(contract)
    reason = (stop_reason or failure_reason or "").lower()
    browser_state = payload.get("browser_state")
    state_text = ""
    if isinstance(browser_state, dict):
        state_text = " ".join(str(value) for value in browser_state.values()).lower()
    haystack = f"{reason} {state_text}"
    variance_reason: str | None = None
    if "timeout" in haystack or "timed out" in haystack:
        variance_reason = "timeout"
    elif any(
        marker in haystack
        for marker in (
            "network",
            "net::err_",
            "name_not_resolved",
            "connection_refused",
            "connection_reset",
            "connection_closed",
            "dns",
            "err_internet_disconnected",
        )
    ):
        variance_reason = "network_error"
    elif "selector" in haystack:
        variance_reason = "missing_selector"
    elif "target_not_allowlisted" in haystack or "redirect" in haystack:
        variance_reason = "redirect_off_allowlist"
    elif "captcha" in haystack or "verify you are human" in haystack or "verification" in haystack:
        variance_reason = "captcha"
    elif "rate limit" in haystack or "rate_limited" in haystack or "abuse detection" in haystack:
        variance_reason = "rate_limited"
    elif (
        "permission" in haystack
        or "private repository" in haystack
        or "access denied" in haystack
    ):
        variance_reason = "permission"
    elif "login_required" in haystack or "sign in" in haystack:
        variance_reason = "login_required"
    elif stop_reason == "public_task_action_not_allowed":
        result = verifier.classify_variance("public_task_action_not_allowed")
        result.completion_state = PublicTaskCompletionState.STOPPED
        result.stop_reason = "public_task_action_not_allowed"
        result.observed_proof = observed_proof
        return result
    if variance_reason is None:
        return None
    result = verifier.classify_variance(variance_reason)
    result.observed_proof = observed_proof
    return result


def _contract_action_name(action_type: str, description: str = "") -> str:
    action = action_type.lower()
    if action == "click" and "expand" in description.lower():
        return "expand"
    return action


def _detect_stop(
    payload: dict[str, Any],
    actions: list[BrowserActionEvent],
    raw_action_items: list[dict[str, Any]] | None = None,
):
    top_level_stop = detect_browser_state_stop(_raw_browser_state(payload.get("browser_state", {})))
    if top_level_stop is not None:
        return top_level_stop
    raw_action_items = raw_action_items or []
    for index, action in enumerate(actions):
        raw_state = (
            _raw_browser_state(raw_action_items[index].get("browser_state", {}))
            if index < len(raw_action_items)
            else action.browser_state
        )
        stop = detect_browser_state_stop(raw_state)
        if stop is not None:
            return stop
    return None


def _detect_public_readonly_stop(
    policy: PublicReadonlyPolicy,
    payload: dict[str, Any],
    actions: list[BrowserActionEvent],
    raw_action_items: list[dict[str, Any]] | None = None,
    public_task_contract: PublicTaskContract | None = None,
) -> BrowserStateStop | None:
    top_level_state = _raw_browser_state(payload.get("browser_state", {}))
    if top_level_state:
        decision = policy.check_browser_state(top_level_state)
        if not decision.allowed:
            return BrowserStateStop(reason=decision.reason, detail=decision.detail or decision.reason)
    raw_action_items = raw_action_items or []
    allowed_task_actions = {
        action.lower()
        for action in (public_task_contract.allowed_actions if public_task_contract else [])
    }
    for index, action in enumerate(actions):
        action_decision = policy.check_action(action.action_type, action.description)
        if not action_decision.allowed:
            return BrowserStateStop(
                reason=action_decision.reason,
                detail=action_decision.detail or action_decision.reason,
            )
        task_action = _contract_action_name(action.action_type, action.description)
        if allowed_task_actions and task_action not in allowed_task_actions:
            return BrowserStateStop(
                reason="public_task_action_not_allowed",
                detail=(
                    f"action '{task_action}' is outside public task contract "
                    f"allowed actions: {', '.join(sorted(allowed_task_actions))}"
                ),
            )
        raw_state = (
            _raw_browser_state(raw_action_items[index].get("browser_state", {}))
            if index < len(raw_action_items)
            else action.browser_state
        )
        state_decision = policy.check_browser_state(raw_state)
        if not state_decision.allowed:
            return BrowserStateStop(
                reason=state_decision.reason,
                detail=state_decision.detail or state_decision.reason,
                evidence=_sanitize_browser_state(raw_state),
            )
    return None


def _raw_browser_state(state: Any) -> dict[str, Any]:
    return state if isinstance(state, dict) else {}


def _sanitize_browser_state(state: Any) -> dict[str, Any]:
    from .trace_writer import sanitize_trace_dict

    if not isinstance(state, dict):
        return {}
    sanitized = sanitize_trace_dict(state)
    return sanitized if isinstance(sanitized, dict) else {}


class PublicReadonlyBrowserAgent:
    """Small public-readonly Playwright adapter with ephemeral local browser state."""

    def __init__(
        self,
        task: str,
        runtime: dict[str, Any],
        vision_backend_url: str | None = None,
        target_url: str | None = None,
        timeout_seconds: int = 15,
        policy: PublicReadonlyPolicy | None = None,
        execution_id: str | None = None,
        visual_artifacts_dir: Path | None = None,
        headed_debug: bool = False,
    ):
        self.task = task
        self.runtime = runtime
        self.vision_backend_url = vision_backend_url
        self.target_url = target_url
        self.timeout_seconds = timeout_seconds
        self.policy = policy
        self.public_task_contract = _public_task_contract_from_runtime(runtime)
        self.execution_id = execution_id or "public-readonly"
        self.visual_artifacts_dir = visual_artifacts_dir
        self.headed_debug = headed_debug

    async def run(self) -> dict[str, Any]:
        if not self.target_url:
            return {"status": "failed", "failure_reason": "missing_public_target", "actions": []}
        if self.policy is not None:
            decision = self.policy.check_url(self.target_url)
            if not decision.allowed:
                return {"status": "stopped", "stop_reason": decision.reason, "actions": []}
        action_decision = self._action_decision("navigate", "opened allowlisted public page")
        if action_decision is not None:
            return {
                "status": "stopped",
                "stop_reason": action_decision.reason,
                "actions": [],
            }

        from playwright.async_api import async_playwright

        actions: list[dict[str, Any]] = []
        visual_artifacts: list[dict[str, Any]] = []
        browser = None
        context = None
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(**_chromium_launch_kwargs(self.headed_debug))
                context = await browser.new_context(storage_state=None)
                page = await context.new_page()
                completed_search = False
                completed_expand = False
                await page.goto(
                    self.target_url,
                    wait_until="domcontentloaded",
                    timeout=self.timeout_seconds * 1000,
                )
                browser_state = await _public_page_state(
                    page,
                    origin=self.runtime.get("public_origin"),
                )
                actions.append(
                    {
                        "type": "navigate",
                        "description": "opened allowlisted public page",
                        "browser_state": browser_state,
                    }
                )
                artifact = await self._capture_visual_artifact(
                    page=page,
                    action_label="opened allowlisted public page",
                    browser_state=browser_state,
                    step_index=len(actions),
                    artifact_kind="step_screenshot",
                    completion_state=PublicTaskCompletionState.PARTIAL,
                )
                if artifact is not None:
                    actions[-1]["screenshot_ref"] = artifact["local_ref"]
                    visual_artifacts.append(artifact)
                blocked = self._blocked_state(browser_state)
                if blocked:
                    _mark_last_visual_artifact_final(
                        visual_artifacts,
                        artifact_kind="blocked_screenshot",
                        completion_state=PublicTaskCompletionState.STOPPED,
                    )
                    return _public_readonly_stopped(blocked.reason, actions, visual_artifacts)

                if self._has_step_budget(actions):
                    query = str(
                        (self.runtime.get("public_task_slots") or {}).get("search_query")
                        or _extract_public_search_query(self.task)
                        or ""
                    )
                    if self._is_github_search_contract() and query:
                        action_decision = self._action_decision(
                            "search",
                            f"read-only GitHub repository search for {query}",
                        )
                        if action_decision is not None:
                            return _public_readonly_stopped(
                                action_decision.reason,
                                actions,
                                visual_artifacts,
                            )
                        browser_state = await _public_page_state(
                            page,
                            origin=self.runtime.get("public_origin"),
                        )
                        actions.append(
                            {
                                "type": "search",
                                "description": f"searched GitHub repositories for {query}",
                                "browser_state": browser_state,
                            }
                        )
                        completed_search = True
                        artifact = await self._capture_visual_artifact(
                            page=page,
                            action_label=f"searched GitHub repositories for {query}",
                            browser_state=browser_state,
                            step_index=len(actions),
                            artifact_kind="step_screenshot",
                            completion_state=PublicTaskCompletionState.PARTIAL,
                        )
                        if artifact is not None:
                            actions[-1]["screenshot_ref"] = artifact["local_ref"]
                            visual_artifacts.append(artifact)
                        blocked = self._blocked_state(browser_state)
                        if blocked:
                            _mark_last_visual_artifact_final(
                                visual_artifacts,
                                artifact_kind="blocked_screenshot",
                                completion_state=PublicTaskCompletionState.STOPPED,
                            )
                            return _public_readonly_stopped(blocked.reason, actions, visual_artifacts)
                    elif query:
                        search_result = await self._try_public_search(page, query)
                        if search_result is not None:
                            if search_result.get("type") == "policy_stop":
                                return _public_readonly_stopped(
                                    str(search_result.get("stop_reason") or "public_task_action_not_allowed"),
                                    actions,
                                    visual_artifacts,
                                )
                            actions.append(search_result)
                            completed_search = True
                            artifact = await self._capture_visual_artifact(
                                page=page,
                                action_label=str(search_result.get("description") or "public search"),
                                browser_state=search_result["browser_state"],
                                step_index=len(actions),
                                artifact_kind="step_screenshot",
                                completion_state=PublicTaskCompletionState.PARTIAL,
                            )
                            if artifact is not None:
                                actions[-1]["screenshot_ref"] = artifact["local_ref"]
                                visual_artifacts.append(artifact)
                            blocked = self._blocked_state(search_result["browser_state"])
                            if blocked:
                                _mark_last_visual_artifact_final(
                                    visual_artifacts,
                                    artifact_kind="blocked_screenshot",
                                    completion_state=PublicTaskCompletionState.STOPPED,
                                )
                                return _public_readonly_stopped(blocked.reason, actions, visual_artifacts)

                if self._has_step_budget(actions) and _wants_public_expand(self.task):
                    expand_result = await self._try_public_expand(page)
                    if expand_result is not None:
                        if expand_result.get("type") == "policy_stop":
                            return _public_readonly_stopped(
                                str(expand_result.get("stop_reason") or "public_task_action_not_allowed"),
                                actions,
                                visual_artifacts,
                            )
                        actions.append(expand_result)
                        completed_expand = True
                        blocked = self._blocked_state(expand_result["browser_state"])
                        if blocked:
                            _mark_last_visual_artifact_final(
                                visual_artifacts,
                                artifact_kind="blocked_screenshot",
                                completion_state=PublicTaskCompletionState.STOPPED,
                            )
                            return _public_readonly_stopped(blocked.reason, actions, visual_artifacts)

                if self._has_step_budget(actions):
                    action_decision = self._action_decision(
                        "extract",
                        "read public page title",
                    )
                    if action_decision is not None:
                        return _public_readonly_stopped(
                            action_decision.reason,
                            actions,
                            visual_artifacts,
                        )
                    browser_state = await _public_page_state(
                        page,
                        origin=self.runtime.get("public_origin"),
                    )
                    actions.append(
                        {
                            "type": "extract",
                            "description": f"read public page title: {browser_state.get('page_title', '')}",
                            "grounding_evidence_refs": [
                                f"grounding/public-readonly/{self.runtime.get('public_allowlist_id')}.json"
                            ],
                            "browser_state": browser_state,
                        }
                    )
                    artifact = await self._capture_visual_artifact(
                        page=page,
                        action_label=f"read public page title: {browser_state.get('page_title', '')}",
                        browser_state=browser_state,
                        step_index=len(actions),
                        artifact_kind="final_screenshot",
                        completion_state=PublicTaskCompletionState.PARTIAL,
                        is_final=True,
                    )
                    if artifact is not None:
                        actions[-1]["screenshot_ref"] = artifact["local_ref"]
                        visual_artifacts.append(artifact)
                stop_reason = _should_stop_for_incomplete_public_task(
                    task=self.task,
                    action_count=len(actions),
                    max_steps=self.policy.max_steps if self.policy is not None else 3,
                    completed_search=completed_search,
                    completed_expand=completed_expand,
                )
                if stop_reason is not None:
                    _mark_last_visual_artifact_final(
                        visual_artifacts,
                        completion_state=PublicTaskCompletionState.PARTIAL,
                    )
                    return _public_readonly_stopped(stop_reason, actions, visual_artifacts)
        except Exception as exc:
            return {
                "status": "failed",
                "failure_reason": "public_readonly_browser_error",
                "actions": [],
                "browser_state": {"page_title": str(exc)[:120]},
            }
        finally:
            if context is not None:
                with suppress(Exception):
                    await context.close()
            if browser is not None:
                with suppress(Exception):
                    await browser.close()

        _mark_last_visual_artifact_final(
            visual_artifacts,
            completion_state=PublicTaskCompletionState.PARTIAL,
        )
        return {"status": "succeeded", "actions": actions, "visual_artifacts": visual_artifacts}

    def _has_step_budget(self, actions: list[dict[str, Any]]) -> bool:
        max_steps = self.policy.max_steps if self.policy is not None else 3
        return len(actions) < max_steps

    def _action_decision(
        self,
        action_type: str,
        description: str,
    ) -> PublicReadonlyPolicyDecision | None:
        if self.policy is not None:
            decision = self.policy.check_action(action_type, description)
            if not decision.allowed:
                return decision
        allowed_actions = {
            action.lower()
            for action in (self.public_task_contract.allowed_actions if self.public_task_contract else [])
        }
        task_action = _contract_action_name(action_type, description)
        if allowed_actions and task_action not in allowed_actions:
            return PublicReadonlyPolicyDecision(
                allowed=False,
                reason="public_task_action_not_allowed",
                detail=(
                    f"action '{task_action}' is outside public task contract allowed actions: "
                    f"{', '.join(sorted(allowed_actions))}"
                ),
            )
        return None

    def _blocked_state(self, state: dict[str, Any]) -> PublicReadonlyPolicyDecision | None:
        if self.policy is None:
            return None
        decision = self.policy.check_browser_state(state)
        return None if decision.allowed else decision

    def _is_github_search_contract(self) -> bool:
        return (
            self.public_task_contract is not None
            and self.public_task_contract.task_kind == "github-repo-search"
        )

    async def _capture_visual_artifact(
        self,
        *,
        page: Any,
        action_label: str,
        browser_state: dict[str, Any],
        step_index: int,
        artifact_kind: str,
        completion_state: PublicTaskCompletionState,
        is_final: bool = False,
    ) -> dict[str, Any] | None:
        if self.visual_artifacts_dir is None:
            return None
        execution_dir = self.visual_artifacts_dir / self.execution_id
        execution_dir.mkdir(parents=True, exist_ok=True)
        filename = f"step-{step_index}-{_slugify_artifact_label(action_label)}.png"
        path = execution_dir / filename
        try:
            await page.screenshot(path=str(path), full_page=True)
        except Exception:
            return None
        local_ref = f"artifacts/public-readonly/{self.execution_id}/{filename}"
        artifact = PublicReadonlyVisualArtifact(
            artifact_id=f"{self.execution_id}-step-{step_index}",
            execution_id=self.execution_id,
            artifact_kind=artifact_kind,
            action_label=action_label,
            local_ref=local_ref,
            page_title=str(browser_state.get("page_title") or ""),
            sanitized_origin=str(self.runtime.get("public_origin") or browser_state.get("origin") or ""),
            completion_state=completion_state,
            privacy_state=EvidencePrivacyState.LOCAL_PRIVATE,
            sanitizer_status=(
                SanitizerStatus.PENDING
                if self.runtime.get("sanitizer_status") == SanitizerStatus.PENDING.value
                else SanitizerStatus.NOT_REQUIRED
            ),
            step_index=step_index,
            is_final=is_final,
        )
        return artifact.model_dump(mode="json")

    async def _try_public_search(self, page: Any, query: str) -> dict[str, Any] | None:
        decision = self._action_decision("search", f"read-only public search for {query}")
        if decision is not None:
            return {
                "type": "policy_stop",
                "description": f"public search policy rejected: {decision.reason}",
                "stop_reason": decision.reason,
                "browser_state": await _public_page_state(page, self.runtime.get("public_origin")),
            }
        locator = page.locator(
            "input[type='search'], input[name='q'], "
            "input[aria-label*='Search' i], input[placeholder*='Search' i]"
        ).first
        try:
            if await locator.count() == 0:
                return None
            await locator.fill(query, timeout=1000)
            await locator.press("Enter", timeout=1000)
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=2000)
            except Exception:
                pass
        except Exception:
            return None
        return {
            "type": "search",
            "description": f"filled public read-only search field for {query}",
            "browser_state": await _public_page_state(page, self.runtime.get("public_origin")),
        }

    async def _try_public_expand(self, page: Any) -> dict[str, Any] | None:
        description = "expand public read-only section"
        decision = self._action_decision("click", description)
        if decision is not None:
            return {
                "type": "policy_stop",
                "description": f"public expand policy rejected: {decision.reason}",
                "stop_reason": decision.reason,
                "browser_state": await _public_page_state(page, self.runtime.get("public_origin")),
            }
        locator = page.locator("summary, button[aria-expanded='false']").first
        try:
            if await locator.count() == 0:
                return None
            await locator.click(timeout=1000)
        except Exception:
            return None
        return {
            "type": "click",
            "description": description,
            "browser_state": await _public_page_state(page, self.runtime.get("public_origin")),
        }


async def _public_page_state(page: Any, origin: str | None) -> dict[str, Any]:
    visible_text = ""
    try:
        visible_text = (await page.locator("body").inner_text(timeout=1000))[:500]
    except Exception:
        visible_text = ""
    return {
        "page_title": await page.title(),
        "url": page.url,
        "origin": origin,
        "visible_text": visible_text,
    }


def _extract_public_search_query(task: str) -> str | None:
    patterns = (
        r"(?:search|look up|find)\s+([^\n.;|]+)",
        r"(?:搜索|查找|查询)\s*([^，。；\n|]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, task, flags=re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            return query[:80] if query else None
    return None


def _wants_public_expand(task: str) -> bool:
    return any(marker in task.lower() for marker in ("expand", "展开", "折叠", "details"))


def _should_stop_for_incomplete_public_task(
    *,
    task: str,
    action_count: int,
    max_steps: int,
    completed_search: bool,
    completed_expand: bool,
) -> str | None:
    budget_exhausted = action_count >= max_steps
    if not budget_exhausted:
        return None
    if _extract_public_search_query(task) and not completed_search:
        return "public_readonly_step_budget_reached"
    if _wants_public_expand(task) and not completed_expand:
        return "public_readonly_step_budget_reached"
    return None


def _public_readonly_stopped(
    reason: str,
    actions: list[dict[str, Any]],
    visual_artifacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = {
        "status": "stopped",
        "stop_reason": reason,
        "actions": actions,
    }
    if visual_artifacts:
        payload["visual_artifacts"] = visual_artifacts
    return payload


def _mark_last_visual_artifact_final(
    visual_artifacts: list[dict[str, Any]],
    *,
    artifact_kind: str | None = None,
    completion_state: PublicTaskCompletionState,
) -> None:
    if not visual_artifacts:
        return
    artifact = visual_artifacts[-1]
    artifact["is_final"] = True
    artifact["completion_state"] = completion_state.value
    if artifact_kind is not None:
        artifact["artifact_kind"] = artifact_kind


def _slugify_artifact_label(label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return (slug or "visual")[:48]


def _chromium_launch_kwargs(headed_debug: bool = False) -> dict[str, Any]:
    system_chrome = _system_chromium_executable()
    if system_chrome is not None:
        return {"headless": not headed_debug, "executable_path": str(system_chrome)}
    return {"headless": not headed_debug}


def _system_chromium_executable() -> Path | None:
    candidates = (
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


class ControlledLiveBrowserAgent:
    """Deterministic local live adapter for controlled demo pages."""

    def __init__(self, task: str, runtime: dict[str, Any], vision_backend_url: str | None = None):
        self.task = task
        self.runtime = runtime
        self.vision_backend_url = vision_backend_url

    async def run(self) -> dict[str, Any]:
        from playwright.async_api import async_playwright

        import browser_use_vision

        target_url = self.runtime.get("controlled_target_url")
        target_ref = self.runtime.get("controlled_target_ref")
        fixture_id = self.runtime.get("controlled_fixture_id") or "controlled"
        if not target_url:
            return {
                "status": "failed",
                "failure_reason": "missing_controlled_target_url",
                "actions": [],
            }

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                executable_path=playwright.chromium.executable_path,
            )
            page = await browser.new_page()
            await page.goto(target_url)
            action = await self._perform_controlled_action(page, fixture_id)
            await browser.close()

        action["grounding_evidence_refs"] = [
            f"grounding/live-controlled/{fixture_id}.json",
            f"browser-use-vision:{getattr(browser_use_vision, '__version__', 'unknown')}",
        ]
        action["screenshot_ref"] = f"screenshots/sanitized/live-controlled/{fixture_id}.png"
        action["browser_state"] = {"controlled_target_ref": target_ref}
        return {
            "status": "succeeded",
            "actions": [action],
            "grounding_evidence_refs": action["grounding_evidence_refs"],
        }

    async def _perform_controlled_action(self, page, fixture_id: str) -> dict[str, str]:
        if fixture_id == "github-showcase":
            await page.get_by_label("repository search").fill("browser-use-vision")
            await page.get_by_label("run controlled search").click()
            return {
                "type": "search",
                "description": "searched the controlled public-code showcase for browser-use-vision",
            }
        if fixture_id == "icon-search":
            await page.get_by_label("search").click()
            return {
                "type": "click",
                "description": "clicked the icon-only search control on the controlled toolbar page",
            }
        if fixture_id == "color-swatch":
            await page.get_by_label("green color swatch").click()
            return {
                "type": "click",
                "description": "selected the green color swatch on the controlled color page",
            }
        if fixture_id == "svg-dashboard":
            text = (await page.locator("svg").text_content()) or ""
            return {
                "type": "extract",
                "description": f"read controlled SVG dashboard text: {text.strip()}",
            }
        return {
            "type": "inspect",
            "description": f"opened controlled page for {fixture_id}",
        }
