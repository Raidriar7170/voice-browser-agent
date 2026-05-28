import json

import pytest

from voice_browser_agent.config import RuntimeConfig
from voice_browser_agent.executor import BrowserExecutorAdapter, BrowserExecutorConfig
from voice_browser_agent.executor import PublicReadonlyBrowserAgent
from voice_browser_agent.executor import _public_page_state, _should_stop_for_incomplete_public_task
from voice_browser_agent.models import (
    BrowserIntentType,
    BrowserTaskRequest,
    EvidencePrivacyState,
    ExecutionMode,
    ExecutionStatus,
    ExecutionTrace,
    PublicTaskCompletionState,
    PublicTaskContract,
    RouteDecision,
    RouteType,
    SanitizerStatus,
)
from voice_browser_agent.public_readonly import (
    PublicTaskCompletionVerifier,
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


def _runtime_with_public_task_contracts(enabled: bool = True) -> RuntimeConfig:
    python_contract = json.dumps(
        {
            "task_id": "python-docs-search",
            "task_kind": "documentation_search",
            "target_url_template": "https://docs.python.org/3/search.html?q={search_query}",
            "allowed_actions": ["navigate", "search", "extract"],
            "slots": ["target_site_hint", "search_query"],
            "completion_criteria": {
                "criteria_id": "python-docs-search-result",
                "required_proof": ["searched_query", "result_heading", "url_path"],
                "visible_markers": ["Search Results", "{search_query}"],
                "url_path_contains": "/search.html",
            },
            "max_steps": 3,
            "timeout_seconds": 12,
            "privacy_policy": "local_private",
        }
    )
    return RuntimeConfig(
        public_readonly_enabled=enabled,
        public_readonly_allowlist=(
            "openai-docs|OpenAI Docs|https://platform.openai.com/docs;"
            f"python-docs|Python Docs|https://docs.python.org/3/|python,docs,documentation|{python_contract}"
        ),
        public_readonly_max_steps=3,
        public_readonly_timeout_seconds=12,
        public_readonly_private_traces=True,
        public_readonly_sanitizer_required=True,
    )


def _routing_config(enabled: bool = True) -> PublicReadonlyRoutingConfig:
    return PublicReadonlyRoutingConfig.from_runtime_config(_runtime_with_public_task_contracts(enabled))


def test_public_task_contract_parses_policy_slots_criteria_and_limits():
    targets = parse_public_readonly_targets(_runtime_with_public_task_contracts(enabled=True))

    python_target = next(target for target in targets if target.allowlist_id == "python-docs")
    contract = python_target.task_contracts[0]

    assert contract.task_id == "python-docs-search"
    assert contract.task_kind == "documentation_search"
    assert contract.allowlist_id == "python-docs"
    assert contract.target_url_template == "https://docs.python.org/3/search.html?q={search_query}"
    assert contract.allowed_actions == ["navigate", "search", "extract"]
    assert contract.slots == ["target_site_hint", "search_query"]
    assert contract.completion_criteria.criteria_id == "python-docs-search-result"
    assert contract.completion_criteria.required_proof == ["searched_query", "result_heading", "url_path"]
    assert contract.max_steps == 3
    assert contract.timeout_seconds == 12
    assert contract.privacy_policy == "local_private"


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
    contract = json.dumps(
        {
            "task_id": "openai-docs-read",
            "task_kind": "direct_reference_read",
            "target_url": "https://platform.openai.com/docs",
            "allowed_actions": ["navigate", "extract"],
            "slots": ["target_site_hint", "read_target"],
            "completion_criteria": {"criteria_id": "openai-docs-title", "required_proof": ["final_title"]},
            "max_steps": 2,
            "timeout_seconds": 9,
            "privacy_policy": "local_private",
        }
    )
    default_config = RuntimeConfig()
    configured = RuntimeConfig(
        public_readonly_enabled=True,
        public_readonly_allowlist=f"openai-docs|OpenAI Docs|https://platform.openai.com/docs|openai,docs|{contract}",
        public_readonly_max_steps=2,
        public_readonly_timeout_seconds=9,
    )

    targets = parse_public_readonly_targets(configured)

    assert default_config.public_readonly_enabled is False
    assert targets[0].allowlist_id == "openai-docs"
    assert targets[0].label == "OpenAI Docs"
    assert targets[0].origin == "https://platform.openai.com"
    assert targets[0].task_contracts[0].task_id == "openai-docs-read"
    assert configured.public_readonly_max_steps == 2
    assert configured.public_readonly_timeout_seconds == 9


def test_route_selection_uses_allowlist_and_never_accepts_arbitrary_transcript_urls():
    decision = select_execution_route(
        _public_request("Search Python docs for pathlib"),
        _validation(),
        _confirmed(),
        public_readonly_config=_routing_config(enabled=True),
    )
    disabled = select_execution_route(
        _public_request("Search Python docs for pathlib"),
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
    assert decision.public_target_label == "Python Docs"
    assert decision.public_allowlist_id == "python-docs"
    assert decision.public_task_id == "python-docs-search"
    assert decision.public_task_kind == "documentation_search"
    assert decision.public_task_slots["search_query"] == "pathlib"
    assert decision.public_completion_criteria_id == "python-docs-search-result"
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


def test_allowlisted_origin_without_matching_task_contract_is_blocked_before_navigation():
    config = PublicReadonlyRoutingConfig.from_runtime_config(
        RuntimeConfig(
            public_readonly_enabled=True,
            public_readonly_allowlist="python-docs|Python Docs|https://docs.python.org/3/|python,docs",
        )
    )

    decision = select_execution_route(
        _public_request("Search Python docs for pathlib"),
        _validation(),
        _confirmed(),
        public_readonly_config=config,
    )

    assert decision.route_type is RouteType.BLOCKED
    assert decision.route_reason == "public_task_contract_mismatch"
    assert decision.public_readonly_enabled is False


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


class DisallowedPublicActionAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "expand",
                    "description": "expand public docs accordion",
                    "browser_state": {
                        "page_title": "Search results - Python documentation",
                        "url": "https://docs.python.org/3/search.html?q=pathlib",
                        "visible_text": "Search Results pathlib",
                    },
                }
            ],
        }


class BrowserErrorAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {
            "status": "failed",
            "failure_reason": "public_readonly_browser_error",
            "actions": [],
            "browser_state": {"page_title": "Timeout 12000ms exceeded while loading page"},
        }


class BrowserNetworkErrorAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {
            "status": "failed",
            "failure_reason": "public_readonly_browser_error",
            "actions": [],
            "browser_state": {"page_title": "net::ERR_NAME_NOT_RESOLVED at https://docs.python.org"},
        }


class FakeSearchLocator:
    def __init__(self):
        self.filled = False

    async def count(self):
        return 1

    async def fill(self, query, timeout=1000):
        self.filled = True

    async def press(self, key, timeout=1000):
        return None


class FakeSearchPage:
    url = "https://docs.python.org/3/"

    def __init__(self):
        self.search_locator = FakeSearchLocator()

    def locator(self, selector):
        return self.search_locator

    async def title(self):
        return "Python Documentation"

    async def wait_for_load_state(self, state, timeout=2000):
        return None


def _python_search_contract():
    return _routing_config(enabled=True).targets[1].task_contracts[0]


def _openai_direct_read_contract():
    return {
        "task_id": "openai-docs-read",
        "task_kind": "direct_reference_read",
        "allowlist_id": "openai-docs",
        "target_url": "https://platform.openai.com/docs",
        "allowed_actions": ["navigate", "extract"],
        "slots": ["target_site_hint"],
        "completion_criteria": {
            "criteria_id": "openai-docs-title",
            "required_proof": ["final_title"],
        },
        "max_steps": 3,
        "timeout_seconds": 12,
        "privacy_policy": "local_private",
    }


def _python_direct_read_contract():
    return {
        "task_id": "python-docs-direct-read",
        "task_kind": "direct_reference_read",
        "allowlist_id": "python-docs",
        "target_url": "https://docs.python.org/3/",
        "allowed_actions": ["navigate", "extract"],
        "slots": ["target_site_hint"],
        "completion_criteria": {
            "criteria_id": "python-docs-title",
            "required_proof": ["final_title"],
        },
        "max_steps": 3,
        "timeout_seconds": 12,
        "privacy_policy": "local_private",
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
            public_task_contract=_openai_direct_read_contract(),
            public_task_slots={"target_site_hint": "openai docs"},
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
async def test_public_readonly_executor_blocks_when_task_contract_is_missing():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            max_steps=3,
            public_target_url="https://docs.python.org/3/",
            public_target_label="Python Docs",
            public_origin="https://docs.python.org",
            public_allowlist_id="python-docs",
        ),
        agent_factory=PublicReadonlyEvidenceAgent,
    )

    result = await adapter.execute(_public_request("Search Python docs for pathlib"), "exec-public-no-contract")

    assert result.final_status is ExecutionStatus.BLOCKED
    assert result.stop_reason == "public_task_contract_mismatch"
    assert result.runtime["public_completion_state"] == "blocked"


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
            public_task_contract=_openai_direct_read_contract(),
            public_task_slots={"target_site_hint": "openai docs"},
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
            public_target_url="https://docs.python.org/3/",
            public_target_label="Python Docs",
            public_origin="https://docs.python.org",
            public_allowlist_id="python-docs",
            public_task_contract=_python_search_contract(),
            public_task_slots={"search_query": "pathlib"},
        ),
        agent_factory=TooManyActionsAgent,
    )

    result = await adapter.execute(_public_request(), execution_id="exec-public-budget")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "public_readonly_step_budget_reached"
    assert len(result.actions) == 3


@pytest.mark.asyncio
async def test_public_readonly_executor_enforces_task_contract_allowed_actions():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            max_steps=3,
            public_target_url="https://docs.python.org/3/",
            public_target_label="Python Docs",
            public_origin="https://docs.python.org",
            public_allowlist_id="python-docs",
            public_task_contract=_python_search_contract(),
            public_task_slots={"search_query": "pathlib"},
        ),
        agent_factory=DisallowedPublicActionAgent,
    )

    result = await adapter.execute(_public_request("Search Python docs for pathlib"), "exec-public-action-policy")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "public_task_action_not_allowed"
    assert result.runtime["public_completion_state"] == "stopped"


@pytest.mark.asyncio
async def test_public_readonly_agent_blocks_disallowed_task_action_before_search():
    page = FakeSearchPage()
    agent = PublicReadonlyBrowserAgent(
        task="Search Python docs for pathlib",
        runtime={
            "public_origin": "https://docs.python.org",
            "public_task_contract": _python_direct_read_contract(),
        },
        target_url="https://docs.python.org/3/",
        policy=PublicReadonlyPolicy(_routing_config(enabled=True)),
    )

    result = await agent._try_public_search(page, "pathlib")

    assert result["type"] == "policy_stop"
    assert result["stop_reason"] == "public_task_action_not_allowed"
    assert page.search_locator.filled is False


@pytest.mark.asyncio
async def test_public_readonly_executor_maps_browser_timeout_to_site_variance():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            max_steps=3,
            public_target_url="https://docs.python.org/3/search.html?q=pathlib",
            public_target_label="Python Docs",
            public_origin="https://docs.python.org",
            public_allowlist_id="python-docs",
            public_task_contract=_python_search_contract(),
            public_task_slots={"search_query": "pathlib"},
        ),
        agent_factory=BrowserErrorAgent,
    )

    result = await adapter.execute(_public_request("Search Python docs for pathlib"), "exec-public-timeout")

    assert result.final_status is ExecutionStatus.FAILED
    assert result.failure_reason == "public_task_timeout"
    assert result.runtime["public_completion_state"] == "failed"
    assert result.runtime["public_task_completion"]["failure_reason"] == "public_task_timeout"


@pytest.mark.asyncio
async def test_public_readonly_executor_maps_browser_network_error_to_site_variance():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
            max_steps=3,
            public_target_url="https://docs.python.org/3/search.html?q=pathlib",
            public_target_label="Python Docs",
            public_origin="https://docs.python.org",
            public_allowlist_id="python-docs",
            public_task_contract=_python_search_contract(),
            public_task_slots={"search_query": "pathlib"},
        ),
        agent_factory=BrowserNetworkErrorAgent,
    )

    result = await adapter.execute(
        _public_request("Search Python docs for pathlib"),
        "exec-public-network",
    )

    assert result.final_status is ExecutionStatus.FAILED
    assert result.failure_reason == "public_task_network_error"
    assert result.runtime["public_completion_state"] == "failed"
    assert result.runtime["public_task_completion"]["failure_reason"] == "public_task_network_error"


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
            public_task_contract=_openai_direct_read_contract(),
            public_task_slots={"target_site_hint": "openai docs"},
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


def test_public_task_completion_verifier_requires_task_specific_search_proof():
    contract = _routing_config(enabled=True).targets[1].task_contracts[0]
    verifier = PublicTaskCompletionVerifier(contract)
    completed = verifier.verify(
        requested_slots={"search_query": "pathlib"},
        actions=[
            {
                "type": "search",
                "description": "searched public docs for pathlib",
                "browser_state": {
                    "page_title": "Search results - Python documentation",
                    "url": "https://docs.python.org/3/search.html?q=pathlib",
                    "visible_text": "Search Results pathlib pathlib.Path",
                },
            }
        ],
    )
    opened_only = verifier.verify(
        requested_slots={"search_query": "pathlib"},
        actions=[
            {
                "type": "navigate",
                "description": "opened Python docs",
                "browser_state": {
                    "page_title": "3.14.0 Documentation",
                    "url": "https://docs.python.org/3/",
                    "visible_text": "Python documentation",
                },
            }
        ],
    )

    assert completed.completion_state is PublicTaskCompletionState.COMPLETED
    assert completed.observed_proof["searched_query"] == "pathlib"
    assert completed.observed_proof["url_path"] == "/3/search.html"
    assert opened_only.completion_state is PublicTaskCompletionState.PARTIAL
    assert opened_only.stop_reason == "missing_public_task_completion"
    assert "searched_query" in opened_only.unmet_criteria


def test_public_task_completion_verifier_records_visible_marker_proof():
    contract = PublicTaskContract.model_validate(
        {
            "task_id": "mdn-fetch-read",
            "task_kind": "direct_reference_read",
            "allowlist_id": "mdn-docs",
            "target_url": "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API",
            "allowed_actions": ["navigate", "extract"],
            "slots": ["target_site_hint"],
            "completion_criteria": {
                "criteria_id": "mdn-fetch-visible-reference",
                "required_proof": ["final_title", "visible_marker"],
                "visible_markers": ["Fetch API"],
            },
            "max_steps": 2,
            "timeout_seconds": 10,
            "privacy_policy": "local_private",
        }
    )
    verifier = PublicTaskCompletionVerifier(contract)

    completed = verifier.verify(
        requested_slots={"target_site_hint": "mdn"},
        actions=[
            {
                "type": "extract",
                "description": "read visible MDN reference",
                "browser_state": {
                    "page_title": "Fetch API - Web APIs | MDN",
                    "url": "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API",
                    "visible_text": "Fetch API provides an interface for fetching resources.",
                },
            }
        ],
    )

    assert completed.completion_state is PublicTaskCompletionState.COMPLETED
    assert completed.observed_proof["visible_marker"] == "Fetch API"


def test_public_task_completion_verifier_applies_title_constraint_and_safe_markers():
    contract = PublicTaskContract.model_validate(
        {
            "task_id": "openai-docs-read",
            "task_kind": "direct_reference_read",
            "allowlist_id": "openai-docs",
            "target_url": "https://platform.openai.com/docs",
            "allowed_actions": ["navigate", "extract"],
            "slots": ["target_site_hint"],
            "completion_criteria": {
                "criteria_id": "openai-docs-title",
                "required_proof": ["final_title", "visible_marker"],
                "title_contains": "OpenAI Docs",
                "visible_markers": ["{missing_slot}", "OpenAI"],
            },
            "max_steps": 2,
            "timeout_seconds": 8,
            "privacy_policy": "local_private",
        }
    )
    verifier = PublicTaskCompletionVerifier(contract)

    wrong_title = verifier.verify(
        requested_slots={"target_site_hint": "openai docs"},
        actions=[
            {
                "type": "extract",
                "description": "read public docs",
                "browser_state": {
                    "page_title": "Different Docs",
                    "visible_text": "OpenAI platform overview",
                },
            }
        ],
    )
    completed = verifier.verify(
        requested_slots={"target_site_hint": "openai docs"},
        actions=[
            {
                "type": "extract",
                "description": "read public docs",
                "browser_state": {
                    "page_title": "OpenAI Docs",
                    "visible_text": "OpenAI platform overview",
                },
            }
        ],
    )

    assert "final_title" in wrong_title.unmet_criteria
    assert completed.completion_state is PublicTaskCompletionState.COMPLETED


def test_public_task_completion_verifier_classifies_site_variance_outcomes():
    contract = _routing_config(enabled=True).targets[1].task_contracts[0]
    verifier = PublicTaskCompletionVerifier(contract)

    timeout = verifier.classify_variance("timeout")
    missing_selector = verifier.classify_variance("missing_selector")
    redirect = verifier.classify_variance("redirect_off_allowlist")
    login = verifier.classify_variance("login_required")
    network = verifier.classify_variance("network_error")
    budget = verifier.classify_variance("step_budget_exhausted")
    blocked = verifier.classify_blocked("public_task_contract_mismatch")

    assert timeout.completion_state is PublicTaskCompletionState.FAILED
    assert timeout.failure_reason == "public_task_timeout"
    assert missing_selector.completion_state is PublicTaskCompletionState.PARTIAL
    assert missing_selector.stop_reason == "public_task_missing_selector"
    assert redirect.completion_state is PublicTaskCompletionState.STOPPED
    assert redirect.stop_reason == "target_not_allowlisted"
    assert login.completion_state is PublicTaskCompletionState.STOPPED
    assert login.stop_reason == "login_required"
    assert network.completion_state is PublicTaskCompletionState.FAILED
    assert network.failure_reason == "public_task_network_error"
    assert budget.completion_state is PublicTaskCompletionState.PARTIAL
    assert budget.stop_reason == "public_readonly_step_budget_reached"
    assert blocked.completion_state is PublicTaskCompletionState.BLOCKED
    assert blocked.stop_reason == "public_task_contract_mismatch"
