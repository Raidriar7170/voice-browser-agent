import json
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from voice_browser_agent.app import create_app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
                    "description": "read public documentation page title",
                    "grounding_evidence_refs": ["grounding/public-readonly/openai-docs.json"],
                    "browser_state": {
                        "page_title": "OpenAI Docs",
                        "origin": "https://platform.openai.com",
                        "visible_text": "third-party documentation body",
                        "cookies": ["private-cookie"],
                    },
                }
            ],
        }


def _enable_public_readonly(monkeypatch):
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_ENABLED", "true")
    monkeypatch.setenv(
        "VOICE_BROWSER_PUBLIC_READONLY_ALLOWLIST",
        "openai-docs|OpenAI Docs|https://platform.openai.com/docs",
    )
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_MAX_STEPS", "2")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_TIMEOUT_SECONDS", "8")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_PRIVATE_TRACES", "true")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_SANITIZER_REQUIRED", "true")


def test_readiness_api_reports_public_readonly_state_and_sanitizer(monkeypatch, tmp_path):
    _enable_public_readonly(monkeypatch)
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.get("/api/readiness")

    assert response.status_code == 200
    body = response.json()
    public = body["checks"]["public_readonly"]
    assert public["status"] == "ready"
    assert public["enabled"] is True
    assert public["allowlist_count"] == 1
    assert public["allowlist"] == [{"id": "openai-docs", "label": "OpenAI Docs"}]
    assert public["browser_isolation"]["status"] == "ready"
    assert public["sanitizer"]["status"] == "required"
    assert "https://platform.openai.com/docs" not in json.dumps(body, ensure_ascii=False)


def test_execution_api_returns_public_readonly_route_private_evidence(monkeypatch, tmp_path):
    _enable_public_readonly(monkeypatch)
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.agent_factory = PublicReadonlyEvidenceAgent
    client = TestClient(app)

    response = client.post(
        "/api/executions",
        json={"transcript_text": "打开 OpenAI 的公开文档页面"},
    )

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    assert route["route_type"] == "public_readonly"
    assert route["execution_mode"] == "live_public_readonly"
    assert route["public_target_label"] == "OpenAI Docs"
    assert route["public_origin"] == "https://platform.openai.com"
    assert route["public_allowlist_id"] == "openai-docs"
    assert route["evidence_privacy_state"] == "local_private"
    assert route["sanitizer_status"] == "pending"
    assert route["execution_limits"] == {"max_steps": 2, "timeout_seconds": 8}
    assert body["execution_runtime"]["browser_context"]["isolation"] == "fresh_ephemeral"
    assert body["final_status"] == "succeeded"
    serialized = json.dumps(body, ensure_ascii=False)
    assert "cookies" not in serialized
    assert "third-party documentation body" not in serialized
    assert "visible_text" not in serialized
    assert "public_target_url" not in serialized
    assert "local_private" in serialized


def test_operator_console_static_assets_render_public_readonly_readiness_and_route_state():
    app_js = (PROJECT_ROOT / "src/voice_browser_agent/static/app.js").read_text(encoding="utf-8")
    index_html = (PROJECT_ROOT / "src/voice_browser_agent/static/index.html").read_text(
        encoding="utf-8"
    )

    assert "public_readonly" in app_js
    assert "Public-readonly" in app_js
    assert "public_target_label" in app_js
    assert "public_origin" in app_js
    assert "public_allowlist_id" in app_js
    assert "evidence_privacy_state" in app_js
    assert "sanitizer_status" in app_js
    assert "execution_limits" in app_js
    assert "Exported public-readonly trace remains local/private" in app_js
    assert "Exported public-readonly trace failed sanitizer checks" in app_js
    assert 'id="readinessPanel"' in index_html


def test_release_pack_excludes_local_private_public_readonly_traces(tmp_path):
    import importlib.util

    script_path = PROJECT_ROOT / "scripts/build_demo_evidence_pack.py"
    spec = importlib.util.spec_from_file_location("build_demo_evidence_pack", script_path)
    builder = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(builder)

    trace_root = tmp_path / "fixtures/traces"
    shutil.copytree(PROJECT_ROOT / "fixtures/traces", trace_root)
    private_dir = trace_root / "public-readonly-private"
    private_dir.mkdir()
    (private_dir / "public-openai-docs.json").write_text(
        json.dumps(
            {
                "execution_id": "exec-public-openai",
                "execution_mode": "live_public_readonly",
                "final_status": "succeeded",
                "evidence_privacy_state": "local_private",
                "sanitizer_status": "pending",
                "route_decision": {
                    "route_type": "public_readonly",
                    "public_target_label": "OpenAI Docs",
                    "public_origin": "https://platform.openai.com",
                    "public_allowlist_id": "openai-docs",
                },
                "execution_runtime": {
                    "evidence_mode": "live_public_readonly",
                    "privacy_scan": {"status": "pending"},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "release-pack",
    )

    assert all(item["evidence_mode"] != "live_public_readonly" for item in manifest["artifacts"])
    assert manifest["local_private_exclusions"] == [
        {
            "execution_id": "exec-public-openai",
            "evidence_mode": "live_public_readonly",
            "reason": "public_readonly_trace_not_public_safe",
            "sanitizer_status": "pending",
            "target_label": "OpenAI Docs",
            "public_origin": "https://platform.openai.com",
        }
    ]


def test_docs_define_public_readonly_smoke_boundaries_and_non_goals():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    suite = (PROJECT_ROOT / "docs/demo/demo-task-suite.md").read_text(encoding="utf-8")
    scenarios = (PROJECT_ROOT / "docs/demo/useful-scenarios.md").read_text(encoding="utf-8")
    public_evidence = (PROJECT_ROOT / "docs/public-evidence/index.html").read_text(
        encoding="utf-8"
    )
    video_plan = (PROJECT_ROOT / "docs/demo/video-plan.md").read_text(encoding="utf-8")
    smoke = json.loads((PROJECT_ROOT / "fixtures/public-readonly-smoke.json").read_text())

    combined = "\n".join([readme, suite, scenarios, public_evidence, video_plan])
    assert "live_public_readonly" in combined
    assert "private-by-default" in combined
    assert "read-only" in combined
    assert "No login" in combined or "no login" in combined
    assert "unrestricted public-web autonomy" in combined
    assert [task["id"] for task in smoke["tasks"]] == [
        "openai-docs-overview",
        "python-docs-search",
        "mdn-readonly-reference",
    ]
    assert all(task["artifact_status"] == "local_private_until_sanitized" for task in smoke["tasks"])
