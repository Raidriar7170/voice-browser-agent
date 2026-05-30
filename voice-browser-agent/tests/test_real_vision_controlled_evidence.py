import base64
import importlib.util
import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts/generate_real_vision_trace.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_real_vision_trace", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_committed_real_vision_trace_is_sanitized_and_has_required_metadata():
    traces = sorted((PROJECT_ROOT / "fixtures/traces/real-vision-sanitized").glob("*.json"))
    forbidden = (
        "raw_audio_path",
        "raw_screenshot",
        "browser_profile",
        "cookie",
        "credential",
        "password",
        "token",
        "remote_host",
        "private_url",
        "file:///Users/",
    )

    assert traces
    payload = json.loads(traces[0].read_text(encoding="utf-8"))
    text = json.dumps(payload, ensure_ascii=False)

    assert payload["execution_id"].startswith("real-vision-")
    assert payload["execution_mode"] == "live_controlled"
    assert payload["final_status"] in {"succeeded", "failed", "blocked"}
    assert payload["execution_runtime"]["evidence_mode"] == "real_vision_controlled"
    assert payload["execution_runtime"]["provider"]["package"] == "browser-use-vision"
    assert payload["execution_runtime"]["adapter"]["api"] == "browser_use_vision.som.annotate_screenshot"
    assert payload["execution_runtime"]["privacy_scan"]["status"] == "passed"
    assert payload["grounding_evidence_refs"]
    assert payload["browser_actions"][0]["grounding_evidence_refs"]
    assert not any(word in text for word in forbidden)


def test_real_vision_generator_invokes_browser_use_vision_som(monkeypatch, tmp_path):
    generator = load_generator()
    calls = []

    def fake_annotate_screenshot(screenshot_b64, selector_map, **kwargs):
        calls.append(
            {
                "screenshot_len": len(screenshot_b64),
                "selector_count": len(selector_map),
                "kwargs": kwargs,
            }
        )
        return base64.b64encode(base64.b64decode(screenshot_b64) + b"som-changed").decode("ascii")

    monkeypatch.setattr(generator, "resolve_annotator", lambda: fake_annotate_screenshot)

    payload = generator.generate_real_vision_trace(output_dir=tmp_path)

    assert calls
    assert calls[0]["screenshot_len"] > 100
    assert calls[0]["selector_count"] >= 3
    assert payload["execution_runtime"]["adapter"]["deterministic_controlled_adapter"] is False
    assert payload["execution_runtime"]["visual_evidence"]["annotated_element_count"] >= 3
    assert payload["execution_runtime"]["visual_evidence"]["annotated_image_bytes_discarded"] is True


def test_resolve_annotator_returns_installed_browser_use_vision_som_function():
    generator = load_generator()
    from browser_use_vision.som import annotate_screenshot

    annotator = generator.resolve_annotator()
    empty_png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9Q"
        "DwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    assert annotator is annotate_screenshot
    assert isinstance(annotator(empty_png_b64, {}), str)


def test_real_vision_generator_fails_clearly_when_entrypoint_or_evidence_is_missing(
    monkeypatch, tmp_path
):
    generator = load_generator()

    def missing_entrypoint():
        raise ImportError("browser-use-vision SoM unavailable")

    monkeypatch.setattr(generator, "resolve_annotator", missing_entrypoint)
    with pytest.raises(generator.RealVisionEvidenceError, match="browser-use-vision.*unavailable"):
        generator.generate_real_vision_trace(output_dir=tmp_path)

    monkeypatch.setattr(generator, "resolve_annotator", lambda: (lambda *_args, **_kwargs: ""))
    with pytest.raises(generator.RealVisionEvidenceError, match="missing/no meaningful visual evidence"):
        generator.generate_real_vision_trace(output_dir=tmp_path)

    monkeypatch.setattr(
        generator,
        "resolve_annotator",
        lambda: (lambda screenshot_b64, *_args, **_kwargs: screenshot_b64),
    )
    with pytest.raises(generator.RealVisionEvidenceError, match="missing/no meaningful visual evidence"):
        generator.generate_real_vision_trace(output_dir=tmp_path)


def test_public_evidence_page_covers_real_vision_and_seed_set_contract():
    page = PROJECT_ROOT / "docs/public-evidence/index.html"
    html = page.read_text(encoding="utf-8")
    lower = html.lower()

    required = (
        "Voice-to-Browser Agent",
        "standalone",
        "real_vision_controlled",
        "fixtures/traces/real-vision-sanitized/",
        "uv run python scripts/build_demo_evidence_pack.py",
        "uv run python scripts/build_speech_to_task_dataset.py --seed-set",
        "uv run python scripts/build_speech_to_task_eval.py",
        "runtime/speech-to-task-adaptation-eval/manifest.json",
        "OPENSPEC_TELEMETRY=0 openspec validate --all --strict",
        "60-90 second",
        "docs/demo/video-plan.md",
        "limitations",
    )
    for term in required:
        assert term in html

    forbidden = (
        "benchmark",
        "sota",
        "production automation",
        "unrestricted public-web autonomy",
        "model-quality",
        "checkpoint publication claim",
    )
    assert not any(term in lower for term in forbidden)
