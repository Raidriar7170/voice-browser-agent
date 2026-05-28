from __future__ import annotations

import ipaddress
import json
import re
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from .config import RuntimeConfig
from .models import (
    BrowserTaskRequest,
    PublicTaskCompletionResult,
    PublicTaskCompletionState,
    PublicTaskContract,
)


PUBLIC_TARGET_MARKERS = (
    "http://",
    "https://",
    "openai",
    "python",
    "mdn",
    "wikipedia",
    "docs",
    "documentation",
    "public",
    "公开",
    "文档",
    "网站",
)


class PublicReadonlyTarget(BaseModel):
    allowlist_id: str
    label: str
    url: str
    origin: str
    keywords: list[str] = Field(default_factory=list)
    task_contracts: list[PublicTaskContract] = Field(default_factory=list)


class PublicReadonlyRoutingConfig(BaseModel):
    enabled: bool = False
    targets: list[PublicReadonlyTarget] = Field(default_factory=list)
    max_steps: int = 3
    timeout_seconds: int = 15
    private_traces: bool = True
    sanitizer_required: bool = True

    @classmethod
    def from_runtime_config(cls, config: RuntimeConfig) -> "PublicReadonlyRoutingConfig":
        return cls(
            enabled=config.public_readonly_enabled,
            targets=parse_public_readonly_targets(config),
            max_steps=config.public_readonly_max_steps,
            timeout_seconds=config.public_readonly_timeout_seconds,
            private_traces=config.public_readonly_private_traces,
            sanitizer_required=config.public_readonly_sanitizer_required,
        )

    @classmethod
    def from_executor_target(
        cls,
        *,
        target_url: str,
        target_label: str,
        public_origin: str,
        allowlist_id: str,
        max_steps: int,
        timeout_seconds: int,
        sanitizer_required: bool = True,
    ) -> "PublicReadonlyRoutingConfig":
        target = PublicReadonlyTarget(
            allowlist_id=allowlist_id,
            label=target_label,
            url=target_url,
            origin=public_origin,
            keywords=_default_keywords(allowlist_id, target_label, target_url),
        )
        return cls(
            enabled=True,
            targets=[target],
            max_steps=max_steps,
            timeout_seconds=timeout_seconds,
            private_traces=True,
            sanitizer_required=sanitizer_required,
        )


class PublicReadonlyPolicyDecision(BaseModel):
    allowed: bool
    reason: str
    detail: str | None = None


class PublicReadonlyPolicy:
    def __init__(self, config: PublicReadonlyRoutingConfig):
        self.config = config

    @property
    def max_steps(self) -> int:
        return self.config.max_steps

    def check_url(self, url: str | None) -> PublicReadonlyPolicyDecision:
        if not url:
            return PublicReadonlyPolicyDecision(allowed=False, reason="missing_public_target")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return PublicReadonlyPolicyDecision(allowed=False, reason="unsafe_protocol")
        if parsed.username or parsed.password:
            return PublicReadonlyPolicyDecision(allowed=False, reason="credentialed_url")
        host = (parsed.hostname or "").lower()
        if not host:
            return PublicReadonlyPolicyDecision(allowed=False, reason="missing_public_host")
        if _is_private_host(host):
            return PublicReadonlyPolicyDecision(allowed=False, reason="private_network_target")
        if not any(_url_matches_target(url, target) for target in self.config.targets):
            return PublicReadonlyPolicyDecision(allowed=False, reason="target_not_allowlisted")
        return PublicReadonlyPolicyDecision(allowed=True, reason="allowlisted_public_target")

    def check_action(self, action_type: str, description: str = "") -> PublicReadonlyPolicyDecision:
        action = action_type.lower()
        haystack = f"{action} {description}".lower()
        mutation_markers = (
            "submit",
            "login",
            "sign in",
            "checkout",
            "payment",
            "purchase",
            "delete",
            "post",
            "publish",
            "upload",
            "download",
            "password",
            "credential",
            "private data",
            "提交",
            "登录",
            "上传",
            "下载",
            "付款",
            "发布",
        )
        if any(marker in haystack for marker in mutation_markers):
            return PublicReadonlyPolicyDecision(allowed=False, reason="mutation_action_blocked")
        allowed_actions = {"navigate", "search", "filter", "expand", "extract", "inspect", "observe", "read"}
        if action == "click" and any(marker in haystack for marker in ("expand", "navigation", "read-only")):
            return PublicReadonlyPolicyDecision(allowed=True, reason="readonly_action_allowed")
        if action not in allowed_actions:
            return PublicReadonlyPolicyDecision(allowed=False, reason="action_not_readonly")
        return PublicReadonlyPolicyDecision(allowed=True, reason="readonly_action_allowed")

    def check_browser_state(self, state: dict[str, object]) -> PublicReadonlyPolicyDecision:
        url = str(state.get("url") or "")
        if url:
            url_decision = self.check_url(url)
            if not url_decision.allowed:
                return url_decision
        haystack = " ".join(
            str(state.get(key, ""))
            for key in ("url", "title", "visible_text", "page_title")
        ).lower()
        checks = [
            ("file_transfer", ("upload", "download", "上传", "下载", "file")),
            ("login_required", ("login", "log in", "sign in", "登录", "账号", "密码")),
            ("payment_or_checkout", ("checkout", "payment", "pay", "结账", "付款", "支付")),
            ("deletion", ("delete", "删除", "remove account")),
            ("posting", ("post", "publish", "发布", "发送")),
            ("private_data_entry", ("address", "身份证", "手机号", "private")),
            ("irreversible_submit", ("submit", "提交", "confirm", "确认")),
        ]
        for reason, keywords in checks:
            if any(keyword in haystack for keyword in keywords):
                return PublicReadonlyPolicyDecision(allowed=False, reason=reason)
        return PublicReadonlyPolicyDecision(allowed=True, reason="browser_state_safe")


class PublicTaskCompletionVerifier:
    def __init__(self, contract: PublicTaskContract):
        self.contract = contract

    def verify(
        self,
        *,
        requested_slots: dict[str, Any],
        actions: list[dict[str, Any]],
    ) -> PublicTaskCompletionResult:
        observed = self._observed_proof(requested_slots, actions)
        unmet = [
            proof
            for proof in self.contract.completion_criteria.required_proof
            if proof not in observed
        ]
        if not unmet:
            return PublicTaskCompletionResult(
                completion_state=PublicTaskCompletionState.COMPLETED,
                observed_proof=observed,
                unmet_criteria=[],
            )
        return PublicTaskCompletionResult(
            completion_state=PublicTaskCompletionState.PARTIAL if actions else PublicTaskCompletionState.FAILED,
            observed_proof=observed,
            unmet_criteria=unmet,
            stop_reason="missing_public_task_completion" if actions else None,
            failure_reason=None if actions else "public_readonly_missing_evidence",
        )

    def classify_variance(self, reason: str) -> PublicTaskCompletionResult:
        mapping = {
            "timeout": (PublicTaskCompletionState.FAILED, None, "public_task_timeout"),
            "missing_selector": (PublicTaskCompletionState.PARTIAL, "public_task_missing_selector", None),
            "redirect_off_allowlist": (PublicTaskCompletionState.STOPPED, "target_not_allowlisted", None),
            "captcha": (PublicTaskCompletionState.STOPPED, "captcha_boundary", None),
            "login_required": (PublicTaskCompletionState.STOPPED, "login_required", None),
            "network_error": (PublicTaskCompletionState.FAILED, None, "public_task_network_error"),
            "step_budget_exhausted": (
                PublicTaskCompletionState.PARTIAL,
                "public_readonly_step_budget_reached",
                None,
            ),
        }
        state, stop_reason, failure_reason = mapping.get(
            reason,
            (PublicTaskCompletionState.FAILED, None, f"public_task_{reason}"),
        )
        return PublicTaskCompletionResult(
            completion_state=state,
            unmet_criteria=list(self.contract.completion_criteria.required_proof),
            stop_reason=stop_reason,
            failure_reason=failure_reason,
        )

    def classify_blocked(self, reason: str) -> PublicTaskCompletionResult:
        return PublicTaskCompletionResult(
            completion_state=PublicTaskCompletionState.BLOCKED,
            unmet_criteria=list(self.contract.completion_criteria.required_proof),
            stop_reason=reason,
        )

    def _observed_proof(
        self,
        requested_slots: dict[str, Any],
        actions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        observed: dict[str, Any] = {}
        combined_parts: list[str] = []
        for action in actions:
            state = action.get("browser_state", {})
            state = state if isinstance(state, dict) else {}
            combined_parts.extend(
                [
                    str(action.get("type", "")),
                    str(action.get("description", "")),
                    str(state.get("page_title", "")),
                    str(state.get("visible_text", "")),
                    str(state.get("url", "")),
                ]
            )
        combined = " ".join(combined_parts).lower()
        query = str(requested_slots.get("search_query") or "").strip()
        if query and query.lower() in combined and any(action.get("type") == "search" for action in actions):
            observed["searched_query"] = query
        final_state = _last_browser_state(actions)
        title = str(final_state.get("page_title") or final_state.get("title") or "")
        expected_title = self.contract.completion_criteria.title_contains
        if title and (not expected_title or expected_title.lower() in title.lower()):
            observed["final_title"] = title
        url = str(final_state.get("url") or "")
        parsed = urlparse(url)
        path = parsed.path if parsed.scheme else ""
        expected_path = self.contract.completion_criteria.url_path_contains
        if path and (not expected_path or expected_path in path):
            observed["url_path"] = path
        markers = []
        for marker in self.contract.completion_criteria.visible_markers:
            try:
                markers.append(
                    marker.format(**{key: str(value) for key, value in requested_slots.items()})
                )
            except KeyError:
                continue
        if markers and any(marker.lower() in combined for marker in markers):
            visible_marker = next(
                marker for marker in markers if marker.lower() in combined
            )
            observed["result_heading"] = visible_marker
            observed["visible_marker"] = visible_marker
        return observed


def parse_public_readonly_targets(config: RuntimeConfig) -> list[PublicReadonlyTarget]:
    entries = [
        entry.strip()
        for chunk in config.public_readonly_allowlist.splitlines()
        for entry in chunk.split(";")
        if entry.strip()
    ]
    targets: list[PublicReadonlyTarget] = []
    for entry in entries:
        parts = [part.strip() for part in entry.split("|")]
        if len(parts) < 3:
            continue
        allowlist_id, label, url = parts[:3]
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        origin = f"{parsed.scheme}://{parsed.netloc.lower()}"
        keywords = (
            [item.strip().lower() for item in parts[3].split(",") if item.strip()]
            if len(parts) > 3
            else _default_keywords(allowlist_id, label, url)
        )
        task_contracts = _parse_task_contracts(
            raw_contracts=parts[4:] if len(parts) > 4 else [],
            allowlist_id=allowlist_id,
        )
        targets.append(
            PublicReadonlyTarget(
                allowlist_id=allowlist_id,
                label=label,
                url=url,
                origin=origin,
                keywords=keywords,
                task_contracts=task_contracts,
            )
        )
    return targets


def match_public_readonly_task(
    request: BrowserTaskRequest,
    config: PublicReadonlyRoutingConfig,
) -> tuple[PublicReadonlyTarget, PublicTaskContract, dict[str, Any]] | None:
    target = match_public_readonly_target(request, config)
    if target is None:
        return None
    slots = normalized_public_task_slots(request)
    for contract in target.task_contracts:
        if _contract_matches_request(contract, request, slots):
            return target, contract, slots
    return None


def match_public_readonly_target(
    request: BrowserTaskRequest,
    config: PublicReadonlyRoutingConfig,
) -> PublicReadonlyTarget | None:
    text = _command_text(request)
    explicit_urls = _extract_urls(text)
    if explicit_urls:
        matched_target: PublicReadonlyTarget | None = None
        for url in explicit_urls:
            matches = [target for target in config.targets if _url_matches_target(url, target)]
            if not matches:
                return None
            if matched_target is None:
                matched_target = matches[0]
            elif matches[0].allowlist_id != matched_target.allowlist_id:
                return None
        return matched_target
    scored_targets = [
        (sum(1 for keyword in target.keywords if keyword and keyword in text), target)
        for target in config.targets
    ]
    scored_targets = [(score, target) for score, target in scored_targets if score > 0]
    if scored_targets:
        return max(scored_targets, key=lambda item: item[0])[1]
    return None


def request_looks_public(request: BrowserTaskRequest) -> bool:
    text = _command_text(request)
    return any(marker in text for marker in PUBLIC_TARGET_MARKERS)


def has_transcript_url(request: BrowserTaskRequest) -> bool:
    return bool(_extract_urls(_command_text(request)))


def normalized_public_task_slots(request: BrowserTaskRequest) -> dict[str, Any]:
    slots = dict(request.public_task_slots)
    text = _command_text(request)
    mentions_docs = "doc" in text or "文档" in text
    if "target_site_hint" not in slots:
        if "python" in text and mentions_docs:
            slots["target_site_hint"] = "python docs"
        elif "openai" in text and mentions_docs:
            slots["target_site_hint"] = "openai docs"
        elif "mdn" in text:
            slots["target_site_hint"] = "mdn"
        elif "wikipedia" in text:
            slots["target_site_hint"] = "wikipedia"
    if "search_query" not in slots:
        query = _extract_search_query(text)
        if query:
            slots["search_query"] = query
    if "read_only_intent" not in slots and request.safety_flags == []:
        slots["read_only_intent"] = True
    return slots


def public_readonly_readiness(config: RuntimeConfig) -> dict[str, object]:
    targets = parse_public_readonly_targets(config)
    task_contract_count = sum(len(target.task_contracts) for target in targets)
    if not config.public_readonly_enabled:
        status = "disabled"
        detail = "Public-readonly execution is disabled by default."
    elif not targets:
        status = "missing_allowlist"
        detail = "Set VOICE_BROWSER_PUBLIC_READONLY_ALLOWLIST before live public execution."
    elif task_contract_count == 0:
        status = "missing_task_contracts"
        detail = "Configured public-readonly targets need explicit public task contracts."
    else:
        status = "ready"
        detail = "Public-readonly execution is enabled for configured allowlist targets."
    return {
        "status": status,
        "enabled": config.public_readonly_enabled,
        "allowlist_count": len(targets),
        "task_contract_count": task_contract_count,
        "allowlist": [{"id": target.allowlist_id, "label": target.label} for target in targets],
        "max_steps": config.public_readonly_max_steps,
        "timeout_seconds": config.public_readonly_timeout_seconds,
        "private_traces": config.public_readonly_private_traces,
        "browser_isolation": {
            "status": "ready",
            "detail": "Uses a fresh ephemeral Playwright context per public-readonly run.",
        },
        "sanitizer": {
            "status": "required" if config.public_readonly_sanitizer_required else "optional",
            "detail": "Public-readonly traces remain local/private until sanitizer approval.",
        },
        "detail": detail,
    }


def _request_text(request: BrowserTaskRequest) -> str:
    parts = [request.task, request.intent_type.value]
    parts.extend(request.constraints)
    parts.extend(request.safety_flags)
    parts.extend(ref.text for ref in request.visual_references)
    return " ".join(parts).lower()


def _command_text(request: BrowserTaskRequest) -> str:
    parts = [request.task]
    parts.extend(ref.text for ref in request.visual_references)
    return " ".join(parts).lower()


def _extract_urls(text: str) -> list[str]:
    return re.findall(r"(?:https?|file|data|javascript):[^\s，。；;]+", text)


def _parse_task_contracts(
    *,
    raw_contracts: list[str],
    allowlist_id: str,
) -> list[PublicTaskContract]:
    contracts: list[PublicTaskContract] = []
    for raw in raw_contracts:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payload.setdefault("allowlist_id", allowlist_id)
            contracts.append(PublicTaskContract.model_validate(payload))
        elif isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    item.setdefault("allowlist_id", allowlist_id)
                    contracts.append(PublicTaskContract.model_validate(item))
    return contracts


def _contract_matches_request(
    contract: PublicTaskContract,
    request: BrowserTaskRequest,
    slots: dict[str, Any],
) -> bool:
    if any(slot not in slots for slot in contract.slots):
        return False
    if contract.task_kind == "documentation_search":
        return bool(slots.get("search_query"))
    if contract.task_kind in {"direct_reference_read", "visible_extraction"}:
        return bool(
            slots.get("read_target")
            or slots.get("extraction_target")
            or all(slot in slots for slot in contract.slots)
        )
    return request.intent_type.value in contract.task_kind or bool(slots)


def _extract_search_query(text: str) -> str | None:
    patterns = (
        r"(?:search|look up|find)\s+(?:[^.\n]*?\s+)?(?:for\s+)?([a-z0-9_.\- ]+?)(?:,|\.|\n|$)",
        r"(?:搜索|查找|查询)\s*([^，。；\n|]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            query = re.sub(r"\s+(?:do not log in|without login)$", "", query, flags=re.IGNORECASE)
            words = query.split()
            if len(words) > 1 and words[0] in {"python", "docs", "documentation"}:
                query = words[-1]
            return query[:80] if query else None
    return None


def _last_browser_state(actions: list[dict[str, Any]]) -> dict[str, Any]:
    for action in reversed(actions):
        state = action.get("browser_state")
        if isinstance(state, dict):
            return state
    return {}


def _default_keywords(allowlist_id: str, label: str, url: str) -> list[str]:
    parsed = urlparse(url)
    host_parts = [part for part in (parsed.hostname or "").split(".") if part and part not in {"www", "com", "org"}]
    raw = re.split(r"[\s_\-/]+", f"{allowlist_id} {label}".lower())
    return sorted(set([item for item in raw + host_parts if item and len(item) > 2]))


def _url_matches_target(url: str, target: PublicReadonlyTarget) -> bool:
    parsed = urlparse(url)
    target_parsed = urlparse(target.url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if (parsed.hostname or "").lower() != (target_parsed.hostname or "").lower():
        return False
    target_path = target_parsed.path.rstrip("/")
    candidate_path = parsed.path.rstrip("/")
    return not target_path or candidate_path.startswith(target_path)


def _is_private_host(host: str) -> bool:
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
