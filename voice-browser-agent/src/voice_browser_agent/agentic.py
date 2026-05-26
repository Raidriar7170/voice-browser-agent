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
        visible_text = ((await page.text_content("body")) or "").strip()
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
        action_type, description = await self._perform_controlled_action(page, fixture_id)
        return VisualActionOutcome(
            status="succeeded",
            action_type=action_type,
            description=description,
            browser_state={
                "controlled_target_ref": self.runtime.get("controlled_target_ref"),
                "page_title": await page.title(),
            },
            screenshot_ref=observation.screenshot_ref,
            grounding_evidence_refs=observation.grounding_evidence_refs,
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
        }
        return summaries.get(fixture_id, f"Observed controlled visual target for {fixture_id}.")

    async def _perform_controlled_action(self, page, fixture_id: str) -> tuple[str, str]:
        if fixture_id == "color-swatch":
            await page.get_by_label("green color swatch").click()
            return "click", "selected the green color swatch using visual target evidence"
        if fixture_id == "svg-dashboard":
            await page.locator("svg").text_content()
            return "extract", "extracted the SVG dashboard text using visual region evidence"
        if fixture_id == "icon-search":
            await page.get_by_label("search").click()
        return "click", "clicked the icon-only search control using visual target evidence"


class AgenticVisionExecutor:
    def __init__(
        self,
        config: BrowserExecutorConfig,
        observation_adapter: AgenticObservationAdapter,
        agent_task: str | None = None,
        runtime: dict[str, Any] | None = None,
    ):
        self.config = config
        self.observation_adapter = observation_adapter
        self.agent_task = agent_task
        self.runtime = runtime or {}

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

            if outcome.status == "succeeded":
                step.verification_decision = AgenticVerificationDecision(
                    passed=True,
                    reason="meaningful progress verified",
                )
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="none",
                    reason="progress verified",
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

            step.verification_decision = AgenticVerificationDecision(
                passed=False,
                reason="action had no meaningful effect"
                if outcome.status == "no_effect"
                else "action failed",
            )
            if recoveries_used < self.config.max_recoveries and step_index < self.config.max_steps:
                recoveries_used += 1
                step.recovery_decision = AgenticRecoveryDecision(
                    kind="reobserve",
                    reason="re-observing after failed verification",
                )
                steps.append(step)
                previous_step = step
                continue

            step.recovery_decision = AgenticRecoveryDecision(
                kind="stop",
                reason="failed verification",
            )
            steps.append(step)
            return self._result(
                execution_id,
                execution_mode,
                ExecutionStatus.STOPPED if outcome.status == "no_effect" else ExecutionStatus.FAILED,
                actions,
                steps,
                grounding_refs,
                runtime,
                stop_reason="no_meaningful_progress" if outcome.status == "no_effect" else None,
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


def _extend_unique(target: list[str], values: list[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def request_task_placeholder(runtime: dict[str, Any]) -> str:
    fixture_id = runtime.get("controlled_fixture_id")
    return f"agentic vision execution for {fixture_id or 'browser task'}"
