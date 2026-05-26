from __future__ import annotations


class StatusVoiceFeedback:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def render_status(self, status: str, reason: str | None = None) -> dict[str, str | bool]:
        text = reason or status
        return {"enabled": self.enabled, "text": text}

