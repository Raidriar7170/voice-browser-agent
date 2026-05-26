from fastapi.testclient import TestClient

from voice_browser_agent.app import create_app


def test_operator_console_exposes_fixture_replay_control(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert 'id="fixtureSelect"' in html
    assert 'id="executionMode"' in html
    assert 'id="fixtureRunButton"' in html
    assert "icon-search" in html
    assert "live_controlled" in html


def test_operator_console_javascript_posts_fixture_replay_endpoint():
    app_js = (
        __import__("pathlib")
        .Path(__file__)
        .resolve()
        .parents[1]
        / "src/voice_browser_agent/static/app.js"
    ).read_text(encoding="utf-8")

    assert "/api/fixtures/${fixtureId}/executions" in app_js
    assert "execution_mode" in app_js
    assert "executionMode" in app_js
    assert "Execution mode:" in app_js
    assert "renderError" in app_js
