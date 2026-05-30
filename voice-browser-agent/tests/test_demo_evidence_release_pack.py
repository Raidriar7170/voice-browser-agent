import importlib.util
import json
import shutil
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts/build_demo_evidence_pack.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_demo_evidence_pack", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def copy_trace_sources(tmp_path: Path) -> Path:
    source_root = PROJECT_ROOT / "fixtures/traces"
    target_root = tmp_path / "fixtures/traces"
    shutil.copytree(source_root, target_root)
    return target_root


def copy_project_inputs(tmp_path: Path) -> None:
    shutil.copytree(PROJECT_ROOT / "fixtures/audio", tmp_path / "fixtures/audio")
    smoke_path = tmp_path / "fixtures/public-readonly-smoke.json"
    smoke_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROJECT_ROOT / "fixtures/public-readonly-smoke.json", smoke_path)
    shutil.copy2(
        PROJECT_ROOT / "fixtures/public-readonly-useful-task-pack.json",
        tmp_path / "fixtures/public-readonly-useful-task-pack.json",
    )


def add_attempt_evidence(smoke: dict) -> dict:
    for task in smoke["tasks"]:
        outcome = task["expected_matrix_coverage"]
        proof = task["completion_criteria"]["required_proof"]
        observed = {}
        unmet = list(proof)
        reason = f"planned_{outcome}_coverage"
        final_status = "stopped"
        if outcome == "completed":
            observed = {
                "final_title": "OpenAI Docs overview",
                "visible_marker": "documentation overview",
            }
            unmet = []
            reason = None
            final_status = "succeeded"
        elif outcome == "partial":
            observed = {"searched_query": "pathlib", "url_path": "/3/search.html"}
        elif outcome == "failed":
            final_status = "failed"
        elif outcome == "blocked":
            final_status = "blocked"
        task["reliability_attempt_evidence"] = {
            "outcome": outcome,
            "final_status": final_status,
            "observed_proof_summary": observed,
            "unmet_criteria": unmet,
            "stop_or_failure_reason": reason,
            "evidence_privacy_state": "local_private",
            "sanitizer_status": "pending",
            "visible_result_state": "local_private"
            if task.get("visual_artifact_policy")
            else "not_captured",
            "export_state": "local_private",
            "regression_coverage": task.get("regression_coverage", []),
        }
    return smoke


def test_release_pack_manifest_covers_preview_live_agentic_real_vision_and_real_voice_evidence(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    output_dir = tmp_path / "release-pack"

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=output_dir,
    )

    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "index.html").exists()
    assert manifest["privacy_scan"]["status"] == "passed"
    modes = {item["evidence_mode"] for item in manifest["artifacts"]}
    assert modes == {
        "demo_preview",
        "live_controlled",
        "agentic_live_controlled",
        "real_vision_controlled",
        "real_voice_controlled",
        "real_use_failure",
    }

    preview = [item for item in manifest["artifacts"] if item["evidence_mode"] == "demo_preview"]
    live = [item for item in manifest["artifacts"] if item["evidence_mode"] == "live_controlled"]
    agentic = [
        item for item in manifest["artifacts"] if item["evidence_mode"] == "agentic_live_controlled"
    ]
    real_vision = [
        item for item in manifest["artifacts"] if item["evidence_mode"] == "real_vision_controlled"
    ]
    real_voice = [
        item for item in manifest["artifacts"] if item["evidence_mode"] == "real_voice_controlled"
    ]
    failures = [item for item in manifest["artifacts"] if item["evidence_mode"] == "real_use_failure"]
    assert len(preview) == 8
    assert {"icon-search", "color-swatch"}.issubset({item["fixture_id"] for item in live})
    assert any(item["fixture_id"] == "github-showcase" for item in live)
    assert {"icon-search", "color-swatch"}.issubset({item["fixture_id"] for item in agentic})
    visual = manifest["visual_verification"]
    assert visual["privacy_scan"]["status"] == "passed"
    assert visual["outcome_counts"]["passed"] >= 1
    assert visual["outcome_counts"]["failed"] + visual["outcome_counts"]["uncertain"] >= 1
    assert {"icon-search", "color-swatch"}.issubset(set(visual["verified_fixture_ids"]))
    assert visual["recovery_count"] >= 0
    assert visual["failed_or_uncertain_reasons"]
    assert any(row["recovery_or_stop_decisions"] for row in visual["rows"])
    assert all(path.startswith("fixtures/traces/agentic-sanitized/") for path in visual["source_trace_paths"])
    assert all(item["visual_verification"]["status"] == "available" for item in agentic)
    assert any(item["visual_verification"]["recovery_count"] > 0 for item in agentic)
    assert {item["fixture_id"] for item in real_vision} == {"icon-search"}
    assert {item["fixture_id"] for item in real_voice} == {"icon-search"}
    assert len(failures) >= 5
    assert real_vision[0]["provider"]["package"] == "browser-use-vision"
    assert real_vision[0]["adapter"]["api"] == "browser_use_vision.som.annotate_screenshot"
    assert real_voice[0]["asr"]["adapter_name"] == "real-use-smoke-asr"
    assert real_voice[0]["transcript_review"]["status"] == "edited"
    assert all(item["privacy_scan"] == "passed" for item in manifest["artifacts"])
    assert all(item["packaged_path"].startswith("traces/") for item in manifest["artifacts"])
    matrix = manifest["public_readonly_reliability_matrix"]
    assert matrix["is_complete"] is True
    assert matrix["task_count"] == 5
    assert matrix["outcome_counts"] == {
        "completed": 1,
        "partial": 1,
        "stopped": 1,
        "failed": 1,
        "blocked": 1,
    }
    assert matrix["public_ready"] is False
    assert all(row["export_state"] == "local_private" for row in matrix["rows"])
    openai_row = next(row for row in matrix["rows"] if row["task_id"] == "openai-docs-overview")
    assert openai_row["observed_proof_summary"] == {
        "final_title": "OpenAI Docs overview",
        "visible_marker": "documentation overview",
    }
    assert "raw_page_text" not in json.dumps(matrix, ensure_ascii=False)
    useful = manifest["public_readonly_useful_task_pack"]
    assert useful["is_complete"] is True
    assert useful["task_count"] >= 8
    assert useful["public_ready"] is False
    assert set(useful["category_counts"]) >= {
        "documentation",
        "reference",
        "package_metadata",
        "release_notes",
        "public_repository_search",
        "public_repository_read",
    }
    assert all(row["export_state"] == "local_private" for row in useful["rows"])
    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "final_title: OpenAI Docs" in index_html
    assert "visible_marker: Docs" in index_html
    assert "Visual verification loop" in index_html
    assert "Recovery or Stop Decision" in index_html
    assert "deterministic_controlled" in index_html
    assert "visual_verification_result" not in index_html
    assert "raw_page_text" not in json.dumps(useful, ensure_ascii=False)


def test_release_pack_includes_latest_live_task_pack_runner_summary(tmp_path):
    builder = load_builder()
    runner_spec = importlib.util.spec_from_file_location(
        "run_public_readonly_task_pack",
        PROJECT_ROOT / "scripts/run_public_readonly_task_pack.py",
    )
    runner = importlib.util.module_from_spec(runner_spec)
    assert runner_spec and runner_spec.loader
    runner_spec.loader.exec_module(runner)
    trace_root = copy_trace_sources(tmp_path)
    run_root = tmp_path / "runtime/public-readonly-task-pack/runs"
    runner.run_task_pack(
        project_root=PROJECT_ROOT,
        output_dir=tmp_path / "runtime/public-readonly-task-pack",
        task_ids=["openai-docs-overview", "github-public-repo-read"],
        mode="deterministic",
        run_id="run-release-pack",
    )

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "release-pack",
        task_pack_run_root=run_root,
    )

    runner_summary = manifest["public_readonly_live_task_pack_runner"]
    assert runner_summary["status"] == "available"
    assert runner_summary["run_id"] == "run-release-pack"
    assert runner_summary["runner_mode"] == "deterministic"
    assert runner_summary["selected_task_count"] == 2
    assert runner_summary["privacy_state"] == "local_private"
    assert runner_summary["sanitizer_status"] == "pending"
    assert runner_summary["export_state"] == "local_private"
    assert [row["task_id"] for row in runner_summary["rows"]] == [
        "openai-docs-overview",
        "github-public-repo-read",
    ]
    index_html = (tmp_path / "release-pack/index.html").read_text(encoding="utf-8")
    assert "Public-readonly live task-pack runner" in index_html
    assert "run-release-pack" in index_html
    serialized = json.dumps(runner_summary, ensure_ascii=False)
    assert "raw_page_text" not in serialized
    assert "raw_screenshot" not in serialized
    assert "/Users/" not in serialized


def test_release_pack_includes_normalizer_comparison_summary(tmp_path):
    builder = load_builder()
    comparison_spec = importlib.util.spec_from_file_location(
        "build_normalizer_comparison",
        PROJECT_ROOT / "scripts/build_normalizer_comparison.py",
    )
    comparison = importlib.util.module_from_spec(comparison_spec)
    assert comparison_spec and comparison_spec.loader
    comparison_spec.loader.exec_module(comparison)
    trace_root = copy_trace_sources(tmp_path)
    comparison_manifest = comparison.build_comparison(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "runtime/normalizer-comparison",
    )

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "release-pack",
        normalizer_comparison_path=tmp_path / "runtime/normalizer-comparison/manifest.json",
    )

    summary = manifest["normalizer_comparison"]
    assert summary["status"] == "available"
    assert summary["input_count"] == comparison_manifest["input_count"]
    assert set(summary["normalizer_modes"]) == {"rule", "mock_llm"}
    assert summary["privacy_state"] == "local_private"
    assert summary["export_state"] == "local_private"
    assert "rows" not in summary
    index_html = (tmp_path / "release-pack/index.html").read_text(encoding="utf-8")
    assert "Normalizer comparison" in index_html
    assert "structured-output comparison, not model training" in index_html


def test_release_pack_includes_adaptation_eval_summary_when_provided(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    eval_manifest = tmp_path / "runtime/speech-to-task-adaptation-eval/manifest.json"
    eval_manifest.parent.mkdir(parents=True)
    eval_manifest.write_text(
        json.dumps(
            {
                "manifest_version": "speech_to_task_adaptation_eval.v1",
                "status": "available",
                "privacy_state": "local_private",
                "export_state": "local_private",
                "positioning": "local adaptation-readiness evidence, not training or benchmark",
                "source_dataset_manifest_path": "runtime/speech-to-task-adaptation-dataset/manifest.json",
                "split": "test",
                "split_counts": {"train": 13, "dev": 4, "test": 4},
                "candidate_modes": ["rule", "mock_llm"],
                "metrics_by_mode": {
                    "rule": {
                        "row_count": 4,
                        "schema_valid_rate": 1.0,
                        "output_kind_accuracy": 0.75,
                        "intent_type_accuracy": 0.5,
                        "required_slot_match_rate": 0.75,
                        "safety_or_clarification_decision_accuracy": 1.0,
                        "route_ready_rate": 0.5,
                        "fallback_rate": 0.0,
                    }
                },
                "failure_slices": {
                    "candidate_mode": {"rule": {"row_count": 4, "failure_count": 1}},
                    "split": {"test": {"row_count": 4, "failure_count": 1}},
                },
                "privacy_scan": {"status": "passed"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "release-pack",
        adaptation_eval_path=eval_manifest,
    )

    summary = manifest["speech_to_task_adaptation_eval"]
    assert summary["status"] == "available"
    assert summary["source_manifest_path"] == "manifest.json"
    assert summary["source_dataset_manifest_path"] == "runtime/speech-to-task-adaptation-dataset/manifest.json"
    assert summary["split_counts"] == {"train": 13, "dev": 4, "test": 4}
    assert summary["candidate_modes"] == ["rule", "mock_llm"]
    assert summary["metrics_by_mode"]["rule"]["schema_valid_rate"] == 1.0
    assert summary["failure_slices"]["split"]["test"]["failure_count"] == 1
    assert summary["privacy_scan"]["status"] == "passed"
    assert "rows" not in summary
    index_html = (tmp_path / "release-pack/index.html").read_text(encoding="utf-8")
    assert "Speech-to-Task adaptation evaluation" in index_html
    assert "local adaptation-readiness evidence" in index_html
    assert "not fine-tuning, checkpoint, ASR/TTS, public benchmark, SOTA, production, or broad autonomy evidence" in index_html
    manifest_text = (tmp_path / "release-pack/manifest.json").read_text(encoding="utf-8")
    assert str(tmp_path) not in manifest_text
    assert str(tmp_path) not in index_html


def test_release_pack_marks_adaptation_eval_not_provided_without_claiming_run(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "release-pack",
    )

    assert manifest["speech_to_task_adaptation_eval"] == {"status": "not_provided"}
    index_html = (tmp_path / "release-pack/index.html").read_text(encoding="utf-8")
    assert "Speech-to-Task adaptation evaluation" in index_html
    assert "not_provided" in index_html
    assert "schema_valid_rate" not in index_html


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("raw_provider_response", "private provider data"),
        ("credentials", "secret"),
        ("local_file_uri", "file:///Users/private/eval.json"),
        ("remote_host", "10.0.0.2"),
        ("checkpoint_path", "/models/checkpoint.bin"),
    ],
)
def test_release_pack_rejects_private_adaptation_eval_manifest(
    tmp_path,
    field_name,
    field_value,
):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    eval_manifest = tmp_path / "runtime/speech-to-task-adaptation-eval/manifest.json"
    eval_manifest.parent.mkdir(parents=True)
    eval_manifest.write_text(
        json.dumps(
            {
                "manifest_version": "speech_to_task_adaptation_eval.v1",
                "status": "available",
                "privacy_state": "local_private",
                "export_state": "local_private",
                "split_counts": {"train": 1, "dev": 1, "test": 1},
                "candidate_modes": ["rule"],
                "metrics_by_mode": {},
                "failure_slices": {},
                "privacy_scan": {"status": "passed"},
                field_name: field_value,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(builder.EvidencePackError, match=field_name):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
            adaptation_eval_path=eval_manifest,
        )


@pytest.mark.parametrize(
    ("field_name", "field_value", "message"),
    [
        ("privacy_state", "public_safe", "local/private"),
        ("export_state", "public_safe", "local/private"),
        ("privacy_scan", {"status": "failed"}, "privacy scan"),
    ],
)
def test_release_pack_rejects_unsafe_adaptation_eval_manifest_state(
    tmp_path,
    field_name,
    field_value,
    message,
):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    eval_manifest = tmp_path / "runtime/speech-to-task-adaptation-eval/manifest.json"
    eval_manifest.parent.mkdir(parents=True)
    payload = {
        "manifest_version": "speech_to_task_adaptation_eval.v1",
        "status": "available",
        "privacy_state": "local_private",
        "export_state": "local_private",
        "split_counts": {"train": 1, "dev": 1, "test": 1},
        "candidate_modes": ["rule"],
        "metrics_by_mode": {},
        "failure_slices": {},
        "privacy_scan": {"status": "passed"},
    }
    payload[field_name] = field_value
    eval_manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match=message):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
            adaptation_eval_path=eval_manifest,
        )


def test_release_pack_rejects_private_normalizer_comparison_manifest(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    comparison_path = tmp_path / "runtime/normalizer-comparison/manifest.json"
    comparison_path.parent.mkdir(parents=True)
    comparison_path.write_text(
        json.dumps(
            {
                "status": "available",
                "privacy_state": "local_private",
                "export_state": "local_private",
                "raw_provider_response": "secret",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(builder.EvidencePackError, match="raw_provider_response"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
            normalizer_comparison_path=comparison_path,
        )


def test_release_pack_rejects_malformed_task_pack_runner_manifest(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    run_root = tmp_path / "runtime/public-readonly-task-pack/runs/run-bad"
    run_root.mkdir(parents=True)
    (run_root / "manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "public_readonly_task_pack_run.v1",
                "run_id": "run-bad",
                "rows": [{"task_id": "openai-docs-overview"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(builder.EvidencePackError, match="runner manifest missing"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
            task_pack_run_root=run_root.parent,
        )


def test_release_pack_rejects_public_safe_task_pack_runner_manifest(tmp_path):
    builder = load_builder()
    runner_spec = importlib.util.spec_from_file_location(
        "run_public_readonly_task_pack",
        PROJECT_ROOT / "scripts/run_public_readonly_task_pack.py",
    )
    runner = importlib.util.module_from_spec(runner_spec)
    assert runner_spec and runner_spec.loader
    runner_spec.loader.exec_module(runner)
    trace_root = copy_trace_sources(tmp_path)
    output_dir = tmp_path / "runtime/public-readonly-task-pack"
    manifest = runner.run_task_pack(
        project_root=PROJECT_ROOT,
        output_dir=output_dir,
        task_ids=["openai-docs-overview"],
        mode="deterministic",
        run_id="run-public-safe",
    )
    manifest["privacy_state"] = "public_safe"
    manifest["export_state"] = "public_safe"
    manifest["rows"][0]["evidence_privacy_state"] = "public_safe"
    manifest["rows"][0]["export_state"] = "public_safe"
    (output_dir / "runs/run-public-safe/manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(builder.EvidencePackError, match="local/private"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
            task_pack_run_root=output_dir / "runs",
        )


def test_release_pack_rejects_completed_runner_row_without_proof(tmp_path):
    builder = load_builder()
    runner_spec = importlib.util.spec_from_file_location(
        "run_public_readonly_task_pack",
        PROJECT_ROOT / "scripts/run_public_readonly_task_pack.py",
    )
    runner = importlib.util.module_from_spec(runner_spec)
    assert runner_spec and runner_spec.loader
    runner_spec.loader.exec_module(runner)
    trace_root = copy_trace_sources(tmp_path)
    output_dir = tmp_path / "runtime/public-readonly-task-pack"
    manifest = runner.run_task_pack(
        project_root=PROJECT_ROOT,
        output_dir=output_dir,
        task_ids=["openai-docs-overview"],
        mode="deterministic",
        run_id="run-missing-proof",
    )
    manifest["rows"][0]["observed_proof_summary"] = {}
    (output_dir / "runs/run-missing-proof/manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(builder.EvidencePackError, match="completed runner row"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
            task_pack_run_root=output_dir / "runs",
        )


def test_release_pack_preserves_route_metadata_for_controlled_showcase(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "release-pack",
    )

    showcase = next(
        item for item in manifest["artifacts"] if item["fixture_id"] == "github-showcase"
    )
    assert showcase["evidence_mode"] == "live_controlled"
    assert showcase["route_type"] == "controlled_live"
    assert showcase["route_evidence_mode"] == "controlled_showcase"
    assert showcase["live_evidence_eligible"] is True


def test_release_pack_classifies_agentic_mode_independently_of_execution_mode(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "release-pack",
    )

    agentic_items = [
        item for item in manifest["artifacts"] if item["evidence_mode"] == "agentic_live_controlled"
    ]
    assert agentic_items
    assert all(item["execution_mode"] == "live_controlled" for item in agentic_items)
    assert all(item["agentic_step_count"] > 0 for item in agentic_items)
    assert all(item["visual_verification"]["outcome_counts"] for item in agentic_items)


def test_release_pack_rejects_agentic_trace_missing_visual_verification(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    trace_path = trace_root / "agentic-sanitized/agentic-icon-search.json"
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    for step in payload["agentic_steps"]:
        step.pop("visual_verification_result", None)
    trace_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="visual verification evidence"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_rejects_unsafe_visual_verification_artifacts(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    trace_path = trace_root / "agentic-sanitized/agentic-icon-search.json"
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    verification = payload["agentic_steps"][0]["visual_verification_result"]
    verification["sanitized_evidence_refs"].append("screenshots/raw_screenshot.png")
    trace_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="raw_screenshot"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


@pytest.mark.parametrize("field_name", ["reason", "observed_state_summary"])
def test_release_pack_rejects_private_visual_verification_value_markers(tmp_path, field_name):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    trace_path = trace_root / "agentic-sanitized/agentic-icon-search.json"
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    payload["agentic_steps"][0]["visual_verification_result"][field_name] = (
        "provider returned raw_provider_response with request_headers"
    )
    trace_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="raw_provider_response"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_fails_when_real_vision_evidence_is_missing_or_empty(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    shutil.rmtree(trace_root / "real-vision-sanitized")

    with pytest.raises(builder.EvidencePackError, match="missing real_vision_controlled evidence"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_fails_when_real_voice_evidence_is_missing(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    shutil.rmtree(trace_root / "real-voice-sanitized")

    with pytest.raises(builder.EvidencePackError, match="missing real_voice_controlled evidence"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )

    shutil.rmtree(trace_root / "real-vision-sanitized")
    (trace_root / "real-vision-sanitized").mkdir()
    with pytest.raises(builder.EvidencePackError, match="missing real_vision_controlled evidence"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_fails_when_required_preview_fixture_is_missing(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    (trace_root / "sanitized/demo-github-search.json").unlink()

    with pytest.raises(builder.EvidencePackError, match="demo_preview.*github-search"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_fails_when_trace_is_malformed(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    (trace_root / "sanitized/demo-github-search.json").write_text("{not json", encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="malformed trace"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_fails_when_evidence_mode_has_duplicate_fixture(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    shutil.copy2(
        trace_root / "live-sanitized/live-icon-search.json",
        trace_root / "live-sanitized/live-icon-search-copy.json",
    )

    with pytest.raises(builder.EvidencePackError, match="ambiguous.*live_controlled.*icon-search"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_fails_when_private_marker_is_present(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    trace_path = trace_root / "sanitized/demo-github-search.json"
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    payload["execution_runtime"] = {"raw_audio_path": "/Users/private/command.wav"}
    trace_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="raw_audio_path"):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("raw_page_text", "full public page text"),
        ("visible_text", "raw visible public page text"),
        ("unsanitized_runtime", {"page_text": "raw browser state"}),
        ("local_file_uri", "file:///Users/private/Profile/trace.json"),
    ],
)
def test_release_pack_fails_when_forbidden_raw_trace_field_is_present(
    tmp_path,
    field_name,
    field_value,
):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    trace_path = trace_root / "sanitized/demo-github-search.json"
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    payload["execution_runtime"] = {field_name: field_value}
    trace_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match=field_name):
        builder.build_release_pack(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_reliability_matrix_requires_attempt_evidence(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    copy_project_inputs(tmp_path)
    smoke_path = tmp_path / "fixtures/public-readonly-smoke.json"
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    smoke = add_attempt_evidence(smoke)
    smoke["tasks"][0].pop("reliability_attempt_evidence", None)
    smoke_path.write_text(json.dumps(smoke), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="attempt evidence"):
        builder.build_release_pack(
            project_root=tmp_path,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_reliability_matrix_requires_completed_attempt_proof(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    copy_project_inputs(tmp_path)
    smoke_path = tmp_path / "fixtures/public-readonly-smoke.json"
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    smoke = add_attempt_evidence(smoke)
    smoke["tasks"][0]["reliability_attempt_evidence"]["observed_proof_summary"] = {}
    smoke_path.write_text(json.dumps(smoke), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="observed proof"):
        builder.build_release_pack(
            project_root=tmp_path,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_reliability_matrix_rejects_private_attempt_evidence(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    copy_project_inputs(tmp_path)
    smoke_path = tmp_path / "fixtures/public-readonly-smoke.json"
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    smoke = add_attempt_evidence(smoke)
    smoke["tasks"][0]["reliability_attempt_evidence"]["observed_proof_summary"][
        "raw_page_text"
    ] = "raw public page text"
    smoke_path.write_text(json.dumps(smoke), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="raw_page_text"):
        builder.build_release_pack(
            project_root=tmp_path,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_fails_when_reliability_matrix_outcome_is_missing(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    copy_project_inputs(tmp_path)
    smoke_path = tmp_path / "fixtures/public-readonly-smoke.json"
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    smoke = add_attempt_evidence(smoke)
    for task in smoke["tasks"]:
        evidence = task.get("reliability_attempt_evidence") or {}
        if evidence.get("outcome") == "blocked":
            evidence["outcome"] = "failed"
            evidence["final_status"] = "failed"
            task["expected_matrix_coverage"] = "failed"
    smoke_path.write_text(json.dumps(smoke), encoding="utf-8")

    with pytest.raises(builder.EvidencePackError, match="missing outcome"):
        builder.build_release_pack(
            project_root=tmp_path,
            trace_root=trace_root,
            output_dir=tmp_path / "release-pack",
        )


def test_release_pack_html_uses_bounded_non_benchmark_positioning(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    output_dir = tmp_path / "release-pack"

    builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=output_dir,
    )

    html = (output_dir / "index.html").read_text(encoding="utf-8").lower()
    assert "bounded demo evidence pack" in html
    assert "public-readonly reliability matrix" in html
    assert "real_vision_controlled" in html
    assert "browser-use-vision" in html
    assert "benchmark" not in html
    assert "sota" not in html
    assert "production automation" not in html
    assert "unrestricted public-web autonomy" not in html
