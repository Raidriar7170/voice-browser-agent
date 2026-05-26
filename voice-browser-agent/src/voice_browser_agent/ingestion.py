from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from .models import SpokenCommandInput


SUPPORTED_AUDIO_TYPES = {
    "audio/wav": ".wav",
    "audio/wave": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/flac": ".flac",
}
SUPPORTED_SUFFIXES = set(SUPPORTED_AUDIO_TYPES.values())
MAGIC_HEADERS = {
    ".wav": lambda data: len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WAVE",
    ".webm": lambda data: data.startswith(b"\x1a\x45\xdf\xa3"),
    ".mp3": lambda data: data.startswith(b"ID3") or data[:2] in {b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"},
    ".m4a": lambda data: len(data) >= 12 and data[4:8] == b"ftyp",
    ".ogg": lambda data: data.startswith(b"OggS"),
    ".flac": lambda data: data.startswith(b"fLaC"),
}


class IngestionError(ValueError):
    pass


class AudioIngestor:
    def __init__(self, storage_dir: str | Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def ingest_upload(self, filename: str, content_type: str, data: bytes) -> SpokenCommandInput:
        if not data:
            raise IngestionError("Missing audio data")

        suffix = _suffix_for(filename, content_type)
        if suffix is None:
            raise IngestionError(f"Unsupported audio input: {filename} ({content_type})")
        if not _looks_like_audio(suffix, data):
            raise IngestionError(f"Unsupported or corrupt audio input: {filename}")

        audio_id = f"{uuid4().hex}{suffix}"
        path = self.storage_dir / audio_id
        path.write_bytes(data)
        return SpokenCommandInput(
            source_type="upload",
            audio_id=audio_id,
            content_type=content_type,
            size_bytes=len(data),
            storage_path=path,
        )

    def ingest_recording(self, data: bytes, content_type: str = "audio/webm") -> SpokenCommandInput:
        return self.ingest_upload(filename=f"recording{SUPPORTED_AUDIO_TYPES[content_type]}", content_type=content_type, data=data)


def _suffix_for(filename: str, content_type: str) -> str | None:
    suffix = Path(_safe_filename(filename)).suffix.lower()
    expected = SUPPORTED_AUDIO_TYPES.get(content_type.lower())
    if expected:
        return expected
    if suffix in SUPPORTED_SUFFIXES:
        return suffix
    return None


def _safe_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip(".-")
    return cleaned or "command"


def _looks_like_audio(suffix: str, data: bytes) -> bool:
    validator = MAGIC_HEADERS.get(suffix)
    return validator(data) if validator else True
