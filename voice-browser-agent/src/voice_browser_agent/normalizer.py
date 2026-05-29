from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from .models import (
    BrowserIntentType,
    BrowserTaskRequest,
    ClarificationRequest,
    NormalizerProvenance,
    VisualReference,
)
from .validator import detect_safety_flags


class NormalizerProviderError(RuntimeError):
    pass


class LLMNormalizerClient(Protocol):
    provider_name: str

    def normalize(self, transcript_text: str) -> dict[str, Any] | str:
        ...


@dataclass(frozen=True)
class NormalizationResult:
    output: BrowserTaskRequest | ClarificationRequest
    provenance: NormalizerProvenance


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
        if _is_unsupported_public_scope(text):
            return ClarificationRequest(
                question="请把公开网页任务限定为一个只读搜索、读取或提取目标。",
                reason="unsupported_public_task_scope",
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
                public_task_slots=_public_task_slots_for(text),
            )

        public_slots = _public_task_slots_for(text)
        return BrowserTaskRequest(
            task=_task_for(text, lowered),
            intent_type=_intent_for(text),
            constraints=_constraints_for(text),
            visual_references=_visual_references_for(text),
            requires_confirmation=False,
            stop_conditions=_stop_conditions_for(public_slots),
            safety_flags=[],
            public_task_slots=public_slots,
        )


class MockLLMNormalizerClient:
    provider_name = "mock-llm"

    def __init__(self, delegate: RuleBasedNormalizer | None = None):
        self.delegate = delegate or RuleBasedNormalizer()

    def normalize(self, transcript_text: str) -> dict[str, Any]:
        return self.delegate.normalize(transcript_text).model_dump(mode="json")


class GenericHTTPNormalizerClient:
    provider_name = "generic-http"

    def __init__(
        self,
        endpoint_url: str,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 15.0,
    ):
        if not endpoint_url:
            raise ValueError("endpoint_url is required")
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def normalize(self, transcript_text: str) -> dict[str, Any] | str:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload: dict[str, Any] = {
            "transcript_text": transcript_text,
            "schema": "voice-browser-agent.normalized-output.v1",
        }
        if self.model:
            payload["model"] = self.model
        try:
            response = httpx.post(
                self.endpoint_url,
                json=payload,
                headers=headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise NormalizerProviderError(f"normalizer provider request failed: {exc}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise NormalizerProviderError("normalizer provider returned non-JSON response") from exc


class UnavailableLLMNormalizerClient:
    def __init__(self, provider_name: str, detail: str):
        self.provider_name = provider_name
        self.detail = detail

    def normalize(self, transcript_text: str) -> dict[str, Any]:
        raise NormalizerProviderError(self.detail)


class StructuredOutputNormalizer:
    def __init__(
        self,
        llm_client: LLMNormalizerClient | None = None,
        fallback: RuleBasedNormalizer | None = None,
        provider_mode: str = "rule",
        fallback_policy: str = "rule",
        prompt_schema_version: str = "structured-normalizer.v1",
    ):
        if fallback_policy not in {"rule", "clarify"}:
            raise ValueError("fallback policy must be 'rule' or 'clarify'")
        self.llm_client = llm_client
        self.fallback = fallback or RuleBasedNormalizer()
        self.provider_mode = provider_mode
        self.fallback_policy = fallback_policy
        self.prompt_schema_version = prompt_schema_version
        self.last_provenance: NormalizerProvenance | None = None

    def normalize(self, transcript_text: str) -> BrowserTaskRequest | ClarificationRequest:
        result = self.normalize_with_provenance(transcript_text)
        self.last_provenance = result.provenance
        return result.output

    def normalize_with_provenance(self, transcript_text: str) -> NormalizationResult:
        if self.llm_client is None:
            output = self.fallback.normalize(transcript_text)
            return self._result(
                output,
                provider_name="rule-based",
                output_source="rule",
                schema_status="not_applicable",
            )
        provider_name = getattr(self.llm_client, "provider_name", "llm")
        try:
            payload = self.llm_client.normalize(transcript_text)
            output = self._parse_payload(payload)
            return self._result(
                output,
                provider_name=provider_name,
                output_source="llm",
                schema_status="passed",
            )
        except Exception as exc:
            return self._fallback_result(
                transcript_text,
                provider_name=provider_name,
                reason=_fallback_reason(exc),
            )

    def _parse_payload(self, payload: dict[str, Any] | str) -> BrowserTaskRequest | ClarificationRequest:
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError(f"malformed provider JSON: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ValueError("malformed provider payload: expected object")
        kind = payload.get("kind")
        if kind == "clarification_request":
            return ClarificationRequest.model_validate(payload)
        if kind == "browser_task_request":
            return BrowserTaskRequest.model_validate(payload)
        raise ValueError(f"malformed provider payload: unknown kind {kind!r}")

    def _fallback_result(
        self,
        transcript_text: str,
        provider_name: str,
        reason: str,
    ) -> NormalizationResult:
        if self.fallback_policy == "clarify":
            output = ClarificationRequest(
                question="LLM 意图解析暂不可用，请改用更明确的一条浏览器任务命令。",
                reason="llm_normalizer_unavailable",
                transcript_text=transcript_text,
            )
            return self._result(
                output,
                provider_name=provider_name,
                output_source="clarification",
                schema_status="failed",
                fallback_reason=reason,
            )
        output = self.fallback.normalize(transcript_text)
        return self._result(
            output,
            provider_name=provider_name,
            output_source="fallback_rule",
            schema_status="failed",
            fallback_reason=reason,
        )

    def _result(
        self,
        output: BrowserTaskRequest | ClarificationRequest,
        provider_name: str,
        output_source: str,
        schema_status: str,
        fallback_reason: str | None = None,
    ) -> NormalizationResult:
        provenance = NormalizerProvenance(
            provider_mode=self.provider_mode,
            provider_name=provider_name,
            output_source=output_source,
            prompt_schema_version=self.prompt_schema_version,
            output_kind=output.kind,
            schema_status=schema_status,  # type: ignore[arg-type]
            fallback_reason=fallback_reason,
        )
        self.last_provenance = provenance
        return NormalizationResult(output=output, provenance=provenance)


def _fallback_reason(exc: Exception) -> str:
    message = str(exc) or exc.__class__.__name__
    if isinstance(exc, NormalizerProviderError):
        return f"provider unavailable: {message}"
    return f"malformed provider output: {message}"


def normalizer_from_config(config: Any) -> StructuredOutputNormalizer:
    provider_mode = str(getattr(config, "normalizer_provider", "rule") or "rule")
    fallback_policy = str(getattr(config, "normalizer_fallback_policy", "rule") or "rule")
    prompt_schema_version = str(
        getattr(config, "normalizer_prompt_schema_version", "structured-normalizer.v1")
        or "structured-normalizer.v1"
    )
    if provider_mode == "rule":
        client = None
    elif provider_mode == "mock_llm":
        client = MockLLMNormalizerClient()
    elif provider_mode in {"openai_compatible", "generic_http"}:
        endpoint_url = getattr(config, "normalizer_endpoint_url", None)
        if endpoint_url:
            client = GenericHTTPNormalizerClient(
                endpoint_url=str(endpoint_url),
                api_key=getattr(config, "normalizer_api_key", None),
                model=getattr(config, "normalizer_model", None),
                timeout_seconds=float(getattr(config, "normalizer_timeout_seconds", 15.0)),
            )
            client.provider_name = provider_mode
        else:
            client = UnavailableLLMNormalizerClient(
                provider_name=provider_mode,
                detail=f"{provider_mode} normalizer endpoint is not configured",
            )
    else:
        client = UnavailableLLMNormalizerClient(
            provider_name=provider_mode,
            detail=f"unsupported normalizer provider: {provider_mode}",
        )
    return StructuredOutputNormalizer(
        llm_client=client,
        provider_mode=provider_mode,
        fallback_policy=fallback_policy,
        prompt_schema_version=prompt_schema_version,
    )


def _is_ambiguous(text: str) -> bool:
    return any(marker in text for marker in ("那个", "那个页面", "这个", "随便")) and not any(
        target in text.lower() for target in ("github", "openai", "browser-use", "页面上")
    )


def _is_unsupported_public_scope(text: str) -> bool:
    lowered = text.lower()
    if not any(
        marker in lowered
        for marker in (
            "github",
            "public",
            "docs",
            "documentation",
            "pypi",
            "npm",
            "package",
            "release",
            "releases",
            "网站",
            "公开",
            "文档",
        )
    ):
        return False
    broad_markers = (
        "all websites",
        "everything",
        "until you find",
        "keep searching",
        "browse all",
        "best",
        "top",
        "rank",
        "全网",
        "所有",
        "一直",
        "最好",
        "最佳",
        "排名",
        "推荐",
    )
    return any(marker in lowered for marker in broad_markers)


def _intent_for(text: str) -> BrowserIntentType:
    lowered = text.lower()
    if any(word in lowered for word in ("点击", "click", "图标", "按钮")):
        return BrowserIntentType.CLICK_VISUAL_TARGET
    if any(word in lowered for word in ("填写", "输入", "填入", "form")):
        return BrowserIntentType.FILL_FORM
    if any(word in lowered for word in ("筛选", "选择", "filter", "select")):
        return BrowserIntentType.SELECT_FILTER_OR_OPTION
    if any(word in lowered for word in ("比较", "提取", "读取", "read", "compare", "extract")):
        return BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO
    return BrowserIntentType.SEARCH_OPEN


def _task_for(text: str, lowered: str) -> str:
    if "图标" in text or "icon" in lowered:
        return text
    return text


def _constraints_for(text: str) -> list[str]:
    constraints = ["bounded single browser task"]
    if _public_task_slots_for(text):
        constraints.append("public_readonly")
    if "不要登录" in text or "无需登录" in text:
        constraints.append("do not log in")
    constraints.append("public or controlled pages only")
    return constraints


def _stop_conditions_for(public_slots: dict[str, object]) -> list[str]:
    conditions = ["login_required", "payment_or_checkout", "irreversible_submit"]
    if public_slots:
        conditions.append("stop_if_login_required")
    return conditions


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


def _public_task_slots_for(text: str) -> dict[str, object]:
    lowered = text.lower()
    slots: dict[str, object] = {}
    mentions_docs = "doc" in lowered or "文档" in text
    if "python" in lowered and mentions_docs:
        slots["target_site_hint"] = "python docs"
    elif "openai" in lowered and mentions_docs:
        slots["target_site_hint"] = "openai docs"
    elif "mdn" in lowered:
        slots["target_site_hint"] = "mdn"
    elif "wikipedia" in lowered:
        slots["target_site_hint"] = "wikipedia"
    elif "github" in lowered:
        slots["target_site_hint"] = "github"
    elif "pypi" in lowered:
        slots["target_site_hint"] = "pypi"
    elif "npm" in lowered:
        slots["target_site_hint"] = "npm"
    package_name = _extract_package_name(text)
    if package_name:
        ecosystem = "pypi" if "pypi" in lowered else "npm" if "npm" in lowered else "package"
        slots["target_site_hint"] = ecosystem
        slots["task_category"] = "package_metadata"
        slots["package_ecosystem"] = ecosystem
        slots["package_name"] = package_name
    search_query = _extract_search_query(text)
    if search_query:
        slots["search_query"] = search_query
        if "github" in lowered:
            slots["task_kind_hint"] = "github-repo-search"
    repo_slug = _extract_github_repo_slug(text)
    if repo_slug:
        owner, repo = repo_slug.split("/", 1)
        slots["target_site_hint"] = "github"
        slots["task_kind_hint"] = "github-public-repo-read"
        slots["repo_slug"] = repo_slug
        slots["owner"] = owner
        slots["repo"] = repo
    release_target = _extract_release_target(text)
    if release_target:
        owner, repo = release_target.split("/", 1)
        slots["target_site_hint"] = "github"
        slots["task_category"] = "release_notes"
        slots["task_kind_hint"] = "release_notes_read"
        slots["release_target"] = release_target
        slots["repo_slug"] = release_target
        slots["owner"] = owner
        slots["repo"] = repo
    read_target = _extract_read_target(text)
    if repo_slug and not read_target:
        read_target = "README" if "readme" in lowered else "repository page"
    if read_target:
        slots["read_target"] = read_target
        slots["extraction_target"] = read_target
    if slots:
        slots["read_only_intent"] = True
    return slots


def _extract_search_query(text: str) -> str | None:
    lowered = text.lower()
    markers = ("search", "look up", "find", "搜索", "查找", "查询")
    if not any(marker in lowered for marker in markers):
        return None
    patterns = (
        r"(?:search|look up|find)\s+(?:(?:python|openai|mdn|wikipedia)\s+)?(?:docs?|documentation)?\s*for\s+([^,\n.]+)",
        r"(?:search|look up|find)\s+(?:[^,\n]*?\s+)?(?:for\s+)?([a-z0-9_.\- ]+?)(?:,|\.|\n|$)",
        r"(?:搜索|查找|查询)\s*([^，。；\n|]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            query = re.sub(
                r"\s+(?:do not log in|without login)$",
                "",
                query,
                flags=re.IGNORECASE,
            )
            words = query.split()
            if len(words) > 1 and words[0].lower() in {"python", "docs", "documentation"}:
                query = words[-1]
            query = _clean_github_search_query(query)
            return query[:80] if query else None
    return None


def _clean_github_search_query(query: str) -> str:
    return re.sub(
        r"^(?:github\s+)?(?:repositories|repository|repos|repo)\s+for\s+",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()


def _extract_read_target(text: str) -> str | None:
    lowered = text.lower()
    if "github" in lowered and "readme" in lowered:
        return "README"
    if not any(marker in lowered for marker in ("read", "extract", "读取", "提取")):
        return None
    patterns = (
        r"(?:read|extract)\s+(?:the\s+)?(.+?)(?:\s+on\s+|\s+from\s+|,|\.|$)",
        r"(?:读取|提取)\s*([^，。；\n]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            target = match.group(1).strip()
            return target[:120] if target else None
    return None


def _extract_package_name(text: str) -> str | None:
    lowered = text.lower()
    if "package" not in lowered and "pypi" not in lowered and "npm" not in lowered:
        return None
    patterns = (
        r"(?:pypi|npm)\s+package\s+metadata\s+for\s+([A-Za-z0-9_.@/\-]+)",
        r"(?:package\s+metadata\s+for|metadata\s+for)\s+([A-Za-z0-9_.@/\-]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip().strip(",.，。")[:80]
    return None


def _extract_release_target(text: str) -> str | None:
    lowered = text.lower()
    if "release" not in lowered and "releases" not in lowered:
        return None
    slug = _extract_github_repo_slug(text)
    return slug


def _extract_github_repo_slug(text: str) -> str | None:
    lowered = text.lower()
    if "github" not in lowered and "github.com/" not in lowered:
        return None
    url_match = re.search(
        r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
        text,
        flags=re.IGNORECASE,
    )
    if url_match:
        return f"{url_match.group(1)}/{url_match.group(2).removesuffix('.git')}"
    slug_match = re.search(
        r"\b([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)\b",
        text,
        flags=re.IGNORECASE,
    )
    if not slug_match:
        return None
    owner, repo = slug_match.group(1), slug_match.group(2).removesuffix(".git")
    if owner.lower() in {"http:", "https:"}:
        return None
    return f"{owner}/{repo}"
