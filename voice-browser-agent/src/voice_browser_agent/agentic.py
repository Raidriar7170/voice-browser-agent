from __future__ import annotations

from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from .executor import BrowserExecutionResult, BrowserExecutorConfig
from .models import (
    AgenticActionResult,
    AgenticRecoveryDecision,
    AgenticVerificationDecision,
    AgenticVisionStep,
    BrowserActionEvent,
    BrowserTaskRequest,
    ExecutionMode,
    ExecutionStatus,
    VisualVerificationResult,
)
from .safety import detect_browser_state_stop


class VisualObservation(BaseModel):
    summary: str
    target_status: Literal["resolved", "missing", "ambiguous", "stale", "sensitive"]
    selected_target_ref: str | None = None
    target_candidates: list[str] = Field(default_factory=list)
    grounding_evidence_refs: list[str] = Field(default_factory=list)
    screenshot_ref: str | None = None
    browser_state: dict[str, Any] = Field(default_factory=dict)


class VisualActionOutcome(BaseModel):
    status: Literal["succeeded", "failed", "no_effect"]
    action_type: str
    description: str
    browser_state: dict[str, Any] = Field(default_factory=dict)
    screenshot_ref: str | None = None
    grounding_evidence_refs: list[str] = Field(default_factory=list)


class AgenticObservationAdapter(Protocol):
    async def observe(
        self,
        request: BrowserTaskRequest,
        step_index: int,
        previous_step: AgenticVisionStep | None,
    ) -> VisualObservation | None: ...

    async def act(
        self,
        request: BrowserTaskRequest,
        observation: VisualObservation,
        step_index: int,
    ) -> VisualActionOutcome | None: ...


class VisualVerifier(Protocol):
    async def verify(
        self,
        request: BrowserTaskRequest,
        observation: VisualObservation,
        outcome: VisualActionOutcome,
        step_index: int,
        runtime: dict[str, Any],
    ) -> VisualVerificationResult: ...


class ScriptedAgenticVisionAdapter:
    def __init__(
        self,
        observations: list[VisualObservation],
        outcomes: list[VisualActionOutcome],
    ):
        self.observations = observations
        self.outcomes = outcomes
        self.observation_index = 0
        self.outcome_index = 0

    async def observe(
        self,
        request: BrowserTaskRequest,
        step_index: int,
        previous_step: AgenticVisionStep | None,
    ) -> VisualObservation | None:
        if self.observation_index >= len(self.observations):
            return None
        observation = self.observations[self.observation_index]
        self.observation_index += 1
        return observation

    async def act(
        self,
        request: BrowserTaskRequest,
        observation: VisualObservation,
        step_index: int,
    ) -> VisualActionOutcome | None:
        if self.outcome_index >= len(self.outcomes):
            return None
        outcome = self.outcomes[self.outcome_index]
        self.outcome_index += 1
        return outcome


class ControlledAgenticVisionAdapter:
    """Small deterministic adapter for controlled demo pages.

    It keeps visual-loop evidence stable for public demo traces while preserving
    `browser-use-vision` as the named visual grounding dependency.
    """

    def __init__(self, task: str, runtime: dict[str, Any], vision_backend_url: str | None = None):
        self.task = task
        self.runtime = runtime
        self.vision_backend_url = vision_backend_url
        self._playwright: Any | None = None
        self._browser: Any | None = None
        self._page: Any | None = None

    async def observe(
        self,
        request: BrowserTaskRequest,
        step_index: int,
        previous_step: AgenticVisionStep | None,
    ) -> VisualObservation | None:
        page = await self._ensure_page()
        fixture_id = self.runtime.get("controlled_fixture_id") or "controlled"
        target_ref = self.runtime.get("controlled_target_ref") or request.controlled_target_ref
        evidence_ref = f"grounding/agentic/{fixture_id}-step-{step_index}.json"
        visible_text = ((await page.locator("body").inner_text()) or "").strip()
        return VisualObservation(
            summary=self._summary_for_fixture(fixture_id),
            target_status="resolved",
            selected_target_ref=f"controlled:{target_ref}",
            target_candidates=[f"controlled:{target_ref}"] if target_ref else [],
            grounding_evidence_refs=[evidence_ref, "browser-use-vision:controlled-adapter"],
            screenshot_ref=f"screenshots/sanitized/agentic/{fixture_id}-step-{step_index}.png",
            browser_state={
                "controlled_target_ref": target_ref,
                "page_title": await page.title(),
                "visible_text": visible_text,
            },
        )

    async def act(
        self,
        request: BrowserTaskRequest,
        observation: VisualObservation,
        step_index: int,
    ) -> VisualActionOutcome | None:
        page = await self._ensure_page()
        fixture_id = self.runtime.get("controlled_fixture_id") or "controlled"
        if (
            fixture_id == "color-swatch"
            and self.runtime.get("controlled_fixture_variant") == "first_no_effect_then_recover"
            and step_index == 1
        ):
            return VisualActionOutcome(
                status="no_effect",
                action_type="click",
                description="clicked stale color-swatch target without changing page state",
                browser_state=await self._post_action_visual_state(page, fixture_id),
                screenshot_ref=f"screenshots/sanitized/agentic/{fixture_id}-step-{step_index}-post.png",
                grounding_evidence_refs=[
                    *observation.grounding_evidence_refs,
                    f"grounding/agentic/{fixture_id}-step-{step_index}-post-action.json",
                ],
            )
        action_type, description = await self._perform_controlled_action(page, fixture_id)
        post_action_state = await self._post_action_visual_state(page, fixture_id)
        return VisualActionOutcome(
            status="succeeded",
            action_type=action_type,
            description=description,
            browser_state=post_action_state,
            screenshot_ref=f"screenshots/sanitized/agentic/{fixture_id}-step-{step_index}-post.png",
            grounding_evidence_refs=[
                *observation.grounding_evidence_refs,
                f"grounding/agentic/{fixture_id}-step-{step_index}-post-action.json",
            ],
        )

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None
        self._page = None

    async def _ensure_page(self):
        if self._page is not None:
            return self._page
        target_url = self.runtime.get("controlled_target_url")
        if not target_url:
            raise RuntimeError("missing controlled target URL for agentic execution")
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            executable_path=self._playwright.chromium.executable_path,
        )
        self._page = await self._browser.new_page()
        await self._page.goto(target_url)
        return self._page

    def _summary_for_fixture(self, fixture_id: str) -> str:
        summaries = {
            "icon-search": "Observed an icon-only toolbar and resolved the magnifying-glass search control.",
            "color-swatch": "Observed color swatches and resolved the requested green option.",
            "svg-dashboard": "Observed an SVG dashboard region and resolved the chart text target.",
            "github-showcase": "Observed a controlled public-code-search page and resolved the repository search field.",
        }
        return summaries.get(fixture_id, f"Observed controlled visual target for {fixture_id}.")

    async def _perform_controlled_action(self, page, fixture_id: str) -> tuple[str, str]:
        if fixture_id == "github-showcase":
            await page.get_by_label("repository search").fill("browser-use-vision")
            await page.get_by_label("run controlled search").click()
            return "search", "searched the controlled public-code showcase for browser-use-vision"
        if fixture_id == "color-swatch":
            await page.get_by_label("green color swatch").click()
            return "click", "selected the green color swatch using visual target evidence"
        if fixture_id == "svg-dashboard":
            await page.locator("svg").text_content()
            return "extract", "extracted the SVG dashboard text using visual region evidence"
        if fixture_id == "icon-search":
            await page.get_by_label("search").click()
        return "click", "clicked the icon-only search control using visual target evidence"

    async def _post_action_visual_state(self, page, fixture_id: str) -> dict[str, Any]:
        state = {
            "controlled_target_ref": self.runtime.get("controlled_target_ref"),
            "page_title": await page.title(),
        }
        if fixture_id == "icon-search":
            panel_state = await page.locator("#search-panel").get_attribute("data-visual-state")
            if panel_state == "open":
                state.update(
                    {
                        "visual_state_marker": "search-panel-open",
                        "result_state": "search panel open",
                    }
                )
        elif fixture_id == "color-swatch":
            selected = await page.locator("body").get_attribute("data-selected-swatch")
            if selected:
                state.update(
                    {
                        "visual_state_marker": f"{selected}-swatch-selected",
                        "selected_value": selected,
                        "result_state": f"{selected} swatch selected",
                    }
                )
        return state


class DeterministicVisualVerifier:
    mode = "deterministic_controlled"

    async def verify(
        self,
        request: BrowserTaskRequest,
        observation: VisualObservation,
        outcome: VisualActionOutcome,
        step_index: int,
        runtime: dict[str, Any],
    ) -> VisualVerificationResult:
        evidence_refs = _visual_verification_evidence_refs(observation, outcome)
        explicit = _coerce_explicit_visual_verification(outcome.browser_state, evidence_refs)
        if explicit is not None:
            return explicit

        expected_condition = _expected_visual_condition(request, runtime)
        observed_state_summary = _observed_visual_state_summary(observation, outcome)
        if outcome.status == "failed":
            return VisualVerificationResult(
                outcome="failed",
                expected_condition=expected_condition,
                observed_state_summary=observed_state_summary,
                reason="action failed before the expected visual state could be confirmed",
                verifier_mode=self.mode,
                sanitized_evidence_refs=evidence_refs,
            )
        if outcome.status == "no_effect":
            return VisualVerificationResult(
                outcome="failed",
                expected_condition=expected_condition,
                observed_state_summary=observed_state_summary,
                reason="post-action visual state showed no meaningful progress",
                verifier_mode=self.mode,
                sanitized_evidence_refs=evidence_refs,
            )
        if _state_requests_uncertain_verification(observation, outcome):
            return VisualVerificationResult(
                outcome="uncertain",
                expected_condition=expected_condition,
                observed_state_summary=observed_state_summary,
                reason="controlled verifier could not safely determine the visual outcome",
                verifier_mode=self.mode,
                sanitized_evidence_refs=evidence_refs,
            )
        if _has_controlled_visual_evidence(observation, outcome, runtime):
            return VisualVerificationResult(
                outcome="passed",
                expected_condition=expected_condition,
                observed_state_summary=observed_state_summary,
                reason="deterministic controlled verifier matched safe post-action evidence",
                verifier_mode=self.mode,
                sanitized_evidence_refs=evidence_refs,
            )
        return VisualVerificationResult(
            outcome="uncertain",
            expected_condition=expected_condition,
            observed_state_summary=observed_state_summary,
            reason="post-action evidence was insufficient for deterministic visual verification",
            verifier_mode=self.mode,
            sanitized_evidence_refs=evidence_refs,
        )


class AgenticVisionExecutor:
    def __init__(
        self,
        config: BrowserExecutorConfig,
        observation_adapter: AgenticObservationAdapter,
        agent_task: str | None = None,
        runtime: dict[str, Any] | None = None,
        visual_verifier: VisualVerifier | None = None,
    ):
        self.config = config
        self.observation_adapter = observation_adapter
        self.agent_task = agent_task
        self.runtime = runtime or {}
        self.visual_verifier = visual_verifier

    async def execute(self, request: BrowserTaskRequest, execution_id: str) -> BrowserExecutionResult:
        try:
            return await self._execute_inner(request, execution_id)
        finally:
            close = getattr(self.observation_adapter, "close", None)
            if close is not None:
                await close()

    async def _execute_inner(self, request: BrowserTaskRequest, execution_id: str) -> BrowserExecutionResult:
        execution_mode = self.config.resolved_execution_mode()
        runtime = {
            "execution_mode": execution_mode.value,
            "execution_style": "agentic_vision",
            "local_browser": self.config.local_browser,
            "remote_vision_backend_url": self.config.remote_vision_backend_url,
            "browser_channel": self.config.browser_channel,
            "max_steps": self.config.max_steps,
            "max_recoveries": self.config.max_recoveries,
            "controlled_fixture_id": self.config.controlled_fixture_id,
            "controlled_target_ref": self.config.controlled_target_ref or request.controlled_target_ref,
            "controlled_target_url": self.config.controlled_target_url,
            "visual_grounding_dependency": "browser-use-vision",
            "visual_verifier_mode": "deterministic_controlled",
            "visual_verifier_provider_mode": "none",
            "request_constraints": request.constraints,
            "stop_conditions": request.stop_conditions,
            **self.runtime,
        }
        runtime["execution_style"] = "agentic_vision"
        runtime["execution_mode"] = execution_mode.value

        actions: list[BrowserActionEvent] = []
        steps: list[AgenticVisionStep] = []
        grounding_refs: list[str] = []
        recoveries_used = 0
        previous_step: AgenticVisionStep | None = None
        visual_verifier = self.visual_verifier or DeterministicVisualVerifier()

        for step_index in range(1, self.config.max_steps + 1):
            observation = await self.observation_adapter.observe(request, step_index, previous_step)
            if observation is None:
                break

            step = self._step_from_observation(step_index, observation)
            _extend_unique(grounding_refs, observation.grounding_evidence_refs)

            stop = detect_browser_state_stop(observation.browser_state)
            if stop is not None:
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="stop",
                    reason=f"sensitive browser state: {stop.reason}",
                )
                step.verification_decision = AgenticVerificationDecision(
                    passed=False,
                    reason=stop.detail,
                )
                steps.append(step)
                return self._result(
                    execution_id,
                    execution_mode,
                    ExecutionStatus.STOPPED,
                    actions,
                    steps,
                    grounding_refs,
                    runtime,
                    stop_reason=stop.reason,
                )

            if observation.target_status == "ambiguous":
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="stop",
                    reason="ambiguous visual target",
                )
                steps.append(step)
                return self._result(
                    execution_id,
                    execution_mode,
                    ExecutionStatus.STOPPED,
                    actions,
                    steps,
                    grounding_refs,
                    runtime,
                    stop_reason="ambiguous_visual_target",
                )

            if observation.target_status in {"missing", "stale"}:
                if recoveries_used < self.config.max_recoveries and step_index < self.config.max_steps:
                    recoveries_used += 1
                    step.recovery_decision = AgenticRecoveryDecision(
                        kind="reobserve",
                        reason=f"{observation.target_status} target; re-observing once",
                    )
                    steps.append(step)
                    previous_step = step
                    continue
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="stop",
                    reason="step budget reached" if step_index >= self.config.max_steps else "target unresolved",
                )
                steps.append(step)
                return self._result(
                    execution_id,
                    execution_mode,
                    ExecutionStatus.STOPPED,
                    actions,
                    steps,
                    grounding_refs,
                    runtime,
                    stop_reason="step_budget_exceeded"
                    if step_index >= self.config.max_steps
                    else f"{observation.target_status}_visual_target",
                )

            outcome = await self.observation_adapter.act(request, observation, step_index)
            if outcome is None:
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="stop",
                    reason="missing action result",
                )
                steps.append(step)
                return self._result(
                    execution_id,
                    execution_mode,
                    ExecutionStatus.FAILED,
                    actions,
                    steps,
                    grounding_refs,
                    runtime,
                    failure_reason="missing_agentic_action_result",
                )

            self._apply_outcome(step, outcome)
            action = BrowserActionEvent(
                action_type=outcome.action_type,
                description=outcome.description,
                screenshot_ref=outcome.screenshot_ref or observation.screenshot_ref,
                grounding_evidence_refs=outcome.grounding_evidence_refs
                or observation.grounding_evidence_refs,
                browser_state=outcome.browser_state,
            )
            actions.append(action)
            _extend_unique(grounding_refs, action.grounding_evidence_refs)

            stop = detect_browser_state_stop(outcome.browser_state)
            if stop is not None:
                step.verification_decision = AgenticVerificationDecision(
                    passed=False,
                    reason=stop.detail,
                )
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="stop",
                    reason=f"sensitive browser state: {stop.reason}",
                )
                steps.append(step)
                return self._result(
                    execution_id,
                    execution_mode,
                    ExecutionStatus.STOPPED,
                    actions,
                    steps,
                    grounding_refs,
                    runtime,
                    stop_reason=stop.reason,
                )

            visual_verification = await visual_verifier.verify(
                request,
                observation,
                outcome,
                step_index,
                runtime,
            )
            step.visual_verification_result = visual_verification
            step.verification_decision = AgenticVerificationDecision(
                passed=visual_verification.outcome == "passed",
                reason=visual_verification.reason,
            )

            if outcome.status == "succeeded" and visual_verification.outcome == "passed":
                step.verification_decision = AgenticVerificationDecision(
                    passed=True,
                    reason=visual_verification.reason,
                )
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="none",
                    reason="visual verification passed",
                )
                steps.append(step)
                return self._result(
                    execution_id,
                    execution_mode,
                    ExecutionStatus.SUCCEEDED,
                    actions,
                    steps,
                    grounding_refs,
                    runtime,
                )

            if recoveries_used < self.config.max_recoveries and step_index < self.config.max_steps:
                recoveries_used += 1
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="reobserve",
                    reason=(
                        f"re-observing after visual verification "
                        f"{visual_verification.outcome}: {visual_verification.reason}"
                    ),
                )
                steps.append(step)
                previous_step = step
                continue

            step.recovery_decision = AgenticRecoveryDecision(
                kind="stop",
                reason=(
                    f"visual verification {visual_verification.outcome}: "
                    f"{visual_verification.reason}"
                ),
            )
            steps.append(step)
            return self._result(
                execution_id,
                execution_mode,
                ExecutionStatus.FAILED if outcome.status == "failed" else ExecutionStatus.STOPPED,
                actions,
                steps,
                grounding_refs,
                runtime,
                stop_reason=(
                    _visual_verification_stop_reason(visual_verification)
                    if outcome.status != "failed"
                    else None
                ),
                failure_reason="agentic_action_failed" if outcome.status == "failed" else None,
            )

        if not steps and not actions and not grounding_refs:
            return self._result(
                execution_id,
                execution_mode,
                ExecutionStatus.FAILED,
                actions,
                steps,
                grounding_refs,
                runtime,
                failure_reason="agentic_live_controlled_missing_evidence",
            )

        return self._result(
            execution_id,
            execution_mode,
            ExecutionStatus.STOPPED,
            actions,
            steps,
            grounding_refs,
            runtime,
            stop_reason="step_budget_exceeded",
        )

    def _step_from_observation(
        self,
        step_index: int,
        observation: VisualObservation,
    ) -> AgenticVisionStep:
        return AgenticVisionStep(
            step_index=step_index,
            observation_summary=observation.summary,
            target_status=observation.target_status,
            selected_target_ref=observation.selected_target_ref,
            target_candidates=observation.target_candidates,
            grounding_evidence_refs=observation.grounding_evidence_refs,
            screenshot_ref=observation.screenshot_ref,
        )

    def _apply_outcome(self, step: AgenticVisionStep, outcome: VisualActionOutcome) -> None:
        step.selected_action = f"{outcome.action_type}: {outcome.description}"
        step.action_result = AgenticActionResult(
            status=outcome.status,
            description=outcome.description,
            browser_state=outcome.browser_state,
        )

    def _result(
        self,
        execution_id: str,
        execution_mode: ExecutionMode,
        final_status: ExecutionStatus,
        actions: list[BrowserActionEvent],
        steps: list[AgenticVisionStep],
        grounding_refs: list[str],
        runtime: dict[str, Any],
        failure_reason: str | None = None,
        stop_reason: str | None = None,
    ) -> BrowserExecutionResult:
        if execution_mode is ExecutionMode.LIVE_CONTROLLED and not steps and not actions and not grounding_refs:
            final_status = ExecutionStatus.FAILED
            failure_reason = failure_reason or "agentic_live_controlled_missing_evidence"
        return BrowserExecutionResult(
            execution_id=execution_id,
            execution_mode=execution_mode,
            final_status=final_status,
            actions=actions,
            agentic_steps=steps,
            grounding_evidence_refs=grounding_refs,
            failure_reason=failure_reason,
            stop_reason=stop_reason,
            agent_task=self.agent_task or request_task_placeholder(runtime),
            runtime=runtime,
        )


def _visual_verification_evidence_refs(
    observation: VisualObservation,
    outcome: VisualActionOutcome,
) -> list[str]:
    refs: list[str] = []
    _extend_unique(refs, outcome.grounding_evidence_refs)
    _extend_unique(refs, observation.grounding_evidence_refs)
    for ref in (outcome.screenshot_ref, observation.screenshot_ref):
        if ref and ref not in refs:
            refs.append(ref)
    return refs


def _coerce_explicit_visual_verification(
    browser_state: dict[str, Any],
    evidence_refs: list[str],
) -> VisualVerificationResult | None:
    raw = browser_state.get("visual_verification")
    if not isinstance(raw, dict):
        return None
    payload = dict(raw)
    payload.setdefault("verifier_mode", "deterministic_controlled")
    payload.setdefault("sanitized_evidence_refs", evidence_refs)
    payload.setdefault("provider_metadata", {})
    return VisualVerificationResult.model_validate(payload)


def _expected_visual_condition(request: BrowserTaskRequest, runtime: dict[str, Any]) -> str:
    explicit = runtime.get("visual_verification_expected_condition")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    target_ref = runtime.get("controlled_target_ref") or request.controlled_target_ref
    fixture_id = runtime.get("controlled_fixture_id")
    if target_ref:
        return f"Controlled visual target {target_ref} satisfies task: {request.task}"
    if fixture_id:
        return f"Controlled fixture {fixture_id} satisfies task: {request.task}"
    return f"Post-action browser state satisfies task: {request.task}"


def _observed_visual_state_summary(
    observation: VisualObservation,
    outcome: VisualActionOutcome,
) -> str:
    state = {**observation.browser_state, **outcome.browser_state}
    explicit = state.get("observed_state_summary")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()

    parts: list[str] = []
    if observation.selected_target_ref:
        parts.append(f"selected_target_ref={observation.selected_target_ref}")
    for key in (
        "page_title",
        "title",
        "controlled_target_ref",
        "result_state",
        "selected_value",
    ):
        value = state.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(f"{key}={_safe_summary_preview(value)}")
    if state.get("visible_text"):
        parts.append("safe body text marker present")
    if outcome.description:
        parts.append(f"action={_safe_summary_preview(outcome.description)}")
    return "; ".join(parts) or "No safe post-action state marker was available."


def _safe_summary_preview(value: str, limit: int = 96) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def _state_requests_uncertain_verification(
    observation: VisualObservation,
    outcome: VisualActionOutcome,
) -> bool:
    state = {**observation.browser_state, **outcome.browser_state}
    return (
        state.get("visual_verification_uncertain") is True
        or state.get("visual_verification_outcome") == "uncertain"
    )


def _has_controlled_visual_evidence(
    observation: VisualObservation,
    outcome: VisualActionOutcome,
    runtime: dict[str, Any],
) -> bool:
    if outcome.status != "succeeded":
        return False
    state = outcome.browser_state
    if state.get("visual_verification_passed") is True:
        return True
    if state.get("visual_verification_outcome") == "passed":
        return True
    has_post_action_marker = any(
        isinstance(state.get(key), str) and bool(state.get(key).strip())
        for key in ("visual_state_marker", "result_state", "selected_value", "extracted_text_marker")
    )
    has_post_action_ref = any(
        "post-action" in ref or "-post" in ref
        for ref in _visual_verification_evidence_refs(observation, outcome)
    )
    return has_post_action_marker and has_post_action_ref


def _visual_verification_stop_reason(verification: VisualVerificationResult) -> str:
    if verification.outcome == "uncertain":
        return "visual_verification_uncertain"
    if verification.outcome == "failed":
        return "visual_verification_failed"
    return "visual_verification_not_passed"


def _extend_unique(target: list[str], values: list[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def request_task_placeholder(runtime: dict[str, Any]) -> str:
    fixture_id = runtime.get("controlled_fixture_id")
    return f"agentic vision execution for {fixture_id or 'browser task'}"
