from __future__ import annotations

from .demo_tasks import get_live_controlled_task
from .models import (
    BrowserIntentType,
    BrowserTaskRequest,
    ClarificationRequest,
    ConfirmationDecision,
    ConfirmationState,
    ExecutionMode,
    NormalizedOutput,
    RouteDecision,
    RouteType,
    ValidationResult,
)


def select_execution_route(
    normalized: NormalizedOutput,
    validation: ValidationResult | None,
    confirmation: ConfirmationDecision | None = None,
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
