import importlib.util
import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from voice_browser_agent.app import create_app
from voice_browser_agent.asr import FallbackASRAdapter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAV_BYTES = b"RIFF\x24\x00\x00\x00WAVEfmt "


class IconSearchASRAdapter:
    name = "real-use-smoke-asr"

    async def transcribe(self, command_input):
        return FallbackASRAdapter.from_text(
            text="点右上角搜索图标",
            command_input=command_input,
            adapter_name=self.name,
            confidence=0.91,
            diagnostics={"source": "uploaded-audio-smoke"},
        )


def load_script(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def copy_trace_sources(tmp_path: Path) -> Path:
    source_root = PROJECT_ROOT / "fixtures/traces"
    target_root = tmp_path / "fixtures/traces"
    shutil.copytree(source_root, target_root)
    return target_root


def test_preflight_report_and_api_are_sanitized(tmp_path):
    from voice_browser_agent.preflight import build_readiness_report

    report = build_readiness_report(project_root=PROJECT_ROOT, runtime_dir=tmp_path)
    text = json.dumps(report, ensure_ascii=False)

    assert report["project"] == "Voice-to-Browser Agent"
    assert {"primary_asr", "fallback_asr", "browser_automation", "real_vision_grounding", "runtime_privacy", "normalizer"}.issubset(
        report["checks"]
    )
    assert report["checks"]["runtime_privacy"]["status"] == "ready"
    assert report["checks"]["normalizer"]["status"] == "ready"
    assert report["checks"]["normalizer"]["provider_mode"] == "rule"
    assert report["recommended_actions"]
    assert "file:///Users/" not in text
    assert "raw_audio_path" not in text
    assert "remote_host" not in text

    client = TestClient(create_app(runtime_dir=tmp_path))
    response = client.get("/api/readiness")
    assert response.status_code == 200
    assert response.json()["checks"]["runtime_privacy"]["status"] == "ready"
    assert response.json()["checks"]["normalizer"]["provider_mode"] == "rule"


def test_preflight_reports_mock_and_misconfigured_llm_normalizer(monkeypatch, tmp_path):
    from voice_browser_agent.preflight import build_readiness_report

    monkeypatch.setenv("VOICE_BROWSER_NORMALIZER_PROVIDER", "mock_llm")
    mock_report = build_readiness_report(project_root=PROJECT_ROOT, runtime_dir=tmp_path / "mock")
    assert mock_report["checks"]["normalizer"]["status"] == "ready"
    assert mock_report["checks"]["normalizer"]["provider_mode"] == "mock_llm"

    monkeypatch.setenv("VOICE_BROWSER_NORMALIZER_PROVIDER", "openai_compatible")
    monkeypatch.delenv("VOICE_BROWSER_NORMALIZER_ENDPOINT_URL", raising=False)
    llm_report = build_readiness_report(project_root=PROJECT_ROOT, runtime_dir=tmp_path / "llm")
    assert llm_report["checks"]["normalizer"]["status"] == "misconfigured"
    assert llm_report["checks"]["normalizer"]["provider_mode"] == "openai_compatible"
    assert "endpoint" in llm_report["checks"]["normalizer"]["detail"].lower()
    normalizer_text = json.dumps(llm_report["checks"]["normalizer"], ensure_ascii=False).lower()
    assert "normalizer_endpoint_url" not in normalizer_text
    assert "api_key" not in normalizer_text


def test_audio_can_be_transcribed_reviewed_and_executed_as_real_voice_controlled(tmp_path):
    app = create_app(runtime_dir=tmp_path)
    app.state.voice_browser.asr_orchestrator.primary = IconSearchASRAdapter()
    client = TestClient(app)

    ingest = client.post(
        "/api/ingest",
        files={"file": ("command.wav", WAV_BYTES, "audio/wav")},
    )
    assert ingest.status_code == 200
    audio_id = ingest.json()["audio_id"]

    transcript = client.post(f"/api/audio/{audio_id}/transcript")
    assert transcript.status_code == 200
    assert transcript.json()["text"] == "点右上角搜索图标"
    assert transcript.json()["metadata"]["adapter_name"] == "real-use-smoke-asr"

    execution = client.post(
        "/api/executions",
        json={
            "audio_id": audio_id,
            "reviewed_transcript_text": "点击右上角的放大镜图标",
            "execution_mode": "live_controlled",
            "controlled_fixture_id": "icon-search",
        },
    )
    assert execution.status_code == 200
    body = execution.json()

    assert body["transcript"]["text"] == "点击右上角的放大镜图标"
    assert body["transcript"]["metadata"]["adapter_name"] == "real-use-smoke-asr"
    diagnostics = body["transcript"]["metadata"]["diagnostics"]
    assert diagnostics["input_source"] == "audio"
    assert diagnostics["transcript_review"]["status"] == "edited"
    assert diagnostics["transcript_review"]["original_text"] == "点右上角搜索图标"
    assert body["execution_runtime"]["evidence_mode"] == "real_voice_controlled"
    assert body["execution_runtime"]["input_source"] == "audio"
    assert body["execution_mode"] == "live_controlled"
    assert body["browser_actions"] or body["grounding_evidence_refs"]
    assert "storage_path" not in json.dumps(body, ensure_ascii=False)


def test_audio_transcript_endpoint_reports_unavailable_asr(tmp_path):
    client = TestClient(create_app(runtime_dir=tmp_path))
    ingest = client.post(
        "/api/ingest",
        files={"file": ("command.wav", WAV_BYTES, "audio/wav")},
    )
    audio_id = ingest.json()["audio_id"]

    response = client.post(f"/api/audio/{audio_id}/transcript")

    assert response.status_code == 503
    assert "ASR" in response.text or "asr" in response.text


def test_real_voice_generator_writes_sanitized_trace_and_rejects_non_audio_sources(tmp_path):
    generator = load_script(
        PROJECT_ROOT / "scripts/generate_real_voice_trace.py",
        "generate_real_voice_trace",
    )

    payload = generator.generate_real_voice_trace(output_dir=tmp_path)
    text = json.dumps(payload, ensure_ascii=False)

    assert payload["execution_id"].startswith("real-voice-")
    assert payload["execution_runtime"]["evidence_mode"] == "real_voice_controlled"
    assert payload["execution_runtime"]["input_source"] == "audio"
    assert payload["transcript"]["metadata"]["adapter_name"] == "real-use-smoke-asr"
    assert payload["transcript"]["metadata"]["diagnostics"]["transcript_review"]["status"] == "edited"
    assert payload["browser_actions"] or payload["grounding_evidence_refs"]
    assert "raw_audio_path" not in text
    assert "storage_path" not in text
    assert "file:///Users/" not in text

    with pytest.raises(generator.RealVoiceEvidenceError, match="source-mismatch"):
        generator.build_real_voice_trace_payload(input_source="fixture")


def test_release_pack_includes_real_voice_and_failure_usage_evidence(tmp_path):
    builder = load_script(
        PROJECT_ROOT / "scripts/build_demo_evidence_pack.py",
        "build_demo_evidence_pack_for_real_voice",
    )
    trace_root = copy_trace_sources(tmp_path)
    output_dir = tmp_path / "release-pack"

    manifest = builder.build_release_pack(
        project_root=PROJECT_ROOT,
        trace_root=trace_root,
        output_dir=output_dir,
    )

    modes = {item["evidence_mode"] for item in manifest["artifacts"]}
    assert "real_voice_controlled" in modes
    assert "real_use_failure" in modes
    real_voice = [item for item in manifest["artifacts"] if item["evidence_mode"] == "real_voice_controlled"]
    failures = [item for item in manifest["artifacts"] if item["evidence_mode"] == "real_use_failure"]
    assert {item["fixture_id"] for item in real_voice} == {"icon-search"}
    assert len(failures) >= 5
    assert all(item["privacy_scan"] == "passed" for item in real_voice + failures)
