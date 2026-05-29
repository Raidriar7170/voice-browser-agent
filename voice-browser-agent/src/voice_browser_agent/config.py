from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VOICE_BROWSER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    runtime_dir: Path = Field(default=Path("runtime"))
    remote_vision_backend_url: str | None = None
    primary_asr_url: str | None = None
    fallback_asr_model: str = "base"
    normalizer_provider: Literal["rule", "mock_llm", "openai_compatible", "generic_http"] = "rule"
    normalizer_fallback_policy: Literal["rule", "clarify"] = "rule"
    normalizer_prompt_schema_version: str = "structured-normalizer.v1"
    normalizer_endpoint_url: str | None = None
    normalizer_api_key: str | None = None
    normalizer_model: str | None = None
    normalizer_timeout_seconds: float = Field(default=15.0, ge=1.0, le=120.0)
    enable_status_voice_feedback: bool = False
    public_trace_exports: bool = True
    demo_dry_run: bool = True
    public_readonly_enabled: bool = False
    public_readonly_allowlist: str = ""
    public_readonly_max_steps: int = Field(default=3, ge=1, le=5)
    public_readonly_timeout_seconds: int = Field(default=15, ge=1, le=60)
    public_readonly_private_traces: bool = True
    public_readonly_sanitizer_required: bool = True
    public_readonly_headed_debug: bool = False

    @property
    def uploads_dir(self) -> Path:
        return self.runtime_dir / "uploads" / "private"

    @property
    def traces_dir(self) -> Path:
        return self.runtime_dir / "traces"

    @property
    def public_readonly_artifacts_dir(self) -> Path:
        return self.runtime_dir / "artifacts" / "public-readonly"


def load_config(runtime_dir: str | Path | None = None) -> RuntimeConfig:
    config = RuntimeConfig()
    if runtime_dir is not None:
        config.runtime_dir = Path(runtime_dir)
    config.uploads_dir.mkdir(parents=True, exist_ok=True)
    config.traces_dir.mkdir(parents=True, exist_ok=True)
    config.public_readonly_artifacts_dir.mkdir(parents=True, exist_ok=True)
    return config
