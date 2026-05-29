import json
from pathlib import Path

from fastapi.testclient import TestClient

from voice_browser_agent.app import create_app
from voice_browser_agent.asr import FallbackASRAdapter
from voice_browser_agent.config import RuntimeConfig
from voice_browser_agent.models import (
    BrowserIntentType,
    BrowserTaskRequest,
    ConfirmationDecision,
    ConfirmationState,
    ExecutionMode,
    RouteDecision,
    RouteType,
    ValidationResult,
)
from voice_browser_agent.public_readonly import PublicReadonlyRoutingConfig
from voice_browser_agent.routing import select_execution_route


WAV_BYTES = b"RIFF\x24\x00\x00\x00WAVEfmt "


def _public_task_config() -> PublicReadonlyRoutingConfig:
    contract = json.dumps(
        {
            "task_id": "python-docs-search",
            "task_kind": "documentation_search",
            "target_url_template": "https://docs.python.org/3/search.html?q={search_query}",
            "allowed_actions": ["navigate", "search", "extract"],
            "slots": ["target_site_hint", "search_query"],
            "completion_criteria": {
                "criteria_id": "python-docs-search-result",
                "required_proof": ["searched_query", "result_heading", "url_path"],
            },
            "max_steps": 3,
            "timeout_seconds": 12,
            "privacy_policy": "local_private",
        }
    )
    return PublicReadonlyRoutingConfig.from_runtime_config(
        RuntimeConfig(
            public_readonly_enabled=True,
            public_readonly_allowlist=f"python-docs|Python Docs|https://docs.python.org/3/|python,docs|{contract}",
            public_readonly_max_steps=5,
            public_readonly_timeout_seconds=20,
        )
    )


def _github_task_config(enabled: bool = True) -> PublicReadonlyRoutingConfig:
    contracts = json.dumps(
        [
            {
                "task_id": "github-repo-search",
                "task_kind": "github-repo-search",
                "target_url_template": "https://github.com/search?q={search_query}&type=repositories",
                "allowed_actions": ["navigate", "search", "extract"],
                "slots": ["target_site_hint", "search_query"],
                "completion_criteria": {
                    "criteria_id": "github-repo-search-results",
                    "required_proof": [
                        "searched_query",
                        "search_page_state",
                        "repository_result_marker",
                    ],
                    "visible_markers": ["Repositories", "{search_query}"],
                    "url_path_contains": "/search",
                    "title_contains": "Search",
                },
                "max_steps": 3,
                "timeout_seconds": 15,
                "privacy_policy": "local_private",
            },
            {
                "task_id": "github-public-repo-read",
                "task_kind": "github-public-repo-read",
                "target_url_template": "https://github.com/{owner}/{repo}",
                "allowed_actions": ["navigate", "extract"],
                "slots": ["target_site_hint", "owner", "repo"],
                "completion_criteria": {
                    "criteria_id": "github-public-repo-page",
                    "required_proof": [
                        "repo_slug",
                        "repo_page_title",
                        "readme_or_description_marker",
                    ],
                    "visible_markers": ["README", "{repo}", "{owner}"],
                },
                "max_steps": 2,
                "timeout_seconds": 15,
                "privacy_policy": "local_private",
            },
        ]
    )
    return PublicReadonlyRoutingConfig.from_runtime_config(
        RuntimeConfig(
            public_readonly_enabled=enabled,
            public_readonly_allowlist=f"github|GitHub|https://github.com/|github,repo,repositories|{contracts}",
            public_readonly_max_steps=5,
            public_readonly_timeout_seconds=20,
        )
    )


def _useful_task_config(enabled: bool = True) -> PublicReadonlyRoutingConfig:
    contracts = json.dumps(
        [
            {
                "task_id": "pypi-package-read",
                "task_kind": "package_metadata_read",
                "target_url_template": "https://pypi.org/project/{package_name}/",
                "allowed_actions": ["navigate", "extract"],
                "slots": ["target_site_hint", "package_ecosystem", "package_name"],
                "task_category": "package_metadata",
                "target_class": "package_metadata",
                "completion_criteria": {
                    "criteria_id": "pypi-package-metadata",
                    "required_proof": ["package_name", "package_metadata_marker", "final_title"],
                    "visible_markers": ["{package_name}", "Project description"],
                    "url_path_contains": "/project/{package_name}/",
                },
                "max_steps": 2,
                "timeout_seconds": 10,
                "privacy_policy": "local_private",
            },
            {
                "task_id": "github-release-notes-read",
                "task_kind": "release_notes_read",
                "target_url_template": "https://github.com/{owner}/{repo}/releases",
                "allowed_actions": ["navigate", "extract"],
                "slots": ["target_site_hint", "owner", "repo", "release_target"],
                "task_category": "release_notes",
                "target_class": "release_notes",
                "completion_criteria": {
                    "criteria_id": "github-release-notes",
                    "required_proof": ["repo_slug", "release_notes_marker", "final_title"],
                    "visible_markers": ["Releases", "{repo}"],
                    "url_path_contains": "/{owner}/{repo}/releases",
                },
                "max_steps": 2,
                "timeout_seconds": 12,
                "privacy_policy": "local_private",
            },
        ]
    )
    return PublicReadonlyRoutingConfig.from_runtime_config(
        RuntimeConfig(
            public_readonly_enabled=enabled,
            public_readonly_allowlist=(
                "pypi|PyPI|https://pypi.org/|pypi,package,metadata|"
                f"{contracts};"
                "github|GitHub|https://github.com/|github,release,releases|"
                f"{contracts}"
            ),
            public_readonly_max_steps=5,
            public_readonly_timeout_seconds=20,
        )
    )


class IconSearchASRAdapter:
    name = "route-smoke-asr"

    async def transcribe(self, command_input):
        return FallbackASRAdapter.from_text(
            text="点右上角搜索图标",
            command_input=command_input,
            adapter_name=self.name,
            confidence=0.92,
            diagnostics={"source": "route-selection-test"},
        )


def test_route_decision_schema_is_serializable_and_sanitized():
    decision = RouteDecision(
        route_type=RouteType.CONTROLLED_LIVE,
        execution_mode="live_controlled",
        evidence_mode="live_controlled",
        controlled_fixture_id="icon-search",
        controlled_target_ref="demo/pages/icon_only_toolbar.html",
        route_reason="matched visual search icon command",
        user_message="Running controlled local icon-search task.",
        live_evidence_eligible=True,
    )

    payload = decision.model_dump(mode="json")

    assert payload["route_type"] == "controlled_live"
    assert payload["controlled_fixture_id"] == "icon-search"
    assert payload["live_evidence_eligible"] is True
    assert "controlled_target_url" not in json.dumps(payload)


def test_typed_transcript_routes_to_controlled_live_without_manual_dropdowns(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.post(
        "/api/executions",
        json={"transcript_text": "点击右上角的放大镜图标"},
    )

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    assert route["route_type"] == "controlled_live"
    assert route["execution_mode"] == "live_controlled"
    assert route["evidence_mode"] == "live_controlled"
    assert route["controlled_fixture_id"] == "icon-search"
    assert route["controlled_target_ref"] == "demo/pages/icon_only_toolbar.html"
    assert route["live_evidence_eligible"] is True
    assert body["execution_mode"] == "live_controlled"
    assert body["final_status"] == "succeeded"
    assert body["browser_actions"] or body["agentic_steps"]


def test_reviewed_audio_uses_same_route_selection_and_preserves_provenance(tmp_path):
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.asr_orchestrator.primary = IconSearchASRAdapter()
    client = TestClient(app)

    ingest = client.post(
        "/api/ingest",
        files={"file": ("command.wav", WAV_BYTES, "audio/wav")},
    )
    audio_id = ingest.json()["audio_id"]

    response = client.post(
        "/api/executions",
        json={
            "audio_id": audio_id,
            "reviewed_transcript_text": "点击右上角的放大镜图标",
        },
    )

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    assert route["route_type"] == "controlled_live"
    assert route["controlled_fixture_id"] == "icon-search"
    assert body["execution_runtime"]["evidence_mode"] == "real_voice_controlled"
    assert body["execution_runtime"]["input_source"] == "audio"
    assert body["execution_runtime"]["transcript_review"]["status"] == "edited"
    assert body["transcript"]["metadata"]["adapter_name"] == "route-smoke-asr"
    assert "storage_path" not in json.dumps(body, ensure_ascii=False)


def test_public_showcase_command_routes_to_controlled_showcase_not_real_public_web(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.post("/api/executions", json={"transcript_text": "打开 GitHub"})

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    assert route["route_type"] == "controlled_live"
    assert route["controlled_fixture_id"] == "github-showcase"
    assert route["controlled_target_ref"] == "demo/pages/github_showcase.html"
    assert "github.com" not in json.dumps(body, ensure_ascii=False).lower()
    assert "file:///users/" not in json.dumps(body, ensure_ascii=False).lower()
    assert "controlled_target_url" not in json.dumps(body, ensure_ascii=False)
    assert body["execution_runtime"]["evidence_mode"] == "controlled_showcase"
    assert body["execution_mode"] == "live_controlled"


def test_github_search_prefers_real_public_readonly_when_enabled_and_contracted():
    request = BrowserTaskRequest(
        task="Search GitHub repositories for agent tooling",
        intent_type=BrowserIntentType.SEARCH_OPEN,
        constraints=["bounded single browser task", "public_readonly"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "stop_if_login_required"],
        public_task_slots={
            "target_site_hint": "github",
            "task_kind_hint": "github-repo-search",
            "search_query": "agent tooling",
            "read_only_intent": True,
        },
    )

    route = select_execution_route(
        request,
        ValidationResult(accepted=True, reason="accepted"),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_github_task_config(enabled=True),
    )

    payload = route.model_dump(mode="json")
    assert payload["route_type"] == "public_readonly"
    assert payload["execution_mode"] == "live_public_readonly"
    assert payload["public_target_label"] == "GitHub"
    assert payload["public_origin"] == "https://github.com"
    assert payload["public_allowlist_id"] == "github"
    assert payload["public_task_id"] == "github-repo-search"
    assert payload["public_task_kind"] == "github-repo-search"
    assert payload["public_task_slots"]["search_query"] == "agent tooling"
    assert payload["public_completion_criteria_id"] == "github-repo-search-results"
    assert payload["public_matrix_eligible"] is True
    assert payload["public_target_class"] == "public_repository"
    assert payload["public_completion_criteria_summary"] == [
        "searched_query",
        "search_page_state",
        "repository_result_marker",
    ]
    assert payload["public_evidence_export_state"] == "local_private"
    assert payload["evidence_privacy_state"] == "local_private"


def test_github_search_keeps_controlled_showcase_fallback_when_public_readonly_disabled():
    request = BrowserTaskRequest(
        task="Search GitHub repositories for agent tooling",
        intent_type=BrowserIntentType.SEARCH_OPEN,
        constraints=["bounded single browser task", "public_readonly"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "stop_if_login_required"],
        public_task_slots={
            "target_site_hint": "github",
            "task_kind_hint": "github-repo-search",
            "search_query": "agent tooling",
            "read_only_intent": True,
        },
    )

    route = select_execution_route(
        request,
        ValidationResult(accepted=True, reason="accepted"),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_github_task_config(enabled=False),
    )

    assert route.route_type is RouteType.CONTROLLED_LIVE
    assert route.execution_mode is ExecutionMode.LIVE_CONTROLLED
    assert route.controlled_fixture_id == "github-showcase"
    assert route.controlled_target_ref == "demo/pages/github_showcase.html"


def test_github_public_readonly_rejects_manual_override_without_matching_contract():
    request = BrowserTaskRequest(
        task="Open https://github.com/login and sign in",
        intent_type=BrowserIntentType.SEARCH_OPEN,
        constraints=["bounded single browser task", "public_readonly"],
        visual_references=[],
        requires_confirmation=True,
        stop_conditions=["login_required", "irreversible_submit"],
        safety_flags=["login"],
        public_task_slots={"target_site_hint": "github"},
    )

    route = select_execution_route(
        request,
        ValidationResult(accepted=True, reason="accepted", requires_confirmation=True),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_github_task_config(enabled=True),
        requested_execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
    )

    assert route.route_type is RouteType.BLOCKED
    assert route.route_reason == "public_readonly_unsafe_command"


def test_public_readonly_route_rejects_unsafe_urls_with_stable_matrix_reasons():
    config = _github_task_config(enabled=True)
    cases = [
        ("Open file:///Users/example/private.txt and search GitHub repositories for agent tooling", "unsafe_protocol"),
        ("Open http://127.0.0.1/admin and search GitHub repositories for agent tooling", "private_network_target"),
        ("Open https://user:secret@github.com/search?q=agent&type=repositories", "credentialed_url"),
        ("Open https://evil.example/private and search GitHub repositories for agent tooling", "target_not_allowlisted"),
    ]

    for transcript, reason in cases:
        request = BrowserTaskRequest(
            task=transcript,
            intent_type=BrowserIntentType.SEARCH_OPEN,
            constraints=["bounded single browser task", "public_readonly"],
            visual_references=[],
            requires_confirmation=False,
            stop_conditions=["login_required", "stop_if_login_required"],
            public_task_slots={
                "target_site_hint": "github",
                "task_kind_hint": "github-repo-search",
                "search_query": "agent tooling",
                "read_only_intent": True,
            },
        )

        route = select_execution_route(
            request,
            ValidationResult(accepted=True, reason="accepted"),
            ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
            public_readonly_config=config,
            requested_execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
        )

        assert route.route_type is RouteType.BLOCKED
        assert route.route_reason == reason
        payload = route.model_dump(mode="json")
        assert payload["public_matrix_eligible"] is False
        assert payload["public_completion_state"] == "blocked"


def test_unsafe_command_does_not_select_live_execution(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.post("/api/executions", json={"transcript_text": "帮我结账并提交付款"})

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    assert route["route_type"] in {"confirmation_required", "demo_preview"}
    assert route["live_evidence_eligible"] is False
    assert body["final_status"] == "pending_confirmation"
    assert not body["browser_actions"]


def test_public_readonly_mode_is_documented_as_disabled_by_default(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.post("/api/executions", json={"transcript_text": "打开 OpenAI 的公开文档页面"})

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    assert route["route_type"] == "demo_preview"
    assert route["execution_mode"] == "demo_preview"
    assert route["live_evidence_eligible"] is False
    assert "public-readonly" in route["user_message"].lower()
    assert body["stop_reason"] == "demo_preview_not_executed"


def test_manual_live_override_cannot_force_public_command_into_controlled_fixture(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.post(
        "/api/executions",
        json={
            "transcript_text": "打开 OpenAI 的公开文档页面",
            "controlled_fixture_id": "icon-search",
            "execution_mode": "live_controlled",
        },
    )

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    assert route["route_type"] == "demo_preview"
    assert route["execution_mode"] == "demo_preview"
    assert route["controlled_fixture_id"] is None
    assert route["live_evidence_eligible"] is False
    assert body["execution_mode"] == "demo_preview"
    assert body["stop_reason"] == "demo_preview_not_executed"


def test_manual_live_override_cannot_bypass_confirmation_gate(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.post(
        "/api/executions",
        json={
            "transcript_text": "帮我结账并提交付款",
            "controlled_fixture_id": "icon-search",
            "execution_mode": "live_controlled",
        },
    )

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    assert route["route_type"] == "confirmation_required"
    assert route["controlled_fixture_id"] is None
    assert route["live_evidence_eligible"] is False
    assert body["final_status"] == "pending_confirmation"
    assert not body["browser_actions"]


def test_trace_read_endpoint_returns_sanitized_payload_for_controlled_live(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))
    execution = client.post("/api/executions", json={"transcript_text": "打开 GitHub"})
    execution_id = execution.json()["execution_id"]

    response = client.get(f"/api/traces/{execution_id}")

    assert response.status_code == 200
    body = response.json()
    serialized = json.dumps(body, ensure_ascii=False).lower()
    assert "controlled_target_url" not in serialized
    assert "file:///users/" not in serialized
    assert "remote_vision_backend_url" not in serialized
    assert body["route_decision"]["controlled_fixture_id"] == "github-showcase"
    assert body["execution_runtime"]["evidence_mode"] == "controlled_showcase"


def test_controlled_showcase_page_is_local_and_inspectable():
    page = Path(__file__).resolve().parents[1] / "demo/pages/github_showcase.html"

    html = page.read_text(encoding="utf-8")

    assert "Controlled GitHub Showcase" in html
    assert "aria-label=\"repository search\"" in html
    assert "github.com" not in html.lower()


def test_public_task_route_preserves_contract_slots_limits_and_private_evidence_state():
    request = BrowserTaskRequest(
        task="Search Python docs for pathlib",
        intent_type=BrowserIntentType.SEARCH_OPEN,
        constraints=["bounded single browser task", "public_readonly"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "stop_if_login_required"],
        public_task_slots={
            "target_site_hint": "python docs",
            "search_query": "pathlib",
            "read_only_intent": True,
        },
    )

    route = select_execution_route(
        request,
        ValidationResult(accepted=True, reason="accepted"),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_public_task_config(),
        requested_execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
    )

    payload = route.model_dump(mode="json")
    assert payload["route_type"] == "public_readonly"
    assert payload["execution_mode"] == "live_public_readonly"
    assert payload["public_task_id"] == "python-docs-search"
    assert payload["public_task_kind"] == "documentation_search"
    assert payload["public_task_slots"]["search_query"] == "pathlib"
    assert payload["public_completion_criteria_id"] == "python-docs-search-result"
    assert payload["public_origin"] == "https://docs.python.org"
    assert payload["public_allowlist_id"] == "python-docs"
    assert payload["execution_limits"] == {"max_steps": 3, "timeout_seconds": 12}
    assert payload["evidence_privacy_state"] == "local_private"
    assert payload["sanitizer_status"] == "pending"


def test_useful_public_task_route_preserves_task_category_slots_and_stable_reasons():
    package_request = BrowserTaskRequest(
        task="Read PyPI package metadata for playwright",
        intent_type=BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO,
        constraints=["bounded single browser task", "public_readonly"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "stop_if_login_required"],
        public_task_slots={
            "target_site_hint": "pypi",
            "task_category": "package_metadata",
            "package_ecosystem": "pypi",
            "package_name": "playwright",
            "read_only_intent": True,
        },
    )
    release_request = BrowserTaskRequest(
        task="Read GitHub release notes for microsoft/playwright",
        intent_type=BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO,
        constraints=["bounded single browser task", "public_readonly"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "stop_if_login_required"],
        public_task_slots={
            "target_site_hint": "github",
            "task_category": "release_notes",
            "release_target": "microsoft/playwright",
            "owner": "microsoft",
            "repo": "playwright",
            "read_only_intent": True,
        },
    )

    package_route = select_execution_route(
        package_request,
        ValidationResult(accepted=True, reason="accepted"),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_useful_task_config(),
    )
    release_route = select_execution_route(
        release_request,
        ValidationResult(accepted=True, reason="accepted"),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_useful_task_config(),
    )
    manual_override = select_execution_route(
        package_request.model_copy(
            update={
                "task": "Read PyPI package metadata",
                "public_task_slots": {
                    "target_site_hint": "pypi",
                    "task_category": "package_metadata",
                    "read_only_intent": True,
                }
            }
        ),
        ValidationResult(accepted=True, reason="accepted"),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_useful_task_config(),
        requested_execution_mode=ExecutionMode.LIVE_PUBLIC_READONLY,
    )

    package_payload = package_route.model_dump(mode="json")
    assert package_payload["route_type"] == "public_readonly"
    assert package_payload["public_task_id"] == "pypi-package-read"
    assert package_payload["public_task_category"] == "package_metadata"
    assert package_payload["public_task_slots"]["package_name"] == "playwright"
    assert package_payload["public_completion_criteria_id"] == "pypi-package-metadata"
    assert release_route.route_type is RouteType.PUBLIC_READONLY
    assert release_route.public_task_id == "github-release-notes-read"
    assert release_route.public_task_category == "release_notes"
    assert release_route.public_task_slots["release_target"] == "microsoft/playwright"
    assert manual_override.route_type is RouteType.BLOCKED
    assert manual_override.route_reason == "public_task_contract_mismatch"


def test_useful_public_task_route_infers_package_and_release_slots_without_normalizer_metadata():
    package_request = BrowserTaskRequest(
        task="Read PyPI package metadata for playwright",
        intent_type=BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO,
        constraints=["bounded single browser task", "public_readonly"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "stop_if_login_required"],
    )
    release_request = BrowserTaskRequest(
        task="Read GitHub release notes for microsoft/playwright",
        intent_type=BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO,
        constraints=["bounded single browser task", "public_readonly"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "stop_if_login_required"],
    )

    package_route = select_execution_route(
        package_request,
        ValidationResult(accepted=True, reason="accepted"),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_useful_task_config(),
    )
    release_route = select_execution_route(
        release_request,
        ValidationResult(accepted=True, reason="accepted"),
        ConfirmationDecision(state=ConfirmationState.CONFIRMED, reason="confirmed"),
        public_readonly_config=_useful_task_config(),
    )

    assert package_route.route_type is RouteType.PUBLIC_READONLY
    assert package_route.public_task_id == "pypi-package-read"
    assert package_route.public_task_slots["package_name"] == "playwright"
    assert package_route.public_task_slots["package_ecosystem"] == "pypi"
    assert package_route.public_task_category == "package_metadata"
    assert release_route.route_type is RouteType.PUBLIC_READONLY
    assert release_route.public_task_id == "github-release-notes-read"
    assert release_route.public_task_slots["release_target"] == "microsoft/playwright"
    assert release_route.public_task_slots["owner"] == "microsoft"
    assert release_route.public_task_slots["repo"] == "playwright"
    assert release_route.public_task_category == "release_notes"
