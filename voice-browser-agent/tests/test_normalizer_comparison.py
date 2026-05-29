import importlib.util
import json
import shutil
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts/build_normalizer_comparison.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_normalizer_comparison", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def copy_project_inputs(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(PROJECT_ROOT / "fixtures", project_root / "fixtures")
    return project_root


def test_normalizer_comparison_builds_local_private_manifest_from_fixtures_and_seed_set(tmp_path):
    builder = load_builder()
    project_root = copy_project_inputs(tmp_path)
    output_dir = tmp_path / "normalizer-comparison"

    manifest = builder.build_comparison(
        project_root=project_root,
        trace_root=project_root / "fixtures/traces",
        output_dir=output_dir,
        seed_set=True,
    )

    assert (output_dir / "manifest.json").exists()
    assert manifest["status"] == "available"
    assert manifest["privacy_state"] == "local_private"
    assert manifest["export_state"] == "local_private"
    assert manifest["positioning"] == "structured_output_comparison_not_model_training"
    assert manifest["input_count"] >= 8
    assert set(manifest["normalizer_modes"]) == {"rule", "mock_llm"}
    assert manifest["privacy_scan"]["status"] == "passed"
    assert manifest["mode_counts"]["rule"] == manifest["input_count"]
    assert manifest["mode_counts"]["mock_llm"] == manifest["input_count"]
    assert manifest["fallback_counts"]["mock_llm"] == 0
    assert all(row["privacy_scan"] == "passed" for row in manifest["rows"])
    assert all("validator_outcome" in row for row in manifest["rows"])
    assert "model checkpoint" not in json.dumps(manifest, ensure_ascii=False).lower()


def test_normalizer_comparison_fails_on_private_marker_in_source_input(tmp_path):
    builder = load_builder()
    project_root = copy_project_inputs(tmp_path)
    fixture_path = project_root / "fixtures/audio/icon-search.fixture.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    payload["expected_transcript"] = "use token secret"
    fixture_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(builder.NormalizerComparisonError, match="token"):
        builder.build_comparison(
            project_root=project_root,
            trace_root=project_root / "fixtures/traces",
            output_dir=tmp_path / "normalizer-comparison",
        )


def test_normalizer_comparison_real_provider_requires_explicit_endpoint(monkeypatch, tmp_path):
    builder = load_builder()
    project_root = copy_project_inputs(tmp_path)
    monkeypatch.setenv("VOICE_BROWSER_NORMALIZER_PROVIDER", "openai_compatible")
    monkeypatch.delenv("VOICE_BROWSER_NORMALIZER_ENDPOINT_URL", raising=False)

    with pytest.raises(builder.NormalizerComparisonError, match="ENDPOINT_URL"):
        builder.build_comparison(
            project_root=project_root,
            trace_root=project_root / "fixtures/traces",
            output_dir=tmp_path / "normalizer-comparison",
            include_real_provider=True,
        )
