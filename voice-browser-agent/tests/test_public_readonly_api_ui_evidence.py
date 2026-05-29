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


def _enable_public_task_contract_with_unsafe_target(monkeypatch):
    contract = json.dumps(
        {
            "task_id": "python-docs-direct-read",
            "task_kind": "direct_reference_read",
            "target_url": "file:///Users/example/private.txt",
            "allowed_actions": ["navigate", "extract"],
            "slots": ["target_site_hint"],
            "completion_criteria": {
                "criteria_id": "python-docs-title",
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
        f"python-docs|Python Docs|https://docs.python.org/3/|python,docs,documentation|{contract}",
    )
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_MAX_STEPS", "2")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_TIMEOUT_SECONDS", "8")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_PRIVATE_TRACES", "true")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_SANITIZER_REQUIRED", "true")


def _enable_github_public_task_contract(monkeypatch):
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
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_ENABLED", "true")
    monkeypatch.setenv(
        "VOICE_BROWSER_PUBLIC_READONLY_ALLOWLIST",
        f"github|GitHub|https://github.com/|github,repo,repositories|{contracts}",
    )
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_MAX_STEPS", "5")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_TIMEOUT_SECONDS", "20")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_PRIVATE_TRACES", "true")
    monkeypatch.setenv("VOICE_BROWSER_PUBLIC_READONLY_SANITIZER_REQUIRED", "true")


class GitHubVisualEvidenceAgent:
    last_kwargs = {}

    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs
        type(self).last_kwargs = kwargs

    async def run(self):
        execution_id = self.kwargs["execution_id"]
        artifact_dir = Path(self.kwargs["visual_artifacts_dir"]) / execution_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifact_dir / "step-1-search.png"
        artifact_path.write_bytes(b"\x89PNG\r\n\x1a\nvisible-github-result")
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "search",
                    "description": "searched GitHub repositories for agent tooling",
                    "screenshot_ref": f"artifacts/public-readonly/{execution_id}/step-1-search.png",
                    "browser_state": {
                        "page_title": "Search · agent tooling · GitHub",
                        "origin": "https://github.com",
                        "url": "https://github.com/search?q=agent+tooling&type=repositories",
                        "visible_text": "Repositories agent tooling public repositories",
                    },
                }
            ],
            "visual_artifacts": [
                {
                    "artifact_id": f"{execution_id}-step-1",
                    "execution_id": execution_id,
                    "artifact_kind": "step_screenshot",
                    "action_label": "searched GitHub repositories for agent tooling",
                    "local_ref": f"artifacts/public-readonly/{execution_id}/step-1-search.png",
                    "page_title": "Search · agent tooling · GitHub",
                    "sanitized_origin": "https://github.com",
                    "completion_state": "partial",
                    "privacy_state": "local_private",
                    "sanitizer_status": "pending",
                    "step_index": 1,
                    "is_final": True,
                }
            ],
        }


class GitHubOutOfScopeVisualEvidenceAgent:
    def __init__(self, task, **kwargs):
        self.task = task
        self.kwargs = kwargs

    async def run(self):
        execution_id = self.kwargs["execution_id"]
        runtime_dir = Path(self.kwargs["visual_artifacts_dir"]).parents[1]
        out_of_scope = runtime_dir / "traces" / "outside.png"
        out_of_scope.parent.mkdir(parents=True, exist_ok=True)
        out_of_scope.write_bytes(b"\x89PNG\r\n\x1a\nout-of-scope")
        return {
            "status": "succeeded",
            "actions": [
                {
                    "type": "search",
                    "description": "searched GitHub repositories for agent tooling",
                    "browser_state": {
                        "page_title": "Search · agent tooling · GitHub",
                        "origin": "https://github.com",
                        "url": "https://github.com/search?q=agent+tooling&type=repositories",
                        "visible_text": "Repositories agent tooling public repositories",
                    },
                }
            ],
            "visual_artifacts": [
                {
                    "artifact_id": f"{execution_id}-outside",
                    "execution_id": execution_id,
                    "artifact_kind": "step_screenshot",
                    "action_label": "searched GitHub repositories for agent tooling",
                    "local_ref": "traces/outside.png",
                    "page_title": "Search · agent tooling · GitHub",
                    "sanitized_origin": "https://github.com",
                    "completion_state": "partial",
                    "privacy_state": "local_private",
                    "sanitizer_status": "pending",
                    "step_index": 1,
                    "is_final": True,
                }
            ],
        }


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
    assert public["useful_task_pack"]["status"] == "available"
    assert public["useful_task_pack"]["task_count"] >= 8
    assert set(public["useful_task_pack"]["category_counts"]) >= {
        "documentation",
        "reference",
        "package_metadata",
        "release_notes",
        "public_repository_search",
        "public_repository_read",
    }
    assert public["useful_task_pack"]["public_ready"] is False
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
    assert route["public_matrix_eligible"] is True
    assert route["public_target_class"] == "documentation"
    assert route["public_completion_criteria_summary"] == [
        "searched_query",
        "result_heading",
        "url_path",
    ]
    assert route["public_evidence_export_state"] == "local_private"
    assert runtime["public_task_id"] == "python-docs-search"
    assert runtime["public_task_kind"] == "documentation_search"
    assert runtime["public_completion_criteria_id"] == "python-docs-search-result"
    assert runtime["public_completion_state"] == "completed"
    assert runtime["public_observed_proof_summary"]["searched_query"] == "pathlib"
    assert runtime["public_unmet_criteria"] == []
    assert runtime["public_reliability_matrix_row"]["task_id"] == "python-docs-search"
    assert runtime["public_reliability_matrix_row"]["target_class"] == "documentation"
    assert runtime["public_reliability_matrix_row"]["outcome"] == "completed"
    assert runtime["public_reliability_matrix_row"]["visible_result_state"] == "not_captured"
    assert runtime["public_reliability_matrix_row"]["export_state"] == "local_private"
    assert PublicTaskSearchEvidenceAgent.last_kwargs["target_url"] == (
        "https://docs.python.org/3/search.html?q=pathlib"
    )
    assert PublicTaskSearchEvidenceAgent.last_kwargs["timeout_seconds"] == 12
    assert body["final_status"] == "succeeded"
    serialized = json.dumps(body, ensure_ascii=False)
    assert "visible_text" not in serialized
    assert "cookies" not in serialized
    assert "https://docs.python.org/3/search.html" not in serialized


def test_execution_api_returns_blocked_matrix_row_for_known_contract_unsafe_target(
    monkeypatch,
    tmp_path,
):
    _enable_public_task_contract_with_unsafe_target(monkeypatch)
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.agent_factory = PublicReadonlyEvidenceAgent
    client = TestClient(app)

    response = client.post(
        "/api/executions",
        json={"transcript_text": "Open Python docs public page, do not log in"},
    )

    assert response.status_code == 200
    body = response.json()
    runtime = body["execution_runtime"]
    row = runtime["public_reliability_matrix_row"]
    serialized = json.dumps(body, ensure_ascii=False)

    assert body["route_decision"]["route_type"] == "public_readonly"
    assert body["final_status"] == "blocked"
    assert body["stop_reason"] == "unsafe_protocol"
    assert runtime["public_completion_state"] == "blocked"
    assert runtime["public_task_completion"]["stop_reason"] == "unsafe_protocol"
    assert runtime["public_unmet_criteria"] == ["final_title"]
    assert row["task_id"] == "python-docs-direct-read"
    assert row["outcome"] == "blocked"
    assert row["final_status"] == "blocked"
    assert row["stop_or_failure_reason"] == "unsafe_protocol"
    assert "file:///Users/example/private.txt" not in serialized
    assert "/Users/example" not in serialized


def test_execution_api_returns_guarded_github_visual_artifact_refs(monkeypatch, tmp_path):
    _enable_github_public_task_contract(monkeypatch)
    GitHubVisualEvidenceAgent.last_kwargs = {}
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.agent_factory = GitHubVisualEvidenceAgent
    client = TestClient(app)

    response = client.post(
        "/api/executions",
        json={"transcript_text": "Search GitHub repositories for agent tooling, do not log in"},
    )

    assert response.status_code == 200
    body = response.json()
    runtime = body["execution_runtime"]
    artifact = runtime["public_visual_artifacts"][0]
    assert body["route_decision"]["route_type"] == "public_readonly"
    assert body["route_decision"]["public_task_id"] == "github-repo-search"
    assert runtime["public_completion_state"] == "completed"
    assert runtime["public_final_visual_result"]["artifact_id"] == artifact["artifact_id"]
    assert artifact["local_ref"].startswith("artifacts/public-readonly/")
    assert artifact["privacy_state"] == "local_private"
    assert artifact["sanitizer_status"] == "pending"
    assert GitHubVisualEvidenceAgent.last_kwargs["target_url"] == (
        "https://github.com/search?q=agent+tooling&type=repositories"
    )

    image = client.get(
        f"/api/executions/{body['execution_id']}/visual-artifacts/{artifact['artifact_id']}"
    )
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    assert image.content.startswith(b"\x89PNG")

    traversal = client.get(f"/api/executions/{body['execution_id']}/visual-artifacts/../../secret")
    assert traversal.status_code in {404, 422}
    serialized = json.dumps(body, ensure_ascii=False)
    assert "visible-github-result" not in serialized
    assert str(tmp_path) not in serialized
    assert "data:image" not in serialized


def test_visual_artifact_endpoint_rejects_refs_outside_execution_artifact_dir(monkeypatch, tmp_path):
    _enable_github_public_task_contract(monkeypatch)
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.agent_factory = GitHubOutOfScopeVisualEvidenceAgent
    client = TestClient(app)

    response = client.post(
        "/api/executions",
        json={"transcript_text": "Search GitHub repositories for agent tooling, do not log in"},
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["execution_runtime"]["public_visual_artifacts"][0]
    assert artifact["local_ref"] == "traces/outside.png"

    image = client.get(
        f"/api/executions/{body['execution_id']}/visual-artifacts/{artifact['artifact_id']}"
    )
    assert image.status_code == 404


def test_operator_console_static_assets_render_public_readonly_readiness_and_route_state():
    app_js = (PROJECT_ROOT / "src/voice_browser_agent/static/app.js").read_text(encoding="utf-8")
    index_html = (PROJECT_ROOT / "src/voice_browser_agent/static/index.html").read_text(
        encoding="utf-8"
    )

    assert "public_readonly" in app_js
    assert "Public-readonly" in app_js
    assert "Useful task pack" in app_js
    assert "useful_task_pack" in app_js
    assert "renderUsefulTaskPack" in app_js
    assert "usefulTaskPackRows" in app_js
    assert "task_category" in app_js
    assert "public_task_category" in app_js
    assert "category_counts" in app_js
    assert "observed_proof_summary" in app_js
    assert "unmet_criteria" in app_js
    assert "stop_or_failure_reason" in app_js
    assert "completion_criteria_summary" in app_js
    assert "task_kind" in app_js
    assert "target_class" in app_js
    assert "export_state" in app_js
    assert "public_target_label" in app_js
    assert "public_origin" in app_js
    assert "public_allowlist_id" in app_js
    assert "public_task_id" in app_js
    assert "public_task_kind" in app_js
    assert "public_completion_criteria_id" in app_js
    assert "public_completion_state" in app_js
    assert "public_observed_proof_summary" in app_js
    assert "public_unmet_criteria" in app_js
    assert "public_reliability_matrix_row" in app_js
    assert "public_matrix_eligible" in app_js
    assert "public_target_class" in app_js
    assert "public_completion_criteria_summary" in app_js
    assert "public_evidence_export_state" in app_js
    assert "matrix-outcome-completed" in app_js
    assert "matrix-outcome-partial" in app_js
    assert "matrix-outcome-stopped" in app_js
    assert "matrix-outcome-failed" in app_js
    assert "matrix-outcome-blocked" in app_js
    assert "evidence_privacy_state" in app_js
    assert "sanitizer_status" in app_js
    assert "execution_limits" in app_js
    assert "renderVisualResult" in app_js
    assert "visualResultPanel" in index_html
    assert "public_visual_artifacts" in app_js
    assert "public_final_visual_result" in app_js
    assert "visual-artifacts" in app_js
    assert "No visual result captured" in app_js
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
    context = (PROJECT_ROOT.parent / "CONTEXT.md").read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    suite = (PROJECT_ROOT / "docs/demo/demo-task-suite.md").read_text(encoding="utf-8")
    scenarios = (PROJECT_ROOT / "docs/demo/useful-scenarios.md").read_text(encoding="utf-8")
    public_evidence = (PROJECT_ROOT / "docs/public-evidence/index.html").read_text(
        encoding="utf-8"
    )
    video_plan = (PROJECT_ROOT / "docs/demo/video-plan.md").read_text(encoding="utf-8")
    closeout = (PROJECT_ROOT / "docs/demo/closeout-checklist.md").read_text(encoding="utf-8")
    interview = (PROJECT_ROOT / "docs/interview-project-overview.html").read_text(encoding="utf-8")
    smoke = json.loads((PROJECT_ROOT / "fixtures/public-readonly-smoke.json").read_text())

    combined = "\n".join([context, readme, suite, scenarios, public_evidence, video_plan, closeout, interview])
    assert "live_public_readonly" in combined
    assert "public-readonly reliability matrix" in combined
    assert "private-by-default" in combined
    assert "read-only" in combined
    assert "No login" in combined or "no login" in combined
    assert "unrestricted public-web autonomy" in combined
    assert "production automation" in combined
    assert "captcha bypass" in combined
    assert "benchmark ranking" in combined
    assert [task["id"] for task in smoke["tasks"]] == [
        "openai-docs-overview",
        "python-docs-search",
        "github-repo-search",
        "github-public-repo-read",
        "mdn-readonly-reference",
    ]
    assert all(task["artifact_status"] == "local_private_until_sanitized" for task in smoke["tasks"])
    assert all(task["task_kind"] for task in smoke["tasks"])
    assert all(task["completion_criteria"] for task in smoke["tasks"])
    assert all(task["target_class"] for task in smoke["tasks"])
    assert {task["expected_matrix_coverage"] for task in smoke["tasks"]} == {
        "completed",
        "partial",
        "stopped",
        "failed",
        "blocked",
    }
    assert "completion verifier" in combined
    assert "task-contract" in combined
    useful_pack = PROJECT_ROOT / "fixtures/public-readonly-useful-task-pack.json"
    useful = json.loads(useful_pack.read_text())
    assert len(useful["tasks"]) >= 8
    assert "public-readonly useful task pack" in combined
    assert "package metadata" in combined
    assert "release notes" in combined
    assert all(task["artifact_status"] == "local_private_until_sanitized" for task in useful["tasks"])
