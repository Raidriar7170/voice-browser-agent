import importlib.util
import json
import shutil
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts/build_reliability_snapshot.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_reliability_snapshot", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def copy_project_inputs(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(PROJECT_ROOT / "fixtures", project_root / "fixtures")
    return project_root


def test_reliability_snapshot_summarizes_committed_evidence_and_missing_optional_manifests(
    tmp_path,
):
    builder = load_builder()
    project_root = copy_project_inputs(tmp_path)

    manifest = builder.build_reliability_snapshot(project_root=project_root)

    manifest_path = project_root / "runtime/reliability-snapshot/manifest.json"
    assert manifest_path.exists()
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest
    assert manifest["manifest_version"] == "reliability_snapshot.v1"
    assert manifest["privacy_scan"]["status"] == "passed"
    assert manifest["output"]["path"] == "runtime/reliability-snapshot/manifest.json"
    assert manifest["output"]["git_policy"] == "ignored_runtime_artifact"

    coverage = manifest["demo_trace_coverage"]
    assert coverage["total_trace_count"] == 22
    assert coverage["evidence_mode_counts"] == {
        "agentic_live_controlled": 3,
        "demo_preview": 8,
        "live_controlled": 4,
        "real_use_failure": 5,
        "real_vision_controlled": 1,
        "real_voice_controlled": 1,
    }
    assert "fixtures/traces/sanitized/demo-icon-search.json" in coverage["source_trace_paths"]

    visual = manifest["visual_verification"]
    assert visual["status"] == "available"
    assert visual["outcome_counts"]["passed"] >= 1
    assert visual["outcome_counts"]["failed"] >= 1
    assert visual["outcome_counts"]["uncertain"] >= 1
    assert set(visual["verified_fixture_ids"]) >= {"icon-search", "color-swatch"}

    public_readonly = manifest["public_readonly"]
    assert public_readonly["smoke_matrix"]["outcome_counts"] == {
        "completed": 1,
        "partial": 1,
        "stopped": 1,
        "failed": 1,
        "blocked": 1,
    }
    assert public_readonly["useful_task_pack"]["task_count"] >= 8
    assert public_readonly["live_task_pack_runner"] == {
        "status": "unavailable",
        "reason": "manifest_absent",
        "source_manifest_path": "runtime/public-readonly-task-pack/runs",
    }

    assert manifest["normalizer_comparison"] == {
        "status": "unavailable",
        "reason": "manifest_absent",
        "source_manifest_path": "runtime/normalizer-comparison/manifest.json",
    }
    assert manifest["speech_to_task_adaptation_eval"] == {
        "status": "unavailable",
        "reason": "manifest_absent",
        "source_manifest_path": "runtime/speech-to-task-adaptation-eval/manifest.json",
    }


def test_reliability_snapshot_includes_optional_local_manifest_summaries(tmp_path):
    builder = load_builder()
    project_root = copy_project_inputs(tmp_path)

    normalizer_path = project_root / "runtime/normalizer-comparison/manifest.json"
    normalizer_path.parent.mkdir(parents=True)
    normalizer_path.write_text(
        json.dumps(
            {
                "manifest_version": "normalizer_comparison.v1",
                "status": "available",
                "privacy_state": "local_private",
                "export_state": "local_private",
                "input_count": 13,
                "row_count": 26,
                "normalizer_modes": ["rule", "mock_llm"],
                "schema_status_counts": {"passed": 26},
                "validator_outcome_counts": {"accepted": 24, "clarification_required": 2},
                "fallback_counts": {"mock_llm": 0},
                "privacy_scan": {"status": "passed"},
                "rows": [{"omitted_from_snapshot": True}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    eval_path = project_root / "runtime/speech-to-task-adaptation-eval/manifest.json"
    eval_path.parent.mkdir(parents=True)
    eval_path.write_text(
        json.dumps(
            {
                "manifest_version": "speech_to_task_adaptation_eval.v1",
                "status": "available",
                "privacy_state": "local_private",
                "export_state": "local_private",
                "split_counts": {"train": 13, "dev": 4, "test": 4},
                "candidate_modes": ["rule", "mock_llm"],
                "metrics_by_mode": {"rule": {"schema_valid_rate": 1.0}},
                "failure_slices": {"split": {"test": {"failure_count": 0}}},
                "privacy_scan": {"status": "passed"},
                "rows": [{"omitted_from_snapshot": True}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    run_dir = project_root / "runtime/public-readonly-task-pack/runs/run-ci"
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "public_readonly_task_pack_run.v1",
                "run_id": "run-ci",
                "runner_mode": "deterministic",
                "selected_task_count": 2,
                "outcome_counts": {"completed": 1, "blocked": 1},
                "privacy_state": "local_private",
                "sanitizer_status": "pending",
                "export_state": "local_private",
                "live_network_attempted": False,
                "rows": [{"task_id": "openai-docs-overview", "export_state": "local_private"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manifest = builder.build_reliability_snapshot(project_root=project_root)

    assert manifest["normalizer_comparison"]["status"] == "available"
    assert manifest["normalizer_comparison"]["input_count"] == 13
    assert manifest["normalizer_comparison"]["row_count"] == 26
    assert "rows" not in manifest["normalizer_comparison"]
    assert manifest["speech_to_task_adaptation_eval"]["status"] == "available"
    assert manifest["speech_to_task_adaptation_eval"]["split_counts"]["test"] == 4
    assert "rows" not in manifest["speech_to_task_adaptation_eval"]
    assert manifest["public_readonly"]["live_task_pack_runner"]["status"] == "available"
    assert manifest["public_readonly"]["live_task_pack_runner"]["run_id"] == "run-ci"
    assert manifest["public_readonly"]["live_task_pack_runner"]["live_network_attempted"] is False
    assert "rows" not in manifest["public_readonly"]["live_task_pack_runner"]
    assert {
        item["command"] for item in manifest["validation_command_provenance"]
    } >= {
        "OPENSPEC_TELEMETRY=0 openspec validate --all --strict",
        "python -m pytest $CI_SAFE_PYTEST_TARGETS",
        "uv run pytest",
    }


@pytest.mark.parametrize(
    ("field_name", "field_value", "message"),
    [
        ("raw_audio_path", "recordings/private.wav", "raw_audio_path"),
        ("raw_screenshot", "screenshots/raw.png", "raw_screenshot"),
        ("browser_profile", "Default", "browser_profile"),
        ("cookies", [{"name": "session"}], "cookies"),
        ("credentials", {"api_key": "secret"}, "credentials"),
        ("raw_prompt", "private prompt", "raw_prompt"),
        ("raw_provider_response", "private provider payload", "raw_provider_response"),
        ("local_file_uri", "file:///Users/private/runtime.json", "local_file_uri"),
        ("notes", "https://127.0.0.1:9222/json/list", "private_url"),
        ("notes", "https://10.0.0.12/internal", "private_url"),
        ("notes", "http://172.16.0.5/internal", "private_url"),
        ("notes", "https://172.31.255.255/internal", "private_url"),
        ("notes", "http://192.168.1.23/internal", "private_url"),
        ("notes", "/Users/private/runtime.json", "local_path"),
        ("remote_host", "ssh://a100.internal", "remote_host"),
        ("raw_public_page_text", "full page text", "raw_public_page_text"),
        ("unsanitized_runtime", {"debug": True}, "unsanitized_runtime"),
        ("checkpoint_path", "models/adapter.safetensors", "checkpoint_path"),
    ],
)
def test_reliability_snapshot_rejects_private_optional_manifest_markers(
    tmp_path,
    field_name,
    field_value,
    message,
):
    builder = load_builder()
    project_root = copy_project_inputs(tmp_path)
    manifest_path = project_root / "runtime/normalizer-comparison/manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "normalizer_comparison.v1",
                "status": "available",
                "privacy_state": "local_private",
                "export_state": "local_private",
                "normalizer_modes": ["rule"],
                "schema_status_counts": {"passed": 1},
                "validator_outcome_counts": {"accepted": 1},
                "privacy_scan": {"status": "passed"},
                field_name: field_value,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(builder.ReliabilitySnapshotError, match=message):
        builder.build_reliability_snapshot(project_root=project_root)
