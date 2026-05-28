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
    contract = json.dumps(
        {
            "task_id": "openai-docs-read",
            "task_kind": "direct_reference_read",
            "target_url": "https://platform.openai.com/docs",
            "allowed_actions": ["navigate", "extract"],
            "slots": ["target_site_hint"],
            "completion_criteria": {
                "criteria_id": "openai-docs-title",
                "required_proof": ["final_title"],
            },
            "max_steps": 2,
            "timeout_seconds": 8,
            "privacy_policy": "local_private",
        }
    )
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_ENABLED", "true")
    monkeypatch.setenv(
        "VOICE_BROWSER_PUBLIC_READONLY_ALLOWLIST",
        f"openai-docs|OpenAI Docs|https://platform.openai.com/docs|openai,docs|{contract}",
    )
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_MAX_STEPS", "2")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_TIMEOUT_SECONDS", "8")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_PRIVATE_TRACES", "true")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_SANITIZER_REQUIRED", "true")


def _enable_public_readonly_without_contract(monkeypatch):
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_ENABLED", "true")
    monkeypatch.setenv(
        "VOICE_BROWSER_PUBLIC_READONLY_ALLOWLIST",
        "openai-docs|OpenAI Docs|https://platform.openai.com/docs|openai,docs",
    )
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_MAX_STEPS", "2")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_TIMEOUT_SECONDS", "8")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_PRIVATE_TRACES", "true")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_SANITIZER_REQUIRED", "true")


class PublicTaskSearchEvidenceAgent:
    last_kwargs = {}

    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs
        type(self).last_kwargs = kwargs

    async def run(self):
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "search",
                    "description": "searched Python public docs for pathlib",
                    "grounding_evidence_refs": ["grounding/public-readonly/python-docs-search.json"],
                    "browser_state": {
                        "page_title": "Search results - Python documentation",
                        "origin": "https://docs.python.org",
                        "url": "https://docs.python.org/3/search.html?q=pathlib",
                        "visible_text": "Search Results pathlib pathlib.Path",
                        "cookies": ["private-cookie"],
                    },
                }
            ],
        }


def _enable_public_task_contract(monkeypatch):
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
                "visible_markers": ["Search Results", "{search_query}"],
                "url_path_contains": "/search.html",
            },
            "max_steps": 3,
            "timeout_seconds": 12,
            "privacy_policy": "local_private",
        }
    )
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_ENABLED", "true")
    monkeypatch.setenv(
        "VOICE_BROWSER_PUBLIC_READONLY_ALLOWLIST",
        f"python-docs|Python Docs|https://docs.python.org/3/|python,docs,documentation|{contract}",
    )
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_MAX_STEPS", "5")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_TIMEOUT_SECONDS", "20")
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


def test_readiness_api_reports_missing_task_contracts(monkeypatch, tmp_path):
    _enable_public_readonly_without_contract(monkeypatch)
    client = TestClient(create_app(runtime_dir=tmp_path))

    response = client.get("/api/readiness")

    assert response.status_code == 200
    public = response.json()["checks"]["public_readonly"]
    assert public["status"] == "missing_task_contracts"
    assert public["task_contract_count"] == 0


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


def test_execution_api_blocks_public_readonly_without_task_contract(monkeypatch, tmp_path):
    _enable_public_readonly_without_contract(monkeypatch)
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.agent_factory = PublicReadonlyEvidenceAgent
    client = TestClient(app)

    response = client.post(
        "/api/executions",
        json={"transcript_text": "打开 OpenAI 的公开文档页面"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["route_decision"]["route_type"] == "blocked"
    assert body["route_decision"]["route_reason"] == "public_task_contract_mismatch"
    assert body["final_status"] == "blocked"
    assert body["stop_reason"] == "public_task_contract_mismatch"
    assert "browser_context" not in body["execution_runtime"]


def test_execution_api_returns_public_task_completion_evidence(monkeypatch, tmp_path):
    _enable_public_task_contract(monkeypatch)
    PublicTaskSearchEvidenceAgent.last_kwargs = {}
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.agent_factory = PublicTaskSearchEvidenceAgent
    client = TestClient(app)

    response = client.post(
        "/api/executions",
        json={"transcript_text": "Search Python docs for pathlib, do not log in"},
    )

    assert response.status_code == 200
    body = response.json()
    route = body["route_decision"]
    runtime = body["execution_runtime"]
    assert route["route_type"] == "public_readonly"
    assert route["public_task_id"] == "python-docs-search"
    assert route["public_task_kind"] == "documentation_search"
    assert route["public_task_slots"]["search_query"] == "pathlib"
    assert route["public_completion_criteria_id"] == "python-docs-search-result"
    assert runtime["public_task_id"] == "python-docs-search"
    assert runtime["public_task_kind"] == "documentation_search"
    assert runtime["public_completion_criteria_id"] == "python-docs-search-result"
    assert runtime["public_completion_state"] == "completed"
    assert runtime["public_observed_proof_summary"]["searched_query"] == "pathlib"
    assert runtime["public_unmet_criteria"] == []
    assert PublicTaskSearchEvidenceAgent.last_kwargs["target_url"] == (
        "https://docs.python.org/3/search.html?q=pathlib"
    )
    assert PublicTaskSearchEvidenceAgent.last_kwargs["timeout_seconds"] == 12
    assert body["final_status"] == "succeeded"
    serialized = json.dumps(body, ensure_ascii=False)
    assert "visible_text" not in serialized
    assert "cookies" not in serialized
    assert "https://docs.python.org/3/search.html" not in serialized


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
    assert "public_task_id" in app_js
    assert "public_task_kind" in app_js
    assert "public_completion_criteria_id" in app_js
    assert "public_completion_state" in app_js
    assert "public_observed_proof_summary" in app_js
    assert "public_unmet_criteria" in app_js
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
                    "public_task_id": "openai-docs-read",
                    "public_task_kind": "direct_reference_read",
                },
                "execution_runtime": {
                    "evidence_mode": "live_public_readonly",
                    "public_completion_state": "partial",
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
            "public_task_id": "openai-docs-read",
            "public_task_kind": "direct_reference_read",
            "completion_state": "partial",
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
    assert all(task["task_kind"] for task in smoke["tasks"])
    assert all(task["completion_criteria"] for task in smoke["tasks"])
    assert "completion verifier" in combined
    assert "task-contract" in combined
