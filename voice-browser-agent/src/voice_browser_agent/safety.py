from __future__ import annotations

from typing import Any

from .models import (
    BrowserStateStop,
    BrowserTaskRequest,
    ConfirmationDecision,
    ConfirmationState,
    ValidationResult,
)


class ConfirmationGate:
    def evaluate(
        self,
        request: BrowserTaskRequest,
        validation: ValidationResult,
    ) -> ConfirmationDecision:
        if not validation.accepted:
            return ConfirmationDecision(
                state=ConfirmationState.BLOCKED,
                reason=f"blocked by validator: {', '.join(validation.issues)}",
            )
        if request.requires_confirmation or validation.requires_confirmation:
            return ConfirmationDecision(
                state=ConfirmationState.PENDING,
                reason="operator confirmation required before browser execution",
            )
        return ConfirmationDecision(
            state=ConfirmationState.CONFIRMED,
            reason="no confirmation required",
        )

    def confirm(self, decision: ConfirmationDecision, decided_by: str) -> ConfirmationDecision:
        if decision.state is not ConfirmationState.PENDING:
            return decision
        return ConfirmationDecision(
            state=ConfirmationState.CONFIRMED,
            reason="confirmed by operator",
            decided_by=decided_by,
        )

    def cancel(self, decision: ConfirmationDecision, decided_by: str) -> ConfirmationDecision:
        if decision.state is not ConfirmationState.PENDING:
            return decision
        return ConfirmationDecision(
            state=ConfirmationState.CANCELLED,
            reason="cancelled by operator",
            decided_by=decided_by,
        )


def detect_browser_state_stop(state: dict[str, Any]) -> BrowserStateStop | None:
    haystack = " ".join(str(state.get(key, "")) for key in ("url", "title", "visible_text")).lower()
    checks = [
        ("file_transfer", ("upload", "download", "上传", "下载")),
        (
            "public_task_captcha_or_verification",
            ("captcha", "verify you are human", "verification", "are you a human", "human verification"),
        ),
        ("public_task_rate_limited", ("rate limit", "rate-limited", "abuse detection", "secondary rate limit")),
        (
            "public_task_private_or_permission_boundary",
            ("private repository", "permission denied", "not found", "access denied"),
        ),
        (
            "public_task_login_boundary",
            ("sign in to github", "you must be logged in", "login to github"),
        ),
        ("login_required", ("login", "log in", "登录", "账号", "密码")),
        ("payment_or_checkout", ("checkout", "payment", "pay", "结账", "付款", "支付")),
        ("deletion", ("delete", "删除", "remove account")),
        ("posting", ("post", "publish", "发布", "发送")),
        ("private_data_entry", ("address", "身份证", "手机号", "private")),
        ("irreversible_submit", ("submit", "提交", "confirm", "确认")),
    ]
    for reason, keywords in checks:
        if any(keyword in haystack for keyword in keywords):
            return BrowserStateStop(reason=reason, detail=f"browser state matched {reason}", evidence=state)
    return None
