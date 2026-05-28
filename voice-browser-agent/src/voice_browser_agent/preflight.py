from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from .config import RuntimeConfig, load_config


def build_readiness_report(
    project_root: Path | None = None,
    runtime_dir: str | Path | None = None,
    config: RuntimeConfig | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]
    config = config or load_config(runtime_dir)
    checks = {
        "primary_asr": check_primary_asr(config),
        "fallback_asr": check_fallback_asr(config),
        "browser_automation": check_browser_automation(),
        "real_vision_grounding": check_real_vision_grounding(),
        "runtime_privacy": check_runtime_privacy(project_root=project_root, config=config),
    }
    return {
        "project": "Voice-to-Browser Agent",
        "checks": checks,
        "recommended_actions": recommended_actions(checks),
    }


def check_primary_asr(config: RuntimeConfig) -> dict[str, Any]:
    if config.primary_asr_url:
        return {
            "status": "configured",
            "adapter": "primary-asr",
            "detail": "Primary ASR endpoint is configured.",
        }
    return {
        "status": "not_configured",
        "adapter": "primary-asr",
        "detail": "Set VOICE_BROWSER_PRIMARY_ASR_URL or install the local ASR extra.",
    }


def check_fallback_asr(config: RuntimeConfig) -> dict[str, Any]:
    available = importlib.util.find_spec("faster_whisper") is not None
    return {
        "status": "ready" if available else "unavailable",
        "adapter": "faster-whisper-fallback",
        "model": config.fallback_asr_model,
        "detail": (
            "faster-whisper is importable."
            if available
            else "Install with `uv sync --extra asr` for local fallback ASR."
        ),
    }


def check_browser_automation() -> dict[str, Any]:
    available = importlib.util.find_spec("playwright") is not None
    return {
        "status": "ready" if available else "unavailable",
        "adapter": "playwright",
        "detail": (
            "Playwright package is importable."
            if available
            else "Install project dependencies and Playwright browser support."
        ),
    }


def check_real_vision_grounding() -> dict[str, Any]:
    available = importlib.util.find_spec("browser_use_vision") is not None
    return {
        "status": "ready" if available else "unavailable",
        "adapter": "browser_use_vision.som.annotate_screenshot",
        "detail": (
            "browser-use-vision package is importable."
            if available
            else "Install or link browser-use-vision before real visual evidence generation."
        ),
    }


def check_runtime_privacy(project_root: Path, config: RuntimeConfig) -> dict[str, Any]:
    ignored = {
        "runtime": "ignored local runtime outputs",
        "uploads": "private audio uploads live under runtime uploads",
        "traces": "private traces live under runtime traces",
    }
    return {
        "status": "ready",
        "runtime_dir": _safe_relative(config.runtime_dir, project_root),
        "ignored_categories": ignored,
        "detail": "Runtime uploads, recordings, generated packs, and private traces stay local.",
    }


def recommended_actions(checks: dict[str, dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    if (
        checks["primary_asr"]["status"] != "configured"
        and checks["fallback_asr"]["status"] != "ready"
    ):
        actions.append("Configure VOICE_BROWSER_PRIMARY_ASR_URL or run `uv sync --extra asr`.")
    if checks["browser_automation"]["status"] != "ready":
        actions.append("Install Playwright dependencies before live-controlled execution.")
    if checks["real_vision_grounding"]["status"] != "ready":
        actions.append("Install or link browser-use-vision for real visual evidence.")
    if not actions:
        actions.append("Run the Operator Console and use one uploaded or recorded command.")
    return actions


def _safe_relative(path: Path, project_root: Path) -> str:
    path = Path(path)
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.name
