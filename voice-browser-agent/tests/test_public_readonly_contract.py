import json

import pytest

from voice_browser_agent.config import RuntimeConfig
from voice_browser_agent.executor import BrowserExecutorAdapter, BrowserExecutorConfig
from voice_browser_agent.executor import _public_page_state, _should_stop_for_incomplete_public_task
from voice_browser_agent.models import (
    BrowserIntentType,
    BrowserTaskRequest,
    EvidencePrivacyState,
    ExecutionMode,
    ExecutionStatus,
    ExecutionTrace,
    RouteDecision,
    RouteType,
    SanitizerStatus,
)
from voice_browser_agent.public_readonly import (
    PublicReadonlyPolicy,
    PublicReadonlyRoutingConfig,
    parse_public_readonly_targets,
)
from voice_browser_agent.routing import select_execution_route
from voice_browser_agent.trace_writer import TraceWriter, sanitize_trace_dict
from voice_browser_agent.models import ConfirmationDecision, ConfirmationState, ValidationResult


def _public_request(text: str = "打开 OpenAI 的公开文档页面") -> BrowserTaskRequest:
    return BrowserTaskRequest(
        task=text,
        intent_type=BrowserIntentType.SEARCH_OPEN,
        constraints=["public read-only page only", "do not log in"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "payment_or_checkout", "irreversible_submit"],
    )


def _validation() -> ValidationResult:
    return ValidationResult(accepted=True, reason="accepted", issues=[], requires_confirmation=False)


def _confirmed() -> ConfirmationDecision:
    return ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="no confirmation required")


def _routing_config(enabled: bool = True) -> PublicReadonlyRoutingConfig:
    return PublicReadonlyRoutingConfig.from_runtime_config(
        RuntimeConfig(
            public_readonly_enabled=enabled,
            public_readonly_allowlist=(
                "openai-docs|OpenAI Docs|https://platform.openai.com/docs;"
                "python-docs|Python Docs|https://docs.python.org/3/"
            ),
            public_readonly_max_steps=3,
            public_readonly_timeout_seconds=12,
            public_readonly_private_traces=True,
            public_readonly_sanitizer_required=True,
        )
    )


def test_public_readonly_model_schema_records_route_privacy_and_sanitizer_state():
    decision = RouteDecision(
        route_type=RouteType.PUBLIC_READONLY,
        execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
        evidence_mode="live_public_readonly",
        route_reason="matched allowlisted public target",
        user_message="Running local isolated public-readonly execution for OpenAI Docs.",
        live_evidence_eligible=False,
        public_readonly_enabled=True,
        public_target_label="OpenAI Docs",
        public_origin="https://platform.openai.com",
        public_allowlist_id="openai-docs",
        evidence_privacy_state=EvidencePrivacyState.LOCAL_PRIVATE,
        sanitizer_status=SanitizerStatus.PENDING,
        execution_limits={"max_steps": 3, "timeout_seconds": 12},
    )
    trace = ExecutionTrace(
        execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
        route_decision=decision,
        evidence_privacy_state=EvidencePrivacyState.LOCAL_PRIVATE,
        sanitizer_status=SanitizerStatus.PENDING,
    )

    payload = trace.model_dump(mode="json")

    assert payload["execution_mode"] == "live_public_readonly"
    assert payload["route_decision"]["route_type"] == "public_readonly"
    assert payload["route_decision"]["public_allowlist_id"] == "openai-docs"
    assert payload["route_decision"]["public_origin"] == "https://platform.openai.com"
    assert payload["route_decision"]["evidence_privacy_state"] == "local_private"
    assert payload["route_decision"]["sanitizer_status"] == "pending"
    assert payload["evidence_privacy_state"] == "local_private"


def test_public_readonly_config_parses_allowlist_and_limits_without_enabling_by_default():
    default_config = RuntimeConfig()
    configured = RuntimeConfig(
        public_readonly_enabled=True,
        public_readonly_allowlist="openai-docs|OpenAI Docs|https://platform.openai.com/docs",
        public_readonly_max_steps=2,
        public_readonly_timeout_seconds=9,
    )

    targets = parse_public_readonly_targets(configured)

    assert default_config.public_readonly_enabled is False
    assert targets[0].allowlist_id == "openai-docs"
    assert targets[0].label == "OpenAI Docs"
    assert targets[0].origin == "https://platform.openai.com"
    assert configured.public_readonly_max_steps == 2
    assert configured.public_readonly_timeout_seconds == 9


def test_route_selection_uses_allowlist_and_never_accepts_arbitrary_transcript_urls():
    decision = select_execution_route(
        _public_request(),
        _validation(),
        _confirmed(),
        public_readonly_config=_routing_config(enabled=True),
    )
    disabled = select_execution_route(
        _public_request(),
        _validation(),
        _confirmed(),
        public_readonly_config=_routing_config(enabled=False),
    )
    non_allowlisted = select_execution_route(
        _public_request("打开 https://evil.example/private 页面"),
        _validation(),
        _confirmed(),
        public_readonly_config=_routing_config(enabled=True),
    )
    explicit_url_with_keyword = select_execution_route(
        _public_request("打开 https://evil.example/private 页面，并参考 OpenAI Docs"),
        _validation(),
        _confirmed(),
        public_readonly_config=_routing_config(enabled=True),
    )
    unsafe_url_with_keyword = select_execution_route(
        _public_request("打开 file:///Users/example/private.txt 页面，并参考 OpenAI Docs"),
        _validation(),
        _confirmed(),
        public_readonly_config=_routing_config(enabled=True),
    )
    mixed_urls = select_execution_route(
        _public_request(
            "打开 https://platform.openai.com/docs 后再看 https://evil.example/private"
        ),
        _validation(),
        _confirmed(),
        public_readonly_config=_routing_config(enabled=True),
    )
    manual_override = select_execution_route(
        _public_request("打开 https://evil.example/private 页面"),
        _validation(),
        _confirmed(),
        public_readonly_config=_routing_config(enabled=True),
        requested_execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
    )

    assert decision.route_type is RouteType.PUBLIC_READONLY
    assert decision.execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY
    assert decision.public_target_label == "OpenAI Docs"
    assert decision.public_allowlist_id == "openai-docs"
    assert decision.execution_limits == {"max_steps": 3, "timeout_seconds": 12}
    assert disabled.route_type is RouteType.DEMO_PREVIEW
    assert disabled.route_reason == "public_readonly_disabled"
    assert non_allowlisted.route_type is RouteType.BLOCKED
    assert non_allowlisted.route_reason == "public_readonly_target_not_allowlisted"
    assert explicit_url_with_keyword.route_type is RouteType.BLOCKED
    assert explicit_url_with_keyword.route_reason == "public_readonly_target_not_allowlisted"
    assert unsafe_url_with_keyword.route_type is RouteType.BLOCKED
    assert unsafe_url_with_keyword.route_reason == "public_readonly_target_not_allowlisted"
    assert mixed_urls.route_type is RouteType.BLOCKED
    assert mixed_urls.route_reason == "public_readonly_target_not_allowlisted"
    assert manual_override.route_type is RouteType.BLOCKED
    assert manual_override.route_reason == "public_readonly_override_not_allowed"


def test_public_readonly_policy_blocks_unsafe_urls_mutations_and_sensitive_state():
    policy = PublicReadonlyPolicy(_routing_config(enabled=True))

    assert policy.check_url("https://platform.openai.com/docs").allowed is True
    assert policy.check_url("file:///Users/secret.txt").reason == "unsafe_protocol"
    assert policy.check_url("https://user:pass@platform.openai.com/docs").reason == "credentialed_url"
    assert policy.check_url("http://127.0.0.1:8000/private").reason == "private_network_target"
    assert policy.check_url("http://192.168.1.20/internal").reason == "private_network_target"
    assert policy.check_url("https://evil.example/docs").reason == "target_not_allowlisted"
    assert policy.check_action("search", "fill public docs search field").allowed is True
    assert policy.check_action("submit", "submit login form").reason == "mutation_action_blocked"
    assert policy.check_action("download", "download report").reason == "mutation_action_blocked"
    assert (
        policy.check_browser_state(
            {
                "url": "https://platform.openai.com/docs",
                "title": "Sign in",
                "visible_text": "Upload a file or log in to continue",
            }
        ).reason
        in {"login_required", "file_transfer"}
    )
    assert policy.max_steps == 3


class PublicReadonlyEvidenceAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "extract",
                    "description": "read OpenAI Docs page title",
                    "grounding_evidence_refs": ["grounding/public-readonly/openai-docs.json"],
                    "browser_state": {
                        "page_title": "OpenAI Docs",
                        "origin": "https://platform.openai.com",
                        "visible_text": "third-party page body that must remain local only",
                        "cookies": ["session=secret"],
                        "browser_profile_path": "/Users/example/Library/Profile",
                    },
                }
            ],
        }


class EmptyEvidenceAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {"status": "succeeded", "actions": []}


class TooManyActionsAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "navigate",
                    "description": "open public docs",
                    "browser_state": {"page_title": "OpenAI Docs"},
                },
                {
                    "type": "search",
                    "description": "search public docs",
                    "browser_state": {"page_title": "OpenAI Docs Search"},
                },
                {
                    "type": "extract",
                    "description": "read public result",
                    "browser_state": {"page_title": "OpenAI Docs Result"},
                },
                {
                    "type": "expand",
                    "description": "expand public read-only section",
                    "browser_state": {"page_title": "OpenAI Docs Expanded"},
                },
            ],
        }


class SensitiveVisibleStateAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "extract",
                    "description": "observe public page",
                    "browser_state": {
                        "page_title": "OpenAI Docs",
                        "url": "https://platform.openai.com/docs",
                        "visible_text": "Log in to continue",
                    },
                }
            ],
        }


@pytest.mark.asyncio
async def test_public_readonly_executor_records_isolation_and_sanitizes_action_state():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            max_steps=3,
            public_target_url="https://platform.openai.com/docs",
            public_target_label="OpenAI Docs",
            public_origin="https://platform.openai.com",
            public_allowlist_id="openai-docs",
            public_timeout_seconds=12,
            public_sanitizer_required=True,
        ),
        agent_factory=PublicReadonlyEvidenceAgent,
    )

    result = await adapter.execute(_public_request(), execution_id="exec-public")
    serialized = json.dumps(result.model_dump(mode="json"), ensure_ascii=False)

    assert result.execution_mode is ExecutionMode.LIVE_PUBLIC_READONLY
    assert result.final_status is ExecutionStatus.SUCCEEDED
    assert result.runtime["browser_context"]["isolation"] == "fresh_ephemeral"
    assert result.runtime["browser_context"]["persistent_profile"] is False
    assert result.runtime["browser_context"]["cookies_reused"] is False
    assert result.runtime["public_allowlist_id"] == "openai-docs"
    assert result.actions[0].browser_state["page_title"] == "OpenAI Docs"
    assert "visible_text" not in result.actions[0].browser_state
    assert "cookies" not in serialized
    assert "browser_profile_path" not in serialized
    assert "third-party page body" not in serialized
    assert "visible_text" not in serialized
    assert "https://platform.openai.com/docs" not in serialized
    assert '"url"' not in serialized
    assert "public_target_url" not in serialized


@pytest.mark.asyncio
async def test_public_readonly_executor_rejects_missing_evidence():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            public_target_url="https://platform.openai.com/docs",
            public_target_label="OpenAI Docs",
            public_origin="https://platform.openai.com",
            public_allowlist_id="openai-docs",
        ),
        agent_factory=EmptyEvidenceAgent,
    )

    result = await adapter.execute(_public_request(), execution_id="exec-public-empty")

    assert result.final_status is ExecutionStatus.FAILED
    assert result.failure_reason == "public_readonly_missing_evidence"


@pytest.mark.asyncio
async def test_public_readonly_executor_stops_when_step_budget_is_exceeded():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            max_steps=3,
            public_target_url="https://platform.openai.com/docs",
            public_target_label="OpenAI Docs",
            public_origin="https://platform.openai.com",
            public_allowlist_id="openai-docs",
        ),
        agent_factory=TooManyActionsAgent,
    )

    result = await adapter.execute(_public_request(), execution_id="exec-public-budget")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "public_readonly_step_budget_reached"
    assert len(result.actions) == 3


@pytest.mark.asyncio
async def test_public_readonly_policy_checks_raw_visible_state_before_sanitizing():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            max_steps=3,
            public_target_url="https://platform.openai.com/docs",
            public_target_label="OpenAI Docs",
            public_origin="https://platform.openai.com",
            public_allowlist_id="openai-docs",
        ),
        agent_factory=SensitiveVisibleStateAgent,
    )

    result = await adapter.execute(_public_request(), execution_id="exec-public-sensitive")
    serialized = json.dumps(result.model_dump(mode="json"), ensure_ascii=False)

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "login_required"
    assert "visible_text" not in serialized
    assert "Log in to continue" not in serialized


def test_public_readonly_sanitizer_keeps_public_trace_local_private_until_approved(tmp_path):
    trace = ExecutionTrace(
        execution_id="exec-public-sanitize",
        execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
        evidence_privacy_state=EvidencePrivacyState.LOCAL_PRIVATE,
        sanitizer_status=SanitizerStatus.PENDING,
    )
    trace.execution_runtime = {
        "public_origin": "https://platform.openai.com",
        "raw_page_text": "third party body",
        "raw_screenshot": "/tmp/raw-public.png",
        "cookies": ["secret"],
        "profile_path": "/Users/example/Profile",
        "local_file_uri": "file:///Users/example/private.txt",
        "third_party_private_markers": ["email@example.com"],
    }
    trace.add_browser_action(
        "extract",
        "read public page title",
    ).browser_state = {
        "page_title": "OpenAI Docs",
        "url": "https://platform.openai.com/docs",
        "visible_text": "raw third-party visible page content",
    }

    writer = TraceWriter(tmp_path)
    exported = writer.export_sanitized(trace)
    text = json.dumps(exported, ensure_ascii=False)

    assert exported["evidence_privacy_state"] == "local_private"
    assert exported["sanitizer_status"] == "pending"
    assert "https://platform.openai.com" in text
    assert "raw_page_text" not in text
    assert "visible_text" not in text
    assert '"url"' not in text
    assert "https://platform.openai.com/docs" not in text
    assert "raw third-party visible page content" not in text
    assert "raw_screenshot" not in text
    assert "cookies" not in text
    assert "/Users/example" not in text
    assert "email@example.com" not in text
    assert sanitize_trace_dict({"public_url": "https://example.com/private"}) == {}


class FakeLocator:
    async def inner_text(self, timeout=1000):
        return "visible third-party body"


class FakePage:
    url = "https://evil.example/off-allowlist"

    async def title(self):
        return "Redirected Page"

    def locator(self, selector):
        return FakeLocator()


@pytest.mark.asyncio
async def test_public_page_state_records_current_url_for_post_navigation_policy():
    state = await _public_page_state(FakePage(), origin="https://platform.openai.com")

    assert state["url"] == "https://evil.example/off-allowlist"
    assert state["origin"] == "https://platform.openai.com"


def test_public_readonly_incomplete_requested_task_stops_when_budget_is_exhausted():
    stop_reason = _should_stop_for_incomplete_public_task(
        task="search public docs for pathlib",
        action_count=1,
        max_steps=1,
        completed_search=False,
        completed_expand=False,
    )

    assert stop_reason == "public_readonly_step_budget_reached"
