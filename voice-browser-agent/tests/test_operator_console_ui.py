from fastapi.testclient import TestClient

from voice_browser_agent.app import create_app


def test_operator_console_exposes_fixture_replay_control(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert 'id="advancedControls"' in html
    assert 'id="fixtureSelect"' in html
    assert 'id="executionMode"' in html
    assert 'id="transcriptRunButton"' in html
    assert 'id="primaryRunButton"' in html
    assert 'id="fixtureRunButton"' in html
    assert 'id="audioRunButton"' in html
    assert 'id="fixtureModeHelp"' in html
    assert 'id="summaryPanel"' in html
    assert "Run Command" in html
    assert "Advanced Replay" in html
    assert "icon-search" in html
    assert "live_controlled" in html


def test_operator_console_exposes_distinct_input_source_controls(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    html = client.get("/").text

    assert 'aria-label="Transcript command"' in html
    assert 'id="routePanel"' in html
    assert 'id="evidencePanel"' in html
    assert 'id="visualResultPanel"' in html
    assert 'id="visualResultPreview"' in html
    assert 'id="visualStepTimeline"' in html
    assert 'aria-label="Demo fixture"' in html
    assert 'aria-label="Audio upload"' in html
    assert "Run Uploaded Audio" in html
    assert "Run Fixture" in html
    assert 'id="readinessPanel"' in html
    assert 'id="reviewedTranscriptInput"' in html
    assert "Review ASR Transcript" in html
    assert "Run Reviewed Audio" in html
    assert "Route Decision" in html
    assert "Execution Evidence" in html


def test_operator_console_uses_versioned_static_assets_to_avoid_stale_js_cache(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    html = client.get("/").text

    assert 'href="/static/styles.css?v=console-v4-20260529"' in html
    assert 'src="/static/app.js?v=console-v4-20260529"' in html


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
    assert "primaryRunButton" in app_js
    assert "renderRoute" in app_js
    assert "renderEvidence" in app_js
    assert "renderVisualResult" in app_js
    assert "public_visual_artifacts" in app_js
    assert "public_final_visual_result" in app_js
    assert "visual-artifacts" in app_js
    assert "No visual result captured" in app_js
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
    assert "/api/audio/${state.audioId}/transcript" in app_js
    assert "reviewed_transcript_text" in app_js
    assert "route_decision" in app_js
    assert "Run reviewed audio" in app_js or "audioReviewButton" in app_js
    assert "audioRunButton" in app_js


def test_operator_console_primary_command_does_not_prefer_reviewed_audio():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")
    run_command_body = app_js.split("async function runCommand()", 1)[1].split(
        "async function loadFixtures()",
        1,
    )[0]

    assert "transcript_text" in run_command_body
    assert "audio_id" not in run_command_body
    assert "reviewed_transcript_text" not in run_command_body


def test_operator_console_javascript_loads_real_use_readiness():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")

    assert "/api/readiness" in app_js
    assert "readinessPanel" in app_js
    assert "primary_asr" in app_js
    assert "fallback_asr" in app_js
    assert "normalizer" in app_js
    assert "fallback_policy" in app_js
    assert "ASR unavailable" in app_js
    assert "visual_verifier" in app_js
    assert "controlled_verifier_available" in app_js
    assert "provider_state" in app_js
    assert "missing_setup_action" in app_js


def test_readiness_api_surfaces_visual_verifier_state(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.get("/api/readiness")

    assert response.status_code == 200
    verifier = response.json()["checks"]["visual_verifier"]
    assert verifier["status"] == "ready"
    assert verifier["mode"] == "deterministic_controlled"
    assert verifier["controlled_verifier_available"] is True
    assert verifier["provider_state"] in {"not_configured", "configured_private"}
    assert "missing_setup_action" in verifier


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
    assert "Route:" in app_js
    assert "Evidence mode:" in app_js
    assert "Normalizer:" in app_js
    assert "Normalizer schema:" in app_js
    assert "Normalizer fallback:" in app_js
    assert "Raw trace JSON" in app_js


def test_operator_console_javascript_renders_reliability_matrix_before_raw_trace():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")
    styles = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/styles.css"
    ).read_text(encoding="utf-8")

    assert "Reliability matrix:" in app_js
    assert "public_reliability_matrix_row" in app_js
    assert "matrix-outcome-completed" in app_js
    assert "matrix-outcome-partial" in app_js
    assert "matrix-outcome-stopped" in app_js
    assert "matrix-outcome-failed" in app_js
    assert "matrix-outcome-blocked" in app_js
    assert ".matrix-outcome-completed" in styles
    assert ".matrix-outcome-partial" in styles
    assert ".matrix-outcome-stopped" in styles
    assert ".matrix-outcome-failed" in styles
    assert ".matrix-outcome-blocked" in styles


def test_operator_console_javascript_renders_visual_verification_without_success_tone_for_non_pass():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")
    styles = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/styles.css"
    ).read_text(encoding="utf-8")

    assert "visual_verification_result" in app_js
    assert "Visual verification:" in app_js
    assert "Expected condition" in app_js
    assert "Observed state" in app_js
    assert "Proof refs" in app_js
    assert "Recovery" in app_js
    assert "Stop reason" in app_js
    assert "visual-verification-passed" in app_js
    assert "visual-verification-failed" in app_js
    assert "visual-verification-uncertain" in app_js
    assert "escapeHtml(label)" in app_js
    assert "escapeHtml(value || \"n/a\")" in app_js
    assert ".visual-verification-passed" in styles
    assert ".visual-verification-failed" in styles
    assert ".visual-verification-uncertain" in styles


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
