import importlib.util
import json
from pathlib import Path

import pytest

from voice_browser_agent.config import RuntimeConfig


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts/build_public_readonly_task_pack_summary.py"
LIVE_RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts/run_public_readonly_task_pack.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("build_public_readonly_task_pack_summary", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def load_live_runner():
    spec = importlib.util.spec_from_file_location(
        "run_public_readonly_task_pack",
        LIVE_RUNNER_SCRIPT_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_public_readonly_task_pack_runner_writes_local_private_summary(tmp_path):
    runner = load_runner()
    output_dir = tmp_path / "runtime/public-readonly-task-pack"

    summary = runner.build_task_pack_summary(
        project_root=PROJECT_ROOT,
        output_dir=output_dir,
    )

    summary_path = output_dir / "summary.json"
    assert summary_path.exists()
    written = json.loads(summary_path.read_text(encoding="utf-8"))
    assert written == summary
    assert summary["task_count"] >= 8
    assert summary["is_complete"] is True
    assert summary["public_ready"] is False
    assert set(summary["category_counts"]) >= {
        "documentation",
        "reference",
        "package_metadata",
        "release_notes",
        "public_repository_search",
        "public_repository_read",
    }
    assert all(row["evidence_privacy_state"] == "local_private" for row in summary["rows"])
    assert all(row["export_state"] == "local_private" for row in summary["rows"])
    serialized = json.dumps(summary, ensure_ascii=False)
    assert "raw_page_text" not in serialized
    assert "raw_screenshot" not in serialized
    assert "browser_profile" not in serialized
    assert "/Users/" not in serialized


def test_deterministic_task_pack_runner_writes_selected_local_private_manifest(tmp_path):
    runner = load_live_runner()
    output_dir = tmp_path / "runtime/public-readonly-task-pack"

    manifest = runner.run_task_pack(
        project_root=PROJECT_ROOT,
        output_dir=output_dir,
        task_ids=["openai-docs-overview", "github-public-repo-read"],
        mode="deterministic",
        run_id="run-test-selected",
    )

    manifest_path = output_dir / "runs/run-test-selected/manifest.json"
    assert manifest_path.exists()
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest
    assert manifest["manifest_version"] == "public_readonly_task_pack_run.v1"
    assert manifest["runner_mode"] == "deterministic"
    assert manifest["live_network_attempted"] is False
    assert manifest["selected_task_ids"] == ["openai-docs-overview", "github-public-repo-read"]
    assert manifest["selected_task_count"] == 2
    assert manifest["privacy_state"] == "local_private"
    assert manifest["sanitizer_status"] == "pending"
    assert manifest["export_state"] == "local_private"
    assert manifest["outcome_counts"] == {
        "completed": 1,
        "partial": 0,
        "stopped": 0,
        "failed": 0,
        "blocked": 1,
    }
    assert [row["task_id"] for row in manifest["rows"]] == [
        "openai-docs-overview",
        "github-public-repo-read",
    ]
    assert all(row["evidence_privacy_state"] == "local_private" for row in manifest["rows"])
    assert all(row["export_state"] == "local_private" for row in manifest["rows"])


def test_task_pack_runner_rejects_unknown_task_ids(tmp_path):
    runner = load_live_runner()

    with pytest.raises(runner.TaskPackRunnerError, match="unknown task id"):
        runner.run_task_pack(
            project_root=PROJECT_ROOT,
            output_dir=tmp_path / "runtime/public-readonly-task-pack",
            task_ids=["not-a-real-task"],
            mode="deterministic",
            run_id="run-unknown",
        )


def test_full_task_pack_runner_manifest_preserves_required_row_fields(tmp_path):
    runner = load_live_runner()

    manifest = runner.run_task_pack(
        project_root=PROJECT_ROOT,
        output_dir=tmp_path / "runtime/public-readonly-task-pack",
        mode="deterministic",
        run_all=True,
        run_id="run-full-pack",
    )

    assert manifest["selected_task_count"] == 10
    assert manifest["task_count"] == 10
    assert manifest["outcome_counts"] == {
        "completed": 4,
        "partial": 2,
        "stopped": 2,
        "failed": 1,
        "blocked": 1,
    }
    assert manifest["configuration_summary"]["public_readonly_enabled"] is False
    assert manifest["configuration_summary"]["browser_context"]["isolation"] == "fresh_ephemeral"
    assert manifest["limitation_notes"]
    required_fields = {
        "task_id",
        "task_category",
        "task_kind",
        "target_class",
        "target_label",
        "sanitized_origin",
        "completion_criteria_id",
        "completion_criteria_summary",
        "outcome",
        "final_status",
        "observed_proof_summary",
        "unmet_criteria",
        "stop_or_failure_reason",
        "route_or_execution_reason",
        "visible_result_state",
        "evidence_privacy_state",
        "sanitizer_status",
        "export_state",
    }
    for row in manifest["rows"]:
        assert required_fields.issubset(row)
        assert row["sanitized_origin"].startswith("https://")
        assert "target_url" not in row


def test_live_task_pack_runner_disabled_config_blocks_without_network(tmp_path):
    runner = load_live_runner()
    config = RuntimeConfig(public_readonly_enabled=False)

    manifest = runner.run_task_pack(
        project_root=PROJECT_ROOT,
        output_dir=tmp_path / "runtime/public-readonly-task-pack",
        task_ids=["openai-docs-overview"],
        mode="live",
        config=config,
        run_id="run-disabled",
    )

    row = manifest["rows"][0]
    assert manifest["runner_mode"] == "live"
    assert manifest["live_network_attempted"] is False
    assert row["outcome"] == "blocked"
    assert row["final_status"] == "blocked"
    assert row["stop_or_failure_reason"] == "public_readonly_disabled"
    assert row["route_or_execution_reason"] == "public_readonly_disabled"
    assert row["unmet_criteria"] == ["final_title", "visible_marker"]


def test_live_task_pack_runner_requires_explicit_task_selection(tmp_path):
    runner = load_live_runner()

    with pytest.raises(runner.TaskPackRunnerError, match="requires --task-id or --all"):
        runner.run_task_pack(
            project_root=PROJECT_ROOT,
            output_dir=tmp_path / "runtime/public-readonly-task-pack",
            mode="live",
            config=RuntimeConfig(public_readonly_enabled=True),
            run_id="run-live-implicit",
        )


def test_live_task_pack_runner_records_site_variance_with_fake_agent(tmp_path):
    runner = load_live_runner()

    class CaptchaAgent:
        def __init__(self, task, **kwargs):
            self.task = task
            self.kwargs = kwargs

        async def run(self):
            return {
                "status": "succeeded",
                "actions": [
                    {
                        "type": "navigate",
                        "description": "opened allowlisted public page",
                        "browser_state": {
                            "url": self.kwargs["target_url"],
                            "page_title": "Verification",
                            "origin": "https://platform.openai.com",
                            "visible_text": "captcha verify you are human",
                        },
                    }
                ],
            }

    manifest = runner.run_task_pack(
        project_root=PROJECT_ROOT,
        output_dir=tmp_path / "runtime/public-readonly-task-pack",
        task_ids=["openai-docs-overview"],
        mode="live",
        config=RuntimeConfig(public_readonly_enabled=True),
        run_id="run-site-variance",
        agent_factory=CaptchaAgent,
    )

    row = manifest["rows"][0]
    assert manifest["runner_mode"] == "live"
    assert manifest["live_network_attempted"] is True
    assert row["outcome"] == "stopped"
    assert row["final_status"] == "stopped"
    assert row["stop_or_failure_reason"] == "public_task_captcha_or_verification"
    assert row["route_or_execution_reason"] == "public_task_captcha_or_verification"
    assert row["browser_context"]["persistent_profile"] is False
    assert row["browser_context"]["cookies_reused"] is False


def test_task_pack_run_manifest_excludes_raw_public_artifacts(tmp_path):
    runner = load_live_runner()

    manifest = runner.run_task_pack(
        project_root=PROJECT_ROOT,
        output_dir=tmp_path / "runtime/public-readonly-task-pack",
        mode="deterministic",
        run_all=True,
        run_id="run-privacy",
    )

    serialized = json.dumps(manifest, ensure_ascii=False)
    assert "raw_page_text" not in serialized
    assert "raw_screenshot" not in serialized
    assert "browser_profile" not in serialized
    assert '"storage_state":' not in serialized
    assert '"cookies":' not in serialized
    assert "file:///Users/" not in serialized
    assert "/Users/" not in serialized
