from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .models import ExecutionTrace


PRIVATE_KEYS = {
    "raw_audio_path",
    "storage_path",
    "credential",
    "credentials",
    "secret",
    "token",
    "password",
    "remote_host",
    "private_url",
    "url",
    "remote_vision_backend_url",
    "controlled_target_url",
    "browser_profile",
    "browser_profile_path",
    "profile_path",
    "cookie",
    "cookies",
    "public_target_url",
    "public_url",
    "raw_page_text",
    "raw_page_html",
    "visible_text",
    "raw_screenshot",
    "local_file_uri",
    "third_party_private_markers",
}


class TraceWriter:
    def __init__(self, trace_dir: str | Path):
        self.trace_dir = Path(trace_dir)
        self.trace_dir.mkdir(parents=True, exist_ok=True)

    def write(self, trace: ExecutionTrace) -> Path:
        trace.touch()
        path = self.trace_dir / f"{trace.execution_id}.json"
        path.write_text(
            json.dumps(trace.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def read(self, execution_id: str) -> ExecutionTrace:
        path = self.trace_dir / f"{execution_id}.json"
        return ExecutionTrace.model_validate_json(path.read_text(encoding="utf-8"))

    def export_sanitized(self, trace: ExecutionTrace) -> dict[str, Any]:
        return sanitize_trace_dict(trace.model_dump(mode="json"))

    def write_sanitized(self, trace: ExecutionTrace, export_dir: str | Path | None = None) -> Path:
        target_dir = Path(export_dir) if export_dir else self.trace_dir / "sanitized"
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{trace.execution_id}.json"
        path.write_text(
            json.dumps(self.export_sanitized(trace), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


def sanitize_trace_dict(value: Any) -> Any:
    value = deepcopy(value)
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            lowered = key.lower()
            if lowered in PRIVATE_KEYS or any(private in lowered for private in PRIVATE_KEYS):
                continue
            sanitized[key] = sanitize_trace_dict(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_trace_dict(item) for item in value]
    return value
