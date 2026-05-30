import importlib.util
import json
import shutil
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_SCRIPT_PATH = PROJECT_ROOT / "scripts/build_speech_to_task_dataset.py"
EVAL_SCRIPT_PATH = PROJECT_ROOT / "scripts/build_speech_to_task_eval.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def copy_trace_sources(tmp_path: Path) -> Path:
    source_root = PROJECT_ROOT / "fixtures/traces"
    target_root = tmp_path / "fixtures/traces"
    shutil.copytree(source_root, target_root)
    return target_root


def build_split_dataset(tmp_path: Path) -> Path:
    dataset = load_module(DATASET_SCRIPT_PATH, "build_speech_to_task_dataset")
    dataset.build_dataset(
        project_root=PROJECT_ROOT,
        trace_root=copy_trace_sources(tmp_path),
        output_dir=tmp_path / "speech-to-task-dataset",
        correction_overlay=PROJECT_ROOT / "fixtures/seed-set/reviewed-variants.json",
        seed_set=True,
        evaluation_splits=True,
    )
    return tmp_path / "speech-to-task-dataset/manifest.json"


def test_eval_harness_scores_rule_and_mock_llm_on_held_out_split(tmp_path):
    evaluator = load_module(EVAL_SCRIPT_PATH, "build_speech_to_task_eval")
    dataset_manifest = build_split_dataset(tmp_path)

    manifest = evaluator.build_evaluation(
        dataset_manifest_path=dataset_manifest,
        output_dir=tmp_path / "speech-to-task-eval",
    )

    assert (tmp_path / "speech-to-task-eval/manifest.json").exists()
    assert (tmp_path / "speech-to-task-eval/summary.json").exists()
    assert manifest["manifest_version"] == "speech_to_task_adaptation_eval.v1"
    assert manifest["status"] == "available"
    assert manifest["privacy_state"] == "local_private"
    assert manifest["split"] == "test"
    assert set(manifest["candidate_modes"]) == {"rule", "mock_llm"}
    assert manifest["row_count"] == manifest["split_counts"]["test"] * 2
    assert manifest["privacy_scan"]["status"] == "passed"
    for mode in ("rule", "mock_llm"):
        metrics = manifest["metrics_by_mode"][mode]
        assert metrics["row_count"] == manifest["split_counts"]["test"]
        assert 0 <= metrics["schema_valid_rate"] <= 1
        assert "output_kind_accuracy" in metrics
        assert "intent_type_accuracy" in metrics
        assert "required_slot_match_rate" in metrics
        assert "safety_or_clarification_decision_accuracy" in metrics
        assert "route_ready_rate" in metrics
        assert "fallback_rate" in metrics
    assert {"candidate_mode", "split", "evidence_mode", "target_output_kind"}.issubset(
        manifest["failure_slices"]
    )
    row = manifest["rows"][0]
    assert row["example_id"]
    assert row["source_trace_path"].startswith("fixtures/traces/")
    assert row["candidate_mode"] in {"rule", "mock_llm"}
    assert row["schema_status"] in {"passed", "failed", "not_applicable"}
    assert row["privacy_scan"] == "passed"
    assert "candidate_output" not in row


def test_eval_harness_accepts_candidate_jsonl_and_records_malformed_rows(tmp_path):
    evaluator = load_module(EVAL_SCRIPT_PATH, "build_speech_to_task_eval")
    dataset_manifest = build_split_dataset(tmp_path)
    examples = evaluator.load_dataset_examples(dataset_manifest, split="test")
    candidate_path = tmp_path / "candidate.jsonl"
    lines = []
    for index, example in enumerate(examples):
        if index == 0:
            payload = {"kind": "not_a_supported_output"}
        else:
            payload = example["active_target_output"]
        lines.append(
            json.dumps(
                {
                    "example_id": example["example_id"],
                    "output": payload,
                },
                ensure_ascii=False,
            )
        )
    candidate_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = evaluator.build_evaluation(
        dataset_manifest_path=dataset_manifest,
        output_dir=tmp_path / "speech-to-task-eval",
        candidate_output_jsonl={"adapted_model_jsonl": candidate_path},
    )

    assert "adapted_model_jsonl" in manifest["candidate_modes"]
    rows = [
        row
        for row in manifest["rows"]
        if row["candidate_mode"] == "adapted_model_jsonl"
    ]
    assert any(row["schema_status"] == "failed" for row in rows)
    assert any("unknown kind" in (row["schema_failure_reason"] or "") for row in rows)
    assert manifest["metrics_by_mode"]["adapted_model_jsonl"]["schema_valid_count"] == len(rows) - 1


@pytest.mark.parametrize(
    ("records", "message"),
    [
        ([{"example_id": "missing", "output": {"kind": "clarification_request"}}], "missing ids"),
        ([], "missing ids"),
    ],
)
def test_eval_harness_rejects_candidate_jsonl_with_missing_or_extra_ids(
    tmp_path,
    records,
    message,
):
    evaluator = load_module(EVAL_SCRIPT_PATH, "build_speech_to_task_eval")
    dataset_manifest = build_split_dataset(tmp_path)
    candidate_path = tmp_path / "bad-candidate.jsonl"
    candidate_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(evaluator.SpeechToTaskEvalError, match=message):
        evaluator.build_evaluation(
            dataset_manifest_path=dataset_manifest,
            output_dir=tmp_path / "speech-to-task-eval",
            candidate_output_jsonl={"bad_jsonl": candidate_path},
        )


def test_eval_harness_rejects_duplicate_candidate_ids_and_private_markers(tmp_path):
    evaluator = load_module(EVAL_SCRIPT_PATH, "build_speech_to_task_eval")
    dataset_manifest = build_split_dataset(tmp_path)
    examples = evaluator.load_dataset_examples(dataset_manifest, split="test")
    duplicate_path = tmp_path / "duplicate.jsonl"
    duplicate_path.write_text(
        "\n".join(
            json.dumps(
                {
                    "example_id": examples[0]["example_id"],
                    "output": examples[0]["active_target_output"],
                }
            )
            for _ in range(2)
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(evaluator.SpeechToTaskEvalError, match="duplicate candidate id"):
        evaluator.build_evaluation(
            dataset_manifest_path=dataset_manifest,
            output_dir=tmp_path / "speech-to-task-eval",
            candidate_output_jsonl={"duplicate": duplicate_path},
        )

    unsafe_path = tmp_path / "unsafe.jsonl"
    unsafe_path.write_text(
        json.dumps(
            {
                "example_id": examples[0]["example_id"],
                "output": examples[0]["active_target_output"],
                "raw_provider_response": "secret payload",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(evaluator.SpeechToTaskEvalError, match="raw_provider_response"):
        evaluator.build_evaluation(
            dataset_manifest_path=dataset_manifest,
            output_dir=tmp_path / "speech-to-task-eval",
            candidate_output_jsonl={"unsafe": unsafe_path},
        )
