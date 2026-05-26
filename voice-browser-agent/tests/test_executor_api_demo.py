import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from playwright.async_api import async_playwright

from voice_browser_agent.app import create_app
from voice_browser_agent.executor import BrowserExecutorAdapter, BrowserExecutorConfig, BrowserExecutionResult
from voice_browser_agent.asr import FallbackASRAdapter
from voice_browser_agent.models import BrowserIntentType, BrowserTaskRequest, ExecutionStatus


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAV_BYTES = b"RIFF\x24\x00\x00\x00WAVEfmt "


class MockVisionAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "click",
                    "description": "clicked icon-only toolbar search button",
                    "screenshot_ref": "screenshots/sanitized/toolbar-search.png",
                    "grounding_evidence_refs": ["grounding/toolbar-search.json"],
                }
            ],
        }


class MockCheckoutAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "click",
                    "description": "arrived at checkout",
                    "browser_state": {
                        "url": "https://shop.example.test/checkout",
                        "title": "Checkout",
                        "visible_text": "Please log in before payment",
                    },
                }
            ],
            "browser_state": {
                "url": "https://shop.example.test/checkout",
                "title": "Checkout",
                "visible_text": "Please log in before payment",
            },
        }


class FixtureASRAdapter:
    name = "fixture-asr"

    async def transcribe(self, command_input):
        return FallbackASRAdapter.from_text(
            text="打开 GitHub 搜索 browser-use-vision，不要登录",
            command_input=command_input,
            adapter_name=self.name,
            confidence=0.93,
        )


def _visual_request() -> BrowserTaskRequest:
    return BrowserTaskRequest(
        task="Click the icon-only search button.",
        intent_type=BrowserIntentType.CLICK_VISUAL_TARGET,
        constraints=["controlled demo page only"],
        visual_references=[{"kind": "icon", "text": "magnifying glass", "source": "fixture"}],
        requires_confirmation=False,
        stop_conditions=["login_required", "payment_or_checkout"],
    )


@pytest.mark.asyncio
async def test_executor_passes_normalized_context_to_vision_enhanced_agent():
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(
            remote_vision_backend_url="https://vision.invalid/api",
            local_browser=True,
            dry_run=False,
        ),
        agent_factory=MockVisionAgent,
    )

    result = await adapter.execute(_visual_request(), execution_id="exec-vision")

    assert isinstance(result, BrowserExecutionResult)
    assert result.final_status is ExecutionStatus.SUCCEEDED
    assert result.actions[0].grounding_evidence_refs == ["grounding/toolbar-search.json"]
    assert "magnifying glass" in result.agent_task
    assert result.runtime["remote_vision_backend_url"] == "https://vision.invalid/api"


def test_api_happy_path_clarification_confirmation_and_trace_export(tmp_path):
    app = create_app(runtime_dir=tmp_path)
    client = TestClient(app)

    ingest = client.post(
        "/api/ingest",
        files={"file": ("command.wav", WAV_BYTES, "audio/wav")},
    )
    assert ingest.status_code == 200

    preview = client.post(
        "/api/normalize",
        json={"transcript_text": "打开 GitHub 搜索 browser-use-vision，不要登录"},
    )
    assert preview.status_code == 200
    assert preview.json()["normalized_output"]["kind"] == "browser_task_request"

    clarification = client.post(
        "/api/normalize",
        json={"transcript_text": "打开那个页面"},
    )
    assert clarification.status_code == 200
    assert clarification.json()["normalized_output"]["kind"] == "clarification_request"

    execution = client.post(
        "/api/executions",
        json={"transcript_text": "帮我结账并提交付款"},
    )
    assert execution.status_code == 200
    execution_body = execution.json()
    assert execution_body["confirmation_decision"]["state"] == "pending"

    confirm = client.post(
        f"/api/executions/{execution_body['execution_id']}/confirmation",
        json={"decision": "cancel", "decided_by": "operator"},
    )
    assert confirm.status_code == 200
    assert confirm.json()["confirmation_decision"]["state"] == "cancelled"

    trace = client.get(f"/api/traces/{execution_body['execution_id']}")
    assert trace.status_code == 200
    assert trace.json()["final_status"] == "cancelled"

    export = client.get(f"/api/traces/{execution_body['execution_id']}/export")
    assert export.status_code == 200
    assert "raw_audio_path" not in export.text


def test_api_executes_uploaded_audio_through_asr_adapter_and_preserves_metadata(tmp_path):
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.asr_orchestrator.primary = FixtureASRAdapter()
    client = TestClient(app)

    ingest = client.post(
        "/api/ingest",
        files={"file": ("command.wav", WAV_BYTES, "audio/wav")},
    )
    assert ingest.status_code == 200
    audio_id = ingest.json()["audio_id"]

    execution = client.post("/api/executions", json={"audio_id": audio_id})

    assert execution.status_code == 200
    body = execution.json()
    assert body["transcript"]["text"] == "打开 GitHub 搜索 browser-use-vision，不要登录"
    assert body["transcript"]["metadata"]["adapter_name"] == "fixture-asr"
    assert body["transcript"]["metadata"]["input_audio_id"] == audio_id
    assert body["normalized_output"]["kind"] == "browser_task_request"


def test_fixture_replay_endpoint_uses_fixture_asr_and_marks_demo_preview(tmp_path):
    app = create_app(runtime_dir=tmp_path)
    client = TestClient(app)

    response = client.post("/api/fixtures/icon-search/executions")

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"]["metadata"]["adapter_name"] == "fixture-manifest-asr"
    assert body["transcript"]["metadata"]["input_audio_id"] == "icon-search"
    assert body["final_status"] == "stopped"
    assert body["stop_reason"] == "demo_preview_not_executed"


def test_confirmation_decision_cannot_be_replayed_to_execute_twice(tmp_path):
    app = create_app(runtime_dir=tmp_path)
    client = TestClient(app)
    execution = client.post(
        "/api/executions",
        json={"transcript_text": "帮我结账并提交付款"},
    ).json()

    first = client.post(
        f"/api/executions/{execution['execution_id']}/confirmation",
        json={"decision": "confirm", "decided_by": "operator"},
    )
    second = client.post(
        f"/api/executions/{execution['execution_id']}/confirmation",
        json={"decision": "confirm", "decided_by": "operator"},
    )

    assert first.status_code == 200
    assert second.status_code == 409
    trace = client.get(f"/api/traces/{execution['execution_id']}").json()
    assert len(trace["browser_actions"]) == 1


@pytest.mark.asyncio
async def test_controlled_visual_page_smoke_with_local_chromium_and_mock_vision_backend():
    page_path = PROJECT_ROOT / "demo/pages/icon_only_toolbar.html"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            executable_path=playwright.chromium.executable_path,
        )
        page = await browser.new_page()
        await page.goto(page_path.as_uri())
        assert await page.get_by_label("search").count() == 1
        assert "Icon-only toolbar demo" in (await page.text_content("body"))
        await browser.close()

    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(local_browser=True, dry_run=False),
        agent_factory=MockVisionAgent,
    )
    result = await adapter.execute(_visual_request(), execution_id="exec-controlled-page")

    assert result.final_status is ExecutionStatus.SUCCEEDED
    assert result.actions[0].action_type == "click"


@pytest.mark.asyncio
async def test_executor_stops_when_agent_reports_sensitive_browser_state():
    request = _visual_request().model_copy(update={"requires_confirmation": False})
    adapter = BrowserExecutorAdapter(
        config=BrowserExecutorConfig(local_browser=True, dry_run=False),
        agent_factory=MockCheckoutAgent,
    )

    result = await adapter.execute(request, execution_id="exec-stop")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason in {"login_required", "payment_or_checkout"}


def test_browser_use_vision_import_works_with_isolated_config(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))

    module = importlib.import_module("browser_use_vision")

    assert getattr(module, "VisionEnhancedAgent") is not None
