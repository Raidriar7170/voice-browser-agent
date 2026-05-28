from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from .models import BrowserTaskRequest, ClarificationRequest, ValidationResult


SAFETY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "checkout": ("checkout", "结账", "下单", "购买", "买下", "order"),
    "payment": ("payment", "付款", "支付", "信用卡", "card", "pay"),
    "deletion": ("delete", "删除", "清空", "移除", "注销"),
    "posting": ("post", "publish", "发布", "发送", "评论", "提交评论"),
    "login": ("login", "log in", "登录", "登陆", "账号", "密码"),
    "github_account_action": (
        "star",
        "fork",
        "watch",
        "pull request",
        "create pr",
        "open pr",
        "issue",
        "comment",
        "commit",
        "edit",
        "merge",
        "clone",
        "private repo",
        "private repository",
        "收藏",
        "加星",
        "派生",
        "评论",
        "提 issue",
        "创建 issue",
        "私有仓库",
    ),
    "private_data_entry": ("身份证", "地址", "手机号", "隐私", "private", "personal"),
    "file_transfer": ("upload", "download", "上传", "下载", "传文件", "文件"),
    "irreversible_submit": ("submit", "提交", "确认提交", "final", "不可撤销"),
}

LONG_HORIZON_KEYWORDS = (
    "所有",
    "全网",
    "一直",
    "自动处理",
    "长期",
    "随便",
    "everything",
    "all websites",
    "best",
    "top",
    "rank",
    "ranking",
    "until you find",
    "keep searching",
    "browse all",
    "recommend",
    "recommendation",
    "推荐",
    "排名",
    "最好",
    "最佳",
)


class NormalizerValidator:
    def validate(self, output: BrowserTaskRequest | ClarificationRequest) -> ValidationResult:
        if isinstance(output, ClarificationRequest):
            return ValidationResult(
                accepted=False,
                reason=f"clarification required: {output.reason}",
                issues=[output.reason],
                requires_confirmation=False,
            )

        issues: list[str] = []
        if not output.task.strip():
            issues.append("missing_task")
        if not output.constraints:
            issues.append("missing_constraints")
        if not output.stop_conditions:
            issues.append("missing_stop_conditions")
        if _contains_long_horizon_goal(output.task):
            issues.append("unsupported_long_horizon_goal")
        if _looks_visual(output.task) and not output.visual_references:
            issues.append("missing_visual_reference")

        safety_flags = set(output.safety_flags) | set(detect_safety_flags(output.task))
        requires_confirmation = output.requires_confirmation or bool(safety_flags)

        if issues:
            return ValidationResult(
                accepted=False,
                reason="request failed deterministic validation",
                issues=issues,
                requires_confirmation=requires_confirmation,
            )
        return ValidationResult(
            accepted=True,
            reason="request accepted by deterministic validator",
            issues=[],
            requires_confirmation=requires_confirmation,
        )


def detect_safety_flags(text: str) -> list[str]:
    lowered = text.lower()
    flags = [
        flag
        for flag, keywords in SAFETY_KEYWORDS.items()
        if any(_keyword_is_active(lowered, keyword.lower()) for keyword in keywords)
    ]
    flags.extend(_detect_url_safety_flags(text))
    return sorted(set(flags), key=flags.index)


def _contains_long_horizon_goal(text: str) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in LONG_HORIZON_KEYWORDS)


def _looks_visual(text: str) -> bool:
    lowered = text.lower()
    visual_terms = ("图标", "icon", "颜色", "色块", "卡片", "右上角", "左边", "chart", "canvas")
    return any(term in lowered for term in visual_terms)


def _keyword_is_active(text: str, keyword: str) -> bool:
    if keyword in {"登录", "登陆", "login", "log in"}:
        negated = (
            f"不要{keyword}",
            f"无需{keyword}",
            f"不用{keyword}",
            f"不需要{keyword}",
            f"do not {keyword}",
            f"without {keyword}",
        )
        if any(marker in text for marker in negated):
            return False
    return keyword in text


def _detect_url_safety_flags(text: str) -> list[str]:
    flags: list[str] = []
    for raw_url in re.findall(r"(?:https?|file|data|javascript):[^\s，。；;]+", text, flags=re.IGNORECASE):
        parsed = urlparse(raw_url)
        if parsed.scheme not in {"http", "https"}:
            flags.append("unsafe_protocol")
            continue
        if parsed.username or parsed.password:
            flags.append("credentialed_url")
        host = (parsed.hostname or "").lower()
        if _is_private_host(host):
            flags.append("private_network_target")
    return flags


def _is_private_host(host: str) -> bool:
    if not host:
        return False
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
