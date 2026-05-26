import pytest

from voice_browser_agent.asr import (
    ASRAdapterError,
    ASRUnavailable,
    FallbackASRAdapter,
    TranscriptOrchestrator,
)
from voice_browser_agent.ingestion import AudioIngestor, IngestionError


WAV_BYTES = b"RIFF\x24\x00\x00\x00WAVEfmt "
WEBM_BYTES = b"\x1a\x45\xdf\xa3demo-webm"


class PrimaryFailsAdapter:
    name = "primary"

    async def transcribe(self, command_input):
        raise ASRUnavailable("primary unavailable")


class FixtureFallbackAdapter:
    name = "fixture-fallback"

    async def transcribe(self, command_input):
        return FallbackASRAdapter.from_text(
            text="打开 GitHub 搜索 browser-use-vision",
            command_input=command_input,
            adapter_name=self.name,
            confidence=0.88,
        )


def test_audio_ingestor_accepts_one_supported_clip(tmp_path):
    ingestor = AudioIngestor(storage_dir=tmp_path)

    command_input = ingestor.ingest_upload(
        filename="command.webm",
        content_type="audio/webm",
        data=WEBM_BYTES,
    )

    assert command_input.source_type == "upload"
    assert command_input.audio_id.endswith(".webm")
    assert command_input.size_bytes == len(WEBM_BYTES)


def test_audio_ingestor_rejects_unsupported_audio_before_asr(tmp_path):
    ingestor = AudioIngestor(storage_dir=tmp_path)

    with pytest.raises(IngestionError, match="Unsupported audio"):
        ingestor.ingest_upload(
            filename="notes.txt",
            content_type="text/plain",
            data=b"not audio",
        )


def test_audio_ingestor_rejects_corrupt_supported_audio_before_asr(tmp_path):
    ingestor = AudioIngestor(storage_dir=tmp_path)

    with pytest.raises(IngestionError, match="Unsupported or corrupt audio"):
        ingestor.ingest_upload(
            filename="command.wav",
            content_type="audio/wav",
            data=b"not a wav file",
        )


@pytest.mark.asyncio
async def test_asr_orchestrator_uses_fallback_and_preserves_metadata(tmp_path):
    command_input = AudioIngestor(storage_dir=tmp_path).ingest_upload(
        filename="command.wav",
        content_type="audio/wav",
        data=WAV_BYTES,
    )
    orchestrator = TranscriptOrchestrator(
        primary=PrimaryFailsAdapter(),
        fallback=FixtureFallbackAdapter(),
    )

    transcript = await orchestrator.transcribe(command_input)

    assert transcript.text == "打开 GitHub 搜索 browser-use-vision"
    assert transcript.metadata.adapter_name == "fixture-fallback"
    assert transcript.metadata.input_audio_id == command_input.audio_id
    assert transcript.metadata.language_mode == "zh-first"
    assert transcript.metadata.confidence == 0.88


@pytest.mark.asyncio
async def test_asr_orchestrator_raises_when_no_adapter_can_transcribe(tmp_path):
    command_input = AudioIngestor(storage_dir=tmp_path).ingest_upload(
        filename="command.wav",
        content_type="audio/wav",
        data=WAV_BYTES,
    )
    orchestrator = TranscriptOrchestrator(primary=PrimaryFailsAdapter(), fallback=None)

    with pytest.raises(ASRAdapterError, match="No ASR adapter"):
        await orchestrator.transcribe(command_input)
