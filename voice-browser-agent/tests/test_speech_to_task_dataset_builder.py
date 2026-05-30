import importlib.util
import json
import shutil
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts/build_speech_to_task_dataset.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_speech_to_task_dataset", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def copy_trace_sources(tmp_path: Path) -> Path:
    source_root = PROJECT_ROOT / "fixtures/traces"
    target_root = tmp_path / "fixtures/traces"
    shutil.copytree(source_root, target_root)
    return target_root


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_dataset_manifest_covers_preview_live_agentic_and_real_vision_traces(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    output_dir = tmp_path / "speech-to-task-dataset"

    manifest = builder.build_dataset(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=output_dir,
    )

    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "examples.jsonl").exists()
    assert manifest["privacy_scan"]["status"] == "passed"
    assert manifest["example_count"] == 16
    assert manifest["evidence_mode_counts"] == {
        "agentic_live_controlled": 3,
        "demo_preview": 8,
        "live_controlled": 4,
        "real_vision_controlled": 1,
    }
    modes = {item["evidence_mode"] for item in manifest["examples"]}
    assert modes == {
        "demo_preview",
        "live_controlled",
        "agentic_live_controlled",
        "real_vision_controlled",
    }
    assert all(item["privacy_scan"] == "passed" for item in manifest["examples"])
    assert all(
        item["source_trace_path"].startswith("fixtures/traces/")
        for item in manifest["examples"]
    )


def test_dataset_manifest_records_provenance_and_jsonl_examples(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    output_dir = tmp_path / "speech-to-task-dataset"

    manifest = builder.build_dataset(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=output_dir,
    )
    rows = read_jsonl(output_dir / "examples.jsonl")

    assert len(rows) == manifest["example_count"]
    icon_row = next(row for row in rows if row["example_id"] == "demo_preview:demo-icon-search")
    icon_manifest = next(
        item for item in manifest["examples"] if item["example_id"] == icon_row["example_id"]
    )
    assert icon_manifest["source_execution_id"] == "demo-icon-search"
    assert icon_manifest["source_trace_path"] == "fixtures/traces/sanitized/demo-icon-search.json"
    assert icon_manifest["final_status"] == "stopped"
    assert icon_manifest["validator_outcome"] == "accepted"
    assert icon_manifest["safety_flags"] == []
    assert icon_row["input"]["transcript_text"] == "点击右上角的放大镜图标"
    assert icon_row["language_metadata"]["language_mode"] == "zh-first"
    assert icon_row["original_target_output"]["kind"] == "browser_task_request"
    assert icon_row["active_target_output"] == icon_row["original_target_output"]
    assert icon_row["validator_decision"]["accepted"] is True
    assert icon_row["correction"]["status"] == "absent"
    assert icon_row["privacy_scan"] == "passed"


def test_dataset_uses_optional_release_pack_manifest_as_provenance(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    release_manifest = tmp_path / "release-pack/manifest.json"
    release_manifest.parent.mkdir()
    release_manifest.write_text(
        json.dumps({"artifacts": [{"fixture_id": "icon-search"}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    manifest = builder.build_dataset(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "speech-to-task-dataset",
        release_pack_manifest=release_manifest,
    )

    assert manifest["release_pack_manifest_path"] == str(release_manifest)
    assert manifest["release_pack_artifact_count"] == 1


def test_dataset_applies_correction_overlay_without_mutating_original_target(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    correction_path = tmp_path / "corrections.json"
    corrected_target = {
        "kind": "browser_task_request",
        "task": "Click the toolbar search icon.",
        "intent_type": "click_visual_target",
        "constraints": ["controlled demo page only"],
        "visual_references": [{"kind": "icon", "text": "magnifying glass"}],
        "requires_confirmation": False,
        "stop_conditions": ["login_required"],
        "safety_flags": [],
    }
    correction_path.write_text(
        json.dumps(
            {
                "corrections": [
                    {
                        "example_id": "demo_preview:demo-icon-search",
                        "target_output": corrected_target,
                        "reason": "tighten English task wording",
                        "note": "Human reviewed for adaptation.",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manifest = builder.build_dataset(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "speech-to-task-dataset",
        correction_overlay=correction_path,
    )
    rows = read_jsonl(tmp_path / "speech-to-task-dataset/examples.jsonl")
    row = next(item for item in rows if item["example_id"] == "demo_preview:demo-icon-search")

    assert manifest["correction_count"] == 1
    assert row["original_target_output"]["task"] == "点击右上角的放大镜图标"
    assert row["active_target_output"]["task"] == "Click the toolbar search icon."
    assert row["corrected_target_output"]["task"] == "Click the toolbar search icon."
    assert row["correction"]["status"] == "applied"
    assert row["correction"]["reason"] == "tighten English task wording"


def test_seed_set_outputs_20_to_50_examples_with_trace_and_variant_provenance(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    overlay = PROJECT_ROOT / "fixtures/seed-set/reviewed-variants.json"
    output_dir = tmp_path / "speech-to-task-seed-set"

    manifest = builder.build_dataset(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=output_dir,
        correction_overlay=overlay,
        seed_set=True,
    )
    rows = read_jsonl(output_dir / "examples.jsonl")

    assert 20 <= manifest["example_count"] <= 50
    assert manifest["seed_set"]["status"] == "adaptation_preparation"
    assert manifest["seed_set"]["trace_derived_count"] == 16
    assert manifest["seed_set"]["reviewed_variant_count"] >= 5
    assert manifest["privacy_scan"]["status"] == "passed"
    assert len(rows) == manifest["example_count"]
    assert all(row["provenance"]["source_trace_id"] for row in rows)
    assert all(row["provenance"]["evidence_mode"] for row in rows)
    assert {row["provenance"]["kind"] for row in rows} >= {
        "trace_derived",
        "reviewed_variant",
    }
    variant = next(row for row in rows if row["provenance"]["kind"] == "reviewed_variant")
    assert variant["original_target_output"]
    assert variant["active_target_output"]
    assert variant["correction"]["status"] == "reviewed_variant"
    assert variant["correction"]["reason"]


def test_seed_set_evaluation_splits_are_stable_and_record_provenance(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    overlay = PROJECT_ROOT / "fixtures/seed-set/reviewed-variants.json"

    first_manifest = builder.build_dataset(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "first",
        correction_overlay=overlay,
        seed_set=True,
        evaluation_splits=True,
    )
    second_manifest = builder.build_dataset(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=tmp_path / "second",
        correction_overlay=overlay,
        seed_set=True,
        evaluation_splits=True,
    )
    rows = read_jsonl(tmp_path / "first/examples.jsonl")

    first_assignments = {
        item["example_id"]: item["split"] for item in first_manifest["examples"]
    }
    second_assignments = {
        item["example_id"]: item["split"] for item in second_manifest["examples"]
    }
    assert first_assignments == second_assignments
    assert set(first_manifest["evaluation_splits"]["split_counts"]) == {"train", "dev", "test"}
    assert all(count > 0 for count in first_manifest["evaluation_splits"]["split_counts"].values())
    assert first_manifest["evaluation_splits"]["target_kind_counts"] == {
        row["active_target_output"]["kind"]: sum(
            1 for item in rows if item["active_target_output"]["kind"] == row["active_target_output"]["kind"]
        )
        for row in rows
    }
    assert first_manifest["evaluation_splits"]["evidence_mode_counts"] == {
        row["evidence_mode"]: sum(1 for item in rows if item["evidence_mode"] == row["evidence_mode"])
        for row in rows
    }
    assert {row["split"] for row in rows} == {"train", "dev", "test"}
    assert all(row["split"] == first_assignments[row["example_id"]] for row in rows)
    for row in rows:
        provenance = row["split_provenance"]
        assert provenance["example_id"] == row["example_id"]
        assert provenance["source_trace_id"] == row["source_execution_id"]
        assert provenance["source_trace_path"].startswith("fixtures/traces/")
        assert provenance["provenance_kind"] in {"trace_derived", "reviewed_variant"}
        assert provenance["evidence_mode"] == row["evidence_mode"]
        assert provenance["target_output_kind"] == row["active_target_output"]["kind"]
        assert provenance["correction_or_variant_status"] == row["correction"]["status"]
        assert provenance["privacy_scan"] == "passed"


def test_evaluation_split_validation_rejects_empty_duplicate_omitted_and_private_metadata():
    builder = load_builder()
    rows = [
        {
            "example_id": "a",
            "source_execution_id": "trace-a",
            "source_trace_path": "fixtures/traces/sanitized/a.json",
            "evidence_mode": "demo_preview",
            "provenance": {"kind": "trace_derived"},
            "active_target_output": {"kind": "browser_task_request"},
            "correction": {"status": "absent"},
            "privacy_scan": "passed",
        },
        {
            "example_id": "b",
            "source_execution_id": "trace-b",
            "source_trace_path": "fixtures/traces/sanitized/b.json",
            "evidence_mode": "demo_preview",
            "provenance": {"kind": "trace_derived"},
            "active_target_output": {"kind": "clarification_request"},
            "correction": {"status": "absent"},
            "privacy_scan": "passed",
        },
        {
            "example_id": "c",
            "source_execution_id": "trace-c",
            "source_trace_path": "fixtures/traces/sanitized/c.json",
            "evidence_mode": "demo_preview",
            "provenance": {"kind": "trace_derived"},
            "active_target_output": {"kind": "browser_task_request"},
            "correction": {"status": "absent"},
            "privacy_scan": "passed",
        },
    ]

    with pytest.raises(builder.DatasetBuildError, match="empty held-out split"):
        builder.validate_evaluation_split_rows(
            rows,
            [
                {"example_id": "a", "split": "train", "split_provenance": {"privacy_scan": "passed"}},
                {"example_id": "b", "split": "train", "split_provenance": {"privacy_scan": "passed"}},
                {"example_id": "c", "split": "test", "split_provenance": {"privacy_scan": "passed"}},
            ],
        )
    with pytest.raises(builder.DatasetBuildError, match="duplicate split assignment"):
        builder.validate_evaluation_split_rows(
            rows,
            [
                {"example_id": "a", "split": "train", "split_provenance": {"privacy_scan": "passed"}},
                {"example_id": "a", "split": "dev", "split_provenance": {"privacy_scan": "passed"}},
                {"example_id": "b", "split": "test", "split_provenance": {"privacy_scan": "passed"}},
                {"example_id": "c", "split": "train", "split_provenance": {"privacy_scan": "passed"}},
            ],
        )
    with pytest.raises(builder.DatasetBuildError, match="omitted examples"):
        builder.validate_evaluation_split_rows(
            rows,
            [
                {"example_id": "a", "split": "train", "split_provenance": {"privacy_scan": "passed"}},
                {"example_id": "b", "split": "dev", "split_provenance": {"privacy_scan": "passed"}},
            ],
        )
    unsafe_rows = [dict(rows[0]), dict(rows[1]), dict(rows[2])]
    unsafe_rows[0]["source_trace_path"] = "file:///Users/private/trace.json"
    with pytest.raises(builder.DatasetBuildError, match="file:///Users/"):
        builder.build_evaluation_split_rows(unsafe_rows)


@pytest.mark.parametrize("privacy_status", ["failed", "pending", None])
def test_evaluation_split_validation_rejects_non_passed_privacy_scan(privacy_status):
    builder = load_builder()
    rows = [
        {
            "example_id": "a",
            "source_execution_id": "trace-a",
            "source_trace_path": "fixtures/traces/sanitized/a.json",
            "evidence_mode": "demo_preview",
            "provenance": {"kind": "trace_derived"},
            "active_target_output": {"kind": "browser_task_request"},
            "correction": {"status": "absent"},
            "privacy_scan": "passed",
        },
        {
            "example_id": "b",
            "source_execution_id": "trace-b",
            "source_trace_path": "fixtures/traces/sanitized/b.json",
            "evidence_mode": "demo_preview",
            "provenance": {"kind": "trace_derived"},
            "active_target_output": {"kind": "clarification_request"},
            "correction": {"status": "absent"},
            "privacy_scan": "passed",
        },
        {
            "example_id": "c",
            "source_execution_id": "trace-c",
            "source_trace_path": "fixtures/traces/sanitized/c.json",
            "evidence_mode": "demo_preview",
            "provenance": {"kind": "trace_derived"},
            "active_target_output": {"kind": "browser_task_request"},
            "correction": {"status": "absent"},
            "privacy_scan": "passed",
        },
    ]
    split_rows = [
        {"example_id": "a", "split": "train", "split_provenance": {"privacy_scan": "passed"}},
        {"example_id": "b", "split": "dev", "split_provenance": {"privacy_scan": privacy_status}},
        {"example_id": "c", "split": "test", "split_provenance": {"privacy_scan": "passed"}},
    ]

    with pytest.raises(builder.DatasetBuildError, match="split provenance privacy scan"):
        builder.validate_evaluation_split_rows(rows, split_rows)


def test_dataset_fails_when_trace_lacks_required_adaptation_inputs(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    trace_path = trace_root / "sanitized/demo-icon-search.json"
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    del payload["normalized_output"]
    trace_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.DatasetBuildError, match="normalized output.*demo-icon-search"):
        builder.build_dataset(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "speech-to-task-dataset",
        )


def test_dataset_fails_on_duplicate_example_id(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    duplicate_path = trace_root / "sanitized/demo-icon-search-copy.json"
    shutil.copy2(trace_root / "sanitized/demo-icon-search.json", duplicate_path)

    with pytest.raises(
        builder.DatasetBuildError,
        match="duplicate example id.*demo_preview:demo-icon-search",
    ):
        builder.build_dataset(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "speech-to-task-dataset",
        )


def test_dataset_fails_on_unknown_or_malformed_correction_overlay(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    unknown_path = tmp_path / "unknown-correction.json"
    unknown_path.write_text(
        json.dumps(
            {
                "corrections": [
                    {
                        "example_id": "demo_preview:missing-example",
                        "target_output": {"kind": "clarification_request"},
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        builder.DatasetBuildError,
        match="unknown correction target.*missing-example",
    ):
        builder.build_dataset(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "speech-to-task-dataset",
            correction_overlay=unknown_path,
        )

    malformed_path = tmp_path / "malformed-correction.json"
    malformed_path.write_text(
        json.dumps({"corrections": [{"example_id": "demo_preview:demo-icon-search"}]}),
        encoding="utf-8",
    )
    with pytest.raises(builder.DatasetBuildError, match="malformed correction"):
        builder.build_dataset(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "speech-to-task-dataset",
            correction_overlay=malformed_path,
        )


def test_dataset_fails_when_private_marker_is_present(tmp_path):
    builder = load_builder()
    trace_root = copy_trace_sources(tmp_path)
    trace_path = trace_root / "sanitized/demo-icon-search.json"
    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    payload["execution_runtime"] = {"raw_audio_path": "/Users/private/command.wav"}
    trace_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.DatasetBuildError, match="raw_audio_path"):
        builder.build_dataset(
            project_root=PROJECT_ROOT,
            trace_root=trace_root,
            output_dir=tmp_path / "speech-to-task-dataset",
        )

    safe_trace_root = copy_trace_sources(tmp_path / "safe")
    correction_path = tmp_path / "private-correction.json"
    correction_path.write_text(
        json.dumps(
            {
                "corrections": [
                    {
                        "example_id": "demo_preview:demo-icon-search",
                        "target_output": {"kind": "clarification_request", "token": "secret"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(builder.DatasetBuildError, match="token"):
        builder.build_dataset(
            project_root=PROJECT_ROOT,
            trace_root=safe_trace_root,
            output_dir=tmp_path / "speech-to-task-dataset",
            correction_overlay=correction_path,
        )
