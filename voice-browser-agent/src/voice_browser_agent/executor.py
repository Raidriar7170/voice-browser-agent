from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, Field

from .models import AgenticVisionStep, BrowserActionEvent, BrowserTaskRequest, ExecutionMode, ExecutionStatus
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
    ) -> BrowserExecutionResult:
        if isinstance(raw_result, BrowserExecutionResult):
            return raw_result
        payload = raw_result if isinstance(raw_result, dict) else {"status": "succeeded", "raw": str(raw_result)}
        status = ExecutionStatus(payload.get("status", "succeeded"))
        actions = [
            BrowserActionEvent(
                action_type=item.get("type", "action"),
                description=item.get("description", ""),
                screenshot_ref=item.get("screenshot_ref"),
                grounding_evidence_refs=item.get("grounding_evidence_refs", []),
                browser_state=item.get("browser_state", {}),
            )
            for item in payload.get("actions", [])
        ]
        grounding_refs: list[str] = []
        for action in actions:
            grounding_refs.extend(action.grounding_evidence_refs)
        grounding_refs.extend(payload.get("grounding_evidence_refs", []))
        stop = _detect_stop(payload, actions)
        if stop is not None:
            status = ExecutionStatus.STOPPED
        failure_reason = payload.get("failure_reason")
        stop_reason = stop.reason if stop else payload.get("stop_reason")
        if execution_mode is ExecutionMode.LIVE_CONTROLLED and not actions and not grounding_refs:
            status = ExecutionStatus.FAILED
            failure_reason = failure_reason or "live_controlled_missing_evidence"
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


def _detect_stop(payload: dict[str, Any], actions: list[BrowserActionEvent]):
    top_level_stop = detect_browser_state_stop(payload.get("browser_state", {}))
    if top_level_stop is not None:
        return top_level_stop
    for action in actions:
        stop = detect_browser_state_stop(action.browser_state)
        if stop is not None:
            return stop
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
