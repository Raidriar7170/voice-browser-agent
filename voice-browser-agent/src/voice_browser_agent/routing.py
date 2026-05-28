from __future__ import annotations

from .demo_tasks import get_live_controlled_task
from .models import (
    BrowserIntentType,
    BrowserTaskRequest,
    ClarificationRequest,
    ConfirmationDecision,
    ConfirmationState,
    EvidencePrivacyState,
    ExecutionMode,
    NormalizedOutput,
    RouteDecision,
    RouteType,
    SanitizerStatus,
    ValidationResult,
)
from .public_readonly import (
    PublicReadonlyRoutingConfig,
    has_transcript_url,
    match_public_readonly_task,
    match_public_readonly_target,
    request_looks_public,
)


def select_execution_route(
    normalized: NormalizedOutput,
    validation: ValidationResult | None,
    confirmation: ConfirmationDecision | None = None,
    public_readonly_config: PublicReadonlyRoutingConfig | None = None,
    requested_execution_mode: ExecutionMode | None = None,
) -> RouteDecision:
    if isinstance(normalized, ClarificationRequest):
        return RouteDecision(
            route_type=RouteType.CLARIFICATION,
            execution_mode=ExecutionMode.DEMO_PREVIEW,
            evidence_mode="clarification",
            route_reason=normalized.reason,
            user_message=normalized.question,
            live_evidence_eligible=False,
        )

    if validation is None or not validation.accepted:
        return RouteDecision(
            route_type=RouteType.BLOCKED,
            execution_mode=ExecutionMode.DEMO_PREVIEW,
            evidence_mode="blocked",
            route_reason=validation.reason if validation else "not validated",
            user_message="Command was not accepted for browser execution.",
            live_evidence_eligible=False,
        )

    if confirmation is not None and confirmation.state is ConfirmationState.PENDING:
        return RouteDecision(
            route_type=RouteType.CONFIRMATION_REQUIRED,
            execution_mode=ExecutionMode.DEMO_PREVIEW,
            evidence_mode="confirmation_required",
            route_reason=confirmation.reason,
            user_message="Command requires operator confirmation before any browser action.",
            live_evidence_eligible=False,
        )

    if requested_execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY:
        public_route = _public_readonly_route(
            normalized,
            public_readonly_config,
            requested_execution_mode=requested_execution_mode,
        )
        if public_route is not None:
            return public_route

    if public_readonly_config is not None and public_readonly_config.enabled:
        public_route = _public_readonly_route(
            normalized,
            public_readonly_config,
            requested_execution_mode=requested_execution_mode,
        )
        if public_route is not None:
            return public_route

    fixture_id = _fixture_for_request(normalized)
    if fixture_id is not None:
        controlled_task = get_live_controlled_task(fixture_id)
        if controlled_task is not None:
            return _controlled_route(
                fixture_id=controlled_task.fixture_id,
                target_ref=controlled_task.target_ref,
                evidence_mode=_evidence_mode_for_controlled_task(controlled_task.fixture_id),
                reason=_route_reason_for_fixture(controlled_task.fixture_id),
            )

    public_route = _public_readonly_route(
        normalized,
        public_readonly_config,
        requested_execution_mode=requested_execution_mode,
    )
    if public_route is not None:
        return public_route

    text = _request_text(normalized)
    if "openai" in text:
        return RouteDecision(
            route_type=RouteType.DEMO_PREVIEW,
            execution_mode=ExecutionMode.DEMO_PREVIEW,
            evidence_mode="demo_preview",
            route_reason="public_readonly_disabled",
            user_message=(
                "Public-readonly execution is disabled by default; this command will be "
                "shown as demo-preview evidence only."
            ),
            live_evidence_eligible=False,
            public_readonly_enabled=False,
        )

    return RouteDecision(
        route_type=RouteType.DEMO_PREVIEW,
        execution_mode=ExecutionMode.DEMO_PREVIEW,
        evidence_mode="demo_preview",
        route_reason="no_supported_controlled_target",
        user_message="No supported controlled live target matched; using demo-preview mode.",
        live_evidence_eligible=False,
    )


def _public_readonly_route(
    request: BrowserTaskRequest,
    config: PublicReadonlyRoutingConfig | None,
    requested_execution_mode: ExecutionMode | None,
) -> RouteDecision | None:
    if config is None:
        if requested_execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY:
            return _blocked_public_route(
                reason="public_readonly_override_not_allowed",
                message="Public-readonly execution cannot be selected without backend policy approval.",
            )
        return None

    target = match_public_readonly_target(request, config)
    task_match = match_public_readonly_task(request, config) if target is not None else None
    looks_public = request_looks_public(request)
    if request.safety_flags:
        if target or looks_public or requested_execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY:
            return _blocked_public_route(
                reason="public_readonly_unsafe_command",
                message="Public-readonly execution stopped before browser action because the command is not read-only.",
            )
        return None

    if target is not None and config.enabled and task_match is None:
        return _blocked_public_route(
            reason="public_task_contract_mismatch",
            message="Public-readonly execution was blocked because no configured task contract matched.",
        )

    if target is not None and config.enabled and task_match is not None:
        task_target, contract, slots = task_match
        return RouteDecision(
            route_type=RouteType.PUBLIC_READONLY,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            evidence_mode="live_public_readonly",
            route_reason="matched_allowlisted_public_target",
            user_message=(
                f"Running local isolated public-readonly execution for {task_target.label}; "
                "trace evidence stays local/private until sanitizer approval."
            ),
            live_evidence_eligible=False,
            public_readonly_enabled=True,
            public_target_label=task_target.label,
            public_origin=task_target.origin,
            public_allowlist_id=task_target.allowlist_id,
            public_task_id=contract.task_id,
            public_task_kind=contract.task_kind,
            public_task_slots=slots,
            public_completion_criteria_id=contract.completion_criteria.criteria_id,
            evidence_privacy_state=EvidencePrivacyState.LOCAL_PRIVATE,
            sanitizer_status=SanitizerStatus.PENDING
            if config.sanitizer_required
            else SanitizerStatus.NOT_REQUIRED,
            execution_limits={
                "max_steps": contract.max_steps,
                "timeout_seconds": contract.timeout_seconds,
            },
        )

    if target is not None and not config.enabled:
        return RouteDecision(
            route_type=RouteType.DEMO_PREVIEW,
            execution_mode=ExecutionMode.DEMO_PREVIEW,
            evidence_mode="demo_preview",
            route_reason="public_readonly_disabled",
            user_message=(
                "Public-readonly execution is disabled by default; this command will be "
                "shown as demo-preview evidence only."
            ),
            live_evidence_eligible=False,
            public_readonly_enabled=False,
            public_target_label=target.label,
            public_origin=target.origin,
            public_allowlist_id=target.allowlist_id,
            evidence_privacy_state=EvidencePrivacyState.NOT_APPLICABLE,
            sanitizer_status=SanitizerStatus.NOT_REQUIRED,
        )

    if requested_execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY:
        return _blocked_public_route(
            reason="public_readonly_override_not_allowed",
            message="Manual public-readonly execution was blocked because no allowlisted target matched.",
        )

    if config.enabled and (looks_public or has_transcript_url(request)):
        return _blocked_public_route(
            reason="public_readonly_target_not_allowlisted",
            message="Public-readonly execution is enabled, but this command does not match an allowlisted target.",
        )

    if not config.enabled and looks_public:
        return RouteDecision(
            route_type=RouteType.DEMO_PREVIEW,
            execution_mode=ExecutionMode.DEMO_PREVIEW,
            evidence_mode="demo_preview",
            route_reason="public_readonly_disabled",
            user_message=(
                "Public-readonly execution is disabled by default; this command will be "
                "shown as demo-preview evidence only."
            ),
            live_evidence_eligible=False,
            public_readonly_enabled=False,
        )
    return None


def _blocked_public_route(reason: str, message: str) -> RouteDecision:
    return RouteDecision(
        route_type=RouteType.BLOCKED,
        execution_mode=ExecutionMode.DEMO_PREVIEW,
        evidence_mode="blocked",
        route_reason=reason,
        user_message=message,
        live_evidence_eligible=False,
        public_readonly_enabled=False,
    )


def _controlled_route(
    fixture_id: str,
    target_ref: str,
    evidence_mode: str,
    reason: str,
) -> RouteDecision:
    return RouteDecision(
        route_type=RouteType.CONTROLLED_LIVE,
        execution_mode=ExecutionMode.LIVE_CONTROLLED,
        evidence_mode=evidence_mode,
        controlled_fixture_id=fixture_id,
        controlled_target_ref=target_ref,
        route_reason=reason,
        user_message=f"Running a controlled local live task for {fixture_id}.",
        live_evidence_eligible=True,
    )


def _fixture_for_request(request: BrowserTaskRequest) -> str | None:
    text = _request_text(request)
    visual_text = " ".join(ref.text.lower() for ref in request.visual_references)
    if "github" in text:
        return "github-showcase"
    if any(marker in text or marker in visual_text for marker in ("放大镜", "search icon", "magnifying", "图标")):
        return "icon-search"
    if any(marker in text or marker in visual_text for marker in ("绿色色块", "色块", "swatch", "green")):
        return "color-swatch"
    if any(marker in text for marker in ("svg", "图表", "柱子", "dashboard", "chart", "highest")):
        return "svg-dashboard"
    if request.intent_type is BrowserIntentType.CLICK_VISUAL_TARGET and request.visual_references:
        return "icon-search"
    return None


def _request_text(request: BrowserTaskRequest) -> str:
    parts = [request.task.lower(), request.intent_type.value.lower()]
    parts.extend(ref.text.lower() for ref in request.visual_references)
    return " ".join(parts)


def _evidence_mode_for_controlled_task(fixture_id: str) -> str:
    if fixture_id == "github-showcase":
        return "controlled_showcase"
    return "live_controlled"


def _route_reason_for_fixture(fixture_id: str) -> str:
    reasons = {
        "github-showcase": "matched github-shaped command to controlled local showcase",
        "icon-search": "matched visual search icon command",
        "color-swatch": "matched color swatch command",
        "svg-dashboard": "matched dashboard/chart extraction command",
    }
    return reasons.get(fixture_id, "matched controlled local task")
