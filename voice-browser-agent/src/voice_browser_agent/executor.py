from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, Field

from .models import BrowserActionEvent, BrowserTaskRequest, ExecutionStatus
from .safety import detect_browser_state_stop


class BrowserExecutorConfig(BaseModel):
    local_browser: bool = True
    remote_vision_backend_url: str | None = None
    dry_run: bool = True
    browser_channel: str = "chromium"
    max_steps: int = 8


class BrowserExecutionResult(BaseModel):
    execution_id: str
    final_status: ExecutionStatus
    actions: list[BrowserActionEvent] = Field(default_factory=list)
    grounding_evidence_refs: list[str] = Field(default_factory=list)
    failure_reason: str | None = None
    stop_reason: str | None = None
    agent_task: str
    runtime: dict[str, Any] = Field(default_factory=dict)


@dataclass
class BrowserExecutorAdapter:
    config: BrowserExecutorConfig
    agent_factory: Callable[..., Any] | None = None

    async def execute(self, request: BrowserTaskRequest, execution_id: str) -> BrowserExecutionResult:
        agent_task = self._build_agent_task(request)
        runtime = {
            "local_browser": self.config.local_browser,
            "remote_vision_backend_url": self.config.remote_vision_backend_url,
            "browser_channel": self.config.browser_channel,
            "max_steps": self.config.max_steps,
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
                final_status=ExecutionStatus.STOPPED,
                actions=[action],
                grounding_evidence_refs=action.grounding_evidence_refs,
                stop_reason="demo_preview_not_executed",
                agent_task=agent_task,
                runtime=runtime,
            )

        factory = self.agent_factory or self._load_vision_enhanced_agent
        agent = factory(task=agent_task, runtime=runtime, vision_backend_url=self.config.remote_vision_backend_url)
        raw_result = await agent.run()
        return self._coerce_result(execution_id, agent_task, runtime, raw_result)

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
        return "\n".join(parts)

    def _load_vision_enhanced_agent(self, **kwargs):
        from browser_use_vision import VisionEnhancedAgent

        return VisionEnhancedAgent(**kwargs)

    def _coerce_result(
        self,
        execution_id: str,
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
        stop = _detect_stop(payload, actions)
        if stop is not None:
            status = ExecutionStatus.STOPPED
        return BrowserExecutionResult(
            execution_id=execution_id,
            final_status=status,
            actions=actions,
            grounding_evidence_refs=grounding_refs,
            failure_reason=payload.get("failure_reason"),
            stop_reason=stop.reason if stop else payload.get("stop_reason"),
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
