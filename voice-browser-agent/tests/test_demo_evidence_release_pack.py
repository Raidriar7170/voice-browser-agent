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
    assert "raw_page_text" not in json.dumps(useful, ensure_ascii=False)


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
