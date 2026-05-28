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
