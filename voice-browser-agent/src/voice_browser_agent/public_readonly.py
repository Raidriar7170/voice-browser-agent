from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from .config import RuntimeConfig
from .models import BrowserTaskRequest


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
        targets.append(
            PublicReadonlyTarget(
                allowlist_id=allowlist_id,
                label=label,
                url=url,
                origin=origin,
                keywords=keywords,
            )
        )
    return targets


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
    for target in config.targets:
        if any(keyword and keyword in text for keyword in target.keywords):
            return target
    return None


def request_looks_public(request: BrowserTaskRequest) -> bool:
    text = _command_text(request)
    return any(marker in text for marker in PUBLIC_TARGET_MARKERS)


def has_transcript_url(request: BrowserTaskRequest) -> bool:
    return bool(_extract_urls(_command_text(request)))


def public_readonly_readiness(config: RuntimeConfig) -> dict[str, object]:
    targets = parse_public_readonly_targets(config)
    if not config.public_readonly_enabled:
        status = "disabled"
        detail = "Public-readonly execution is disabled by default."
    elif not targets:
        status = "missing_allowlist"
        detail = "Set VOICE_BROWSER_PUBLIC_READONLY_ALLOWLIST before live public execution."
    else:
        status = "ready"
        detail = "Public-readonly execution is enabled for configured allowlist targets."
    return {
        "status": status,
        "enabled": config.public_readonly_enabled,
        "allowlist_count": len(targets),
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
