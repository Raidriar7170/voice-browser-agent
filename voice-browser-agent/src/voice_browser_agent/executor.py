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
    SanitizerStatus,
)
from .public_readonly import (
    PublicReadonlyPolicy,
    PublicReadonlyPolicyDecision,
    PublicReadonlyRoutingConfig,
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
    public_origin: str | None = None
    public_allowlist_id: str | None = None
    public_timeout_seconds: int = 15
    public_sanitizer_required: bool = True

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
                    "public_origin": self.config.public_origin,
                    "public_allowlist_id": self.config.public_allowlist_id,
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
                    },
                }
            )
            url_decision = public_policy.check_url(self.config.public_target_url)
            if not url_decision.allowed:
                return BrowserExecutionResult(
                    execution_id=execution_id,
                    execution_mode=execution_mode,
                    final_status=ExecutionStatus.STOPPED,
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
                max_steps=self.config.max_steps,
                timeout_seconds=self.config.public_timeout_seconds,
                sanitizer_required=self.config.public_sanitizer_required,
            )
        )

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
        stop = budget_stop or _detect_stop(payload, actions, raw_action_items)
        if public_policy is not None:
            public_stop = _detect_public_readonly_stop(
                public_policy,
                payload,
                actions,
                raw_action_items,
            )
            stop = public_stop or stop
        if stop is not None:
            status = ExecutionStatus.STOPPED
        failure_reason = payload.get("failure_reason")
        stop_reason = stop.reason if stop else payload.get("stop_reason")
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
) -> BrowserStateStop | None:
    top_level_state = _raw_browser_state(payload.get("browser_state", {}))
    if top_level_state:
        decision = policy.check_browser_state(top_level_state)
        if not decision.allowed:
            return BrowserStateStop(reason=decision.reason, detail=decision.detail or decision.reason)
    raw_action_items = raw_action_items or []
    for index, action in enumerate(actions):
        action_decision = policy.check_action(action.action_type, action.description)
        if not action_decision.allowed:
            return BrowserStateStop(
                reason=action_decision.reason,
                detail=action_decision.detail or action_decision.reason,
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
    ):
        self.task = task
        self.runtime = runtime
        self.vision_backend_url = vision_backend_url
        self.target_url = target_url
        self.timeout_seconds = timeout_seconds
        self.policy = policy

    async def run(self) -> dict[str, Any]:
        if not self.target_url:
            return {"status": "failed", "failure_reason": "missing_public_target", "actions": []}
        if self.policy is not None:
            decision = self.policy.check_url(self.target_url)
            if not decision.allowed:
                return {"status": "stopped", "stop_reason": decision.reason, "actions": []}

        from playwright.async_api import async_playwright

        actions: list[dict[str, Any]] = []
        browser = None
        context = None
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(**_chromium_launch_kwargs())
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
                blocked = self._blocked_state(browser_state)
                if blocked:
                    return _public_readonly_stopped(blocked.reason, actions)

                if self._has_step_budget(actions):
                    query = _extract_public_search_query(self.task)
                    if query:
                        search_result = await self._try_public_search(page, query)
                        if search_result is not None:
                            actions.append(search_result)
                            completed_search = True
                            blocked = self._blocked_state(search_result["browser_state"])
                            if blocked:
                                return _public_readonly_stopped(blocked.reason, actions)

                if self._has_step_budget(actions) and _wants_public_expand(self.task):
                    expand_result = await self._try_public_expand(page)
                    if expand_result is not None:
                        actions.append(expand_result)
                        completed_expand = True
                        blocked = self._blocked_state(expand_result["browser_state"])
                        if blocked:
                            return _public_readonly_stopped(blocked.reason, actions)

                if self._has_step_budget(actions):
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
                stop_reason = _should_stop_for_incomplete_public_task(
                    task=self.task,
                    action_count=len(actions),
                    max_steps=self.policy.max_steps if self.policy is not None else 3,
                    completed_search=completed_search,
                    completed_expand=completed_expand,
                )
                if stop_reason is not None:
                    return _public_readonly_stopped(stop_reason, actions)
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

        return {"status": "succeeded", "actions": actions}

    def _has_step_budget(self, actions: list[dict[str, Any]]) -> bool:
        max_steps = self.policy.max_steps if self.policy is not None else 3
        return len(actions) < max_steps

    def _blocked_state(self, state: dict[str, Any]) -> PublicReadonlyPolicyDecision | None:
        if self.policy is None:
            return None
        decision = self.policy.check_browser_state(state)
        return None if decision.allowed else decision

    async def _try_public_search(self, page: Any, query: str) -> dict[str, Any] | None:
        if self.policy is not None:
            decision = self.policy.check_action("search", f"read-only public search for {query}")
            if not decision.allowed:
                return {
                    "type": "inspect",
                    "description": f"search policy rejected: {decision.reason}",
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
        if self.policy is not None:
            decision = self.policy.check_action("click", description)
            if not decision.allowed:
                return None
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


def _public_readonly_stopped(reason: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "stopped",
        "stop_reason": reason,
        "actions": actions,
    }


def _chromium_launch_kwargs() -> dict[str, Any]:
    system_chrome = _system_chromium_executable()
    if system_chrome is not None:
        return {"headless": True, "executable_path": str(system_chrome)}
    return {"headless": True}


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
