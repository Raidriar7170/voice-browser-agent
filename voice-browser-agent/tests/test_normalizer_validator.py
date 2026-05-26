from voice_browser_agent.models import BrowserIntentType, BrowserTaskRequest, ClarificationRequest
from voice_browser_agent.normalizer import RuleBasedNormalizer
from voice_browser_agent.validator import NormalizerValidator, detect_safety_flags


def test_clear_chinese_command_becomes_supported_browser_task_request():
    output = RuleBasedNormalizer().normalize("打开 GitHub 搜索 browser-use-vision，不要登录")

    assert isinstance(output, BrowserTaskRequest)
    assert output.intent_type is BrowserIntentType.SEARCH_OPEN
    assert output.requires_confirmation is False
    assert "login_required" in output.stop_conditions

    result = NormalizerValidator().validate(output)
    assert result.accepted is True
    assert result.requires_confirmation is False


def test_visual_reference_command_keeps_structured_visual_reference():
    output = RuleBasedNormalizer().normalize("点击右上角的放大镜图标")

    assert isinstance(output, BrowserTaskRequest)
    assert output.intent_type is BrowserIntentType.CLICK_VISUAL_TARGET
    assert output.visual_references[0].kind == "icon"


def test_ambiguous_command_returns_clarification_request_without_execution():
    output = RuleBasedNormalizer().normalize("打开那个页面")

    assert isinstance(output, ClarificationRequest)
    assert output.reason == "ambiguous_target"


def test_safety_sensitive_command_requires_confirmation():
    output = RuleBasedNormalizer().normalize("帮我结账并提交付款")

    assert isinstance(output, BrowserTaskRequest)
    assert output.requires_confirmation is True
    assert {"checkout", "payment", "irreversible_submit"}.issubset(set(output.safety_flags))

    result = NormalizerValidator().validate(output)
    assert result.accepted is True
    assert result.requires_confirmation is True


def test_validator_rejects_long_horizon_or_missing_required_fields():
    request = BrowserTaskRequest(
        task="帮我浏览全网找到所有相关资料并自动处理",
        intent_type=BrowserIntentType.SEARCH_OPEN,
        constraints=[],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=[],
    )

    result = NormalizerValidator().validate(request)

    assert result.accepted is False
    assert "missing_stop_conditions" in result.issues
    assert "unsupported_long_horizon_goal" in result.issues


def test_safety_detection_covers_private_and_irreversible_actions():
    flags = detect_safety_flags("登录账号后上传文件，然后发布这条内容")

    assert {"login", "file_transfer", "posting"}.issubset(set(flags))

