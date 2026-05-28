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
    assert "real_vision_controlled" in html
    assert "browser-use-vision" in html
    assert "benchmark" not in html
    assert "sota" not in html
    assert "production automation" not in html
    assert "unrestricted public-web autonomy" not in html
