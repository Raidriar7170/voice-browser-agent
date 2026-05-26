from __future__ import annotations

from .models import BrowserIntentType, BrowserTaskRequest, ClarificationRequest, VisualReference
from .validator import detect_safety_flags


class RuleBasedNormalizer:
    """Deterministic local normalizer used for tests, fixtures, and offline demos."""

    def normalize(self, transcript_text: str) -> BrowserTaskRequest | ClarificationRequest:
        text = transcript_text.strip()
        lowered = text.lower()
        if not text:
            return ClarificationRequest(
                question="没有识别到有效语音内容，请重新上传或录制一条命令。",
                reason="empty_transcript",
                transcript_text=transcript_text,
            )
        if _is_ambiguous(text):
            return ClarificationRequest(
                question="请说明要打开的网站、页面或可见目标。",
                reason="ambiguous_target",
                transcript_text=transcript_text,
            )

        safety_flags = detect_safety_flags(text)
        if safety_flags:
            return BrowserTaskRequest(
                task=text,
                intent_type=_intent_for(text),
                constraints=["pause before destructive, private, or irreversible action"],
                visual_references=_visual_references_for(text),
                requires_confirmation=True,
                stop_conditions=["payment_or_checkout", "login_required", "irreversible_submit"],
                safety_flags=safety_flags,
            )

        return BrowserTaskRequest(
            task=_task_for(text, lowered),
            intent_type=_intent_for(text),
            constraints=_constraints_for(text),
            visual_references=_visual_references_for(text),
            requires_confirmation=False,
            stop_conditions=["login_required", "payment_or_checkout", "irreversible_submit"],
            safety_flags=[],
        )


class StructuredOutputNormalizer:
    def __init__(self, llm_client=None, fallback: RuleBasedNormalizer | None = None):
        self.llm_client = llm_client
        self.fallback = fallback or RuleBasedNormalizer()

    def normalize(self, transcript_text: str) -> BrowserTaskRequest | ClarificationRequest:
        if self.llm_client is None:
            return self.fallback.normalize(transcript_text)
        payload = self.llm_client.normalize(transcript_text)
        if payload.get("kind") == "clarification_request":
            return ClarificationRequest.model_validate(payload)
        return BrowserTaskRequest.model_validate(payload)


def _is_ambiguous(text: str) -> bool:
    return any(marker in text for marker in ("那个", "那个页面", "这个", "随便")) and not any(
        target in text.lower() for target in ("github", "openai", "browser-use", "页面上")
    )


def _intent_for(text: str) -> BrowserIntentType:
    lowered = text.lower()
    if any(word in lowered for word in ("点击", "click", "图标", "按钮")):
        return BrowserIntentType.CLICK_VISUAL_TARGET
    if any(word in lowered for word in ("填写", "输入", "填入", "form")):
        return BrowserIntentType.FILL_FORM
    if any(word in lowered for word in ("筛选", "选择", "filter", "select")):
        return BrowserIntentType.SELECT_FILTER_OR_OPTION
    if any(word in lowered for word in ("比较", "提取", "读取", "compare", "extract")):
        return BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO
    return BrowserIntentType.SEARCH_OPEN


def _task_for(text: str, lowered: str) -> str:
    if "github" in lowered and ("搜索" in text or "search" in lowered):
        return "Open GitHub and search for browser-use-vision on public pages."
    if "图标" in text or "icon" in lowered:
        return text
    return text


def _constraints_for(text: str) -> list[str]:
    constraints = ["bounded single browser task"]
    if "不要登录" in text or "无需登录" in text:
        constraints.append("do not log in")
    constraints.append("public or controlled pages only")
    return constraints


def _visual_references_for(text: str) -> list[VisualReference]:
    lowered = text.lower()
    references: list[VisualReference] = []
    if "放大镜" in text or "search icon" in lowered or "magnifying" in lowered:
        references.append(VisualReference(kind="icon", text="top-right magnifying glass", source="transcript"))
    elif "图标" in text or "icon" in lowered:
        references.append(VisualReference(kind="icon", text=text, source="transcript"))
    if "色块" in text or "颜色" in text or "swatch" in lowered:
        references.append(VisualReference(kind="color_swatch", text=text, source="transcript"))
    if "卡片" in text or "card" in lowered:
        references.append(VisualReference(kind="card", text=text, source="transcript"))
    return references

