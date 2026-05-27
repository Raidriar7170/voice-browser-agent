from fastapi.testclient import TestClient

from voice_browser_agent.app import create_app


def test_operator_console_exposes_fixture_replay_control(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert 'id="fixtureSelect"' in html
    assert 'id="executionMode"' in html
    assert 'id="transcriptRunButton"' in html
    assert 'id="fixtureRunButton"' in html
    assert 'id="audioRunButton"' in html
    assert 'id="fixtureModeHelp"' in html
    assert 'id="summaryPanel"' in html
    assert "Run Transcript" in html
    assert "icon-search" in html
    assert "live_controlled" in html


def test_operator_console_exposes_distinct_input_source_controls(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    html = client.get("/").text

    assert 'aria-label="Transcript command"' in html
    assert 'aria-label="Demo fixture"' in html
    assert 'aria-label="Audio upload"' in html
    assert "Run Uploaded Audio" in html
    assert "Run Fixture" in html


def test_operator_console_uses_versioned_static_assets_to_avoid_stale_js_cache(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    html = client.get("/").text

    assert 'href="/static/styles.css?v=console-flow-20260527"' in html
    assert 'src="/static/app.js?v=console-flow-20260527"' in html


def test_operator_console_javascript_posts_fixture_replay_endpoint():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")

    assert "/api/fixtures/${fixtureId}/executions" in app_js
    assert "/api/fixtures" in app_js
    assert "execution_mode" in app_js
    assert "executionMode" in app_js
    assert "updateFixtureModeSupport" in app_js
    assert "Execution mode:" in app_js
    assert "agentic_steps" in app_js
    assert "verification" in app_js
    assert "eventTypeLabel" in app_js
    assert "renderError" in app_js


def test_operator_console_javascript_runs_uploaded_audio_by_audio_id():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")

    assert "audioId" in app_js
    assert "state.audioId" in app_js
    assert 'postJson("/api/executions", { audio_id: state.audioId })' in app_js
    assert "audioRunButton" in app_js


def test_operator_console_javascript_renders_compact_summary_before_raw_trace():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")

    assert "renderSummary" in app_js
    assert "summaryPanel" in app_js
    assert "Input source:" in app_js
    assert "Final status:" in app_js
    assert "Raw trace JSON" in app_js


def test_operator_console_javascript_gates_status_voice_feedback():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")

    assert "speakStatus" in app_js
    assert "status_voice" in app_js
    assert "speechSynthesis" in app_js
    assert "if (!statusVoice?.enabled)" in app_js
