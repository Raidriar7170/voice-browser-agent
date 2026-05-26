from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import httpx

from .models import ASRTranscript, ASRTranscriptMetadata, SpokenCommandInput


class ASRAdapterError(RuntimeError):
    pass


class ASRUnavailable(ASRAdapterError):
    pass


class ASRAdapter(Protocol):
    name: str

    async def transcribe(self, command_input: SpokenCommandInput) -> ASRTranscript:
        ...


@dataclass
class TranscriptOrchestrator:
    primary: ASRAdapter
    fallback: ASRAdapter | None = None

    async def transcribe(self, command_input: SpokenCommandInput) -> ASRTranscript:
        try:
            return await self.primary.transcribe(command_input)
        except ASRUnavailable as primary_error:
            if self.fallback is None:
                raise ASRAdapterError("No ASR adapter could transcribe the audio") from primary_error
            return await self.fallback.transcribe(command_input)
        except ASRAdapterError:
            raise


class UnavailableASRAdapter:
    name = "unconfigured-asr"

    async def transcribe(self, command_input: SpokenCommandInput) -> ASRTranscript:
        raise ASRUnavailable("No primary ASR backend is configured")


class FixtureManifestASRAdapter:
    name = "fixture-manifest-asr"

    async def transcribe(self, command_input: SpokenCommandInput) -> ASRTranscript:
        if command_input.source_type != "fixture" or command_input.storage_path is None:
            raise ASRUnavailable("Fixture ASR only handles fixture command inputs")
        payload = json.loads(Path(command_input.storage_path).read_text(encoding="utf-8"))
        text = payload.get("expected_transcript") or payload.get("spoken_text")
        if not text:
            raise ASRAdapterError("Fixture manifest is missing expected_transcript")
        return FallbackASRAdapter.from_text(
            text=text,
            command_input=command_input,
            adapter_name=self.name,
            confidence=1.0,
            diagnostics={"fixture": True, "source": payload.get("source", "fixture")},
        )


class RemoteASRAdapter:
    def __init__(self, endpoint_url: str, name: str = "primary-asr", timeout_seconds: float = 30):
        self.endpoint_url = endpoint_url
        self.name = name
        self.timeout_seconds = timeout_seconds

    async def transcribe(self, command_input: SpokenCommandInput) -> ASRTranscript:
        if command_input.storage_path is None:
            raise ASRUnavailable("Remote ASR requires a stored audio file")

        path = Path(command_input.storage_path)
        if not path.exists():
            raise ASRUnavailable(f"Audio file is missing: {path.name}")

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            with path.open("rb") as audio_file:
                response = await client.post(
                    self.endpoint_url,
                    files={"file": (command_input.audio_id, audio_file, command_input.content_type)},
                )
        if response.status_code >= 500:
            raise ASRUnavailable(f"Primary ASR service unavailable: {response.status_code}")
        if response.status_code >= 400:
            raise ASRAdapterError(f"ASR service rejected audio: {response.status_code}")

        payload = response.json()
        text = payload.get("text") or payload.get("transcript")
        if not text:
            raise ASRAdapterError("ASR response did not include transcript text")
        return FallbackASRAdapter.from_text(
            text=text,
            command_input=command_input,
            adapter_name=self.name,
            confidence=payload.get("confidence"),
            diagnostics={"remote_status": response.status_code, **payload.get("diagnostics", {})},
        )


class FallbackASRAdapter:
    name = "faster-whisper-fallback"

    def __init__(self, model_size: str = "base", language_mode: str = "zh-first"):
        self.model_size = model_size
        self.language_mode = language_mode

    async def transcribe(self, command_input: SpokenCommandInput) -> ASRTranscript:
        if command_input.storage_path is None:
            raise ASRUnavailable("Fallback ASR requires a stored audio file")
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise ASRUnavailable("faster-whisper is not installed") from exc

        model = WhisperModel(self.model_size)
        segments, info = model.transcribe(str(command_input.storage_path), language="zh")
        text = "".join(segment.text for segment in segments).strip()
        if not text:
            raise ASRAdapterError("Fallback ASR produced an empty transcript")
        return self.from_text(
            text=text,
            command_input=command_input,
            adapter_name=self.name,
            confidence=getattr(info, "language_probability", None),
            diagnostics={"model_size": self.model_size},
        )

    @staticmethod
    def from_text(
        text: str,
        command_input: SpokenCommandInput,
        adapter_name: str,
        confidence: float | None = None,
        diagnostics: dict | None = None,
    ) -> ASRTranscript:
        return ASRTranscript(
            text=text,
            metadata=ASRTranscriptMetadata(
                adapter_name=adapter_name,
                input_audio_id=command_input.audio_id,
                language_mode="zh-first",
                confidence=confidence,
                diagnostics=diagnostics or {},
            ),
        )
