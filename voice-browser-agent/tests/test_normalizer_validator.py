import pytest

from voice_browser_agent.models import BrowserIntentType, BrowserTaskRequest, ClarificationRequest
from voice_browser_agent.normalizer import (
    MockLLMNormalizerClient,
    NormalizerProviderError,
    RuleBasedNormalizer,
    StructuredOutputNormalizer,
)
from voice_browser_agent.validator import NormalizerValidator, detect_safety_flags


def test_clear_chinese_command_becomes_supported_browser_task_request():
    output = RuleBasedNormalizer().normalize("打开 GitHub 搜索 browser-use-vision，不要登录")

    assert isinstance(output, BrowserTaskRequest)
    assert output.intent_type is BrowserIntentType.SEARCH_OPEN
    assert output.requires_confirmation is False
    assert "login_required" in output.stop_conditions
    assert output.task == "打开 GitHub 搜索 browser-use-vision，不要登录"
    assert output.public_task_slots["target_site_hint"] == "github"
    assert output.public_task_slots["search_query"] == "browser-use-vision"
    assert output.public_task_slots["read_only_intent"] is True

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


def test_public_documentation_search_preserves_task_slots_and_readonly_boundaries():
    output = RuleBasedNormalizer().normalize("Search Python docs for pathlib, do not log in")

    assert isinstance(output, BrowserTaskRequest)
    assert output.public_task_slots["target_site_hint"] == "python docs"
    assert output.public_task_slots["search_query"] == "pathlib"
    assert output.public_task_slots["read_only_intent"] is True
    assert "public_readonly" in output.constraints
    assert "stop_if_login_required" in output.stop_conditions
    assert output.safety_flags == []

    result = NormalizerValidator().validate(output)
    assert result.accepted is True


def test_public_reference_read_preserves_read_and_extraction_targets():
    output = RuleBasedNormalizer().normalize("Read the pathlib Path section on Python docs")

    assert isinstance(output, BrowserTaskRequest)
    assert output.intent_type is BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO
    assert output.public_task_slots["target_site_hint"] == "python docs"
    assert output.public_task_slots["read_target"] == "pathlib Path section"
    assert output.public_task_slots["extraction_target"] == "pathlib Path section"
    assert output.public_task_slots["read_only_intent"] is True


def test_expanded_public_reference_commands_preserve_safe_slots():
    openai = RuleBasedNormalizer().normalize("Read the OpenAI docs responses API guide")
    mdn = RuleBasedNormalizer().normalize("Search MDN docs for fetch API")
    wikipedia = RuleBasedNormalizer().normalize("Read the Wikipedia page for Alan Turing")

    assert isinstance(openai, BrowserTaskRequest)
    assert openai.public_task_slots["target_site_hint"] == "openai docs"
    assert openai.public_task_slots["read_target"] == "OpenAI docs responses API guide"
    assert openai.public_task_slots["read_only_intent"] is True
    assert isinstance(mdn, BrowserTaskRequest)
    assert mdn.public_task_slots["target_site_hint"] == "mdn"
    assert mdn.public_task_slots["search_query"] == "fetch API"
    assert mdn.public_task_slots["read_only_intent"] is True
    assert isinstance(wikipedia, BrowserTaskRequest)
    assert wikipedia.public_task_slots["target_site_hint"] == "wikipedia"
    assert wikipedia.public_task_slots["read_target"] == "Wikipedia page for Alan Turing"
    assert wikipedia.public_task_slots["read_only_intent"] is True


def test_useful_public_package_and_release_commands_preserve_safe_slots():
    pypi = RuleBasedNormalizer().normalize("Read PyPI package metadata for playwright")
    npm = RuleBasedNormalizer().normalize("Check npm package metadata for playwright")
    release = RuleBasedNormalizer().normalize("Read GitHub release notes for microsoft/playwright")

    assert isinstance(pypi, BrowserTaskRequest)
    assert pypi.public_task_slots["target_site_hint"] == "pypi"
    assert pypi.public_task_slots["task_category"] == "package_metadata"
    assert pypi.public_task_slots["package_ecosystem"] == "pypi"
    assert pypi.public_task_slots["package_name"] == "playwright"
    assert pypi.public_task_slots["read_only_intent"] is True
    assert isinstance(npm, BrowserTaskRequest)
    assert npm.public_task_slots["target_site_hint"] == "npm"
    assert npm.public_task_slots["task_category"] == "package_metadata"
    assert npm.public_task_slots["package_ecosystem"] == "npm"
    assert npm.public_task_slots["package_name"] == "playwright"
    assert isinstance(release, BrowserTaskRequest)
    assert release.public_task_slots["target_site_hint"] == "github"
    assert release.public_task_slots["task_category"] == "release_notes"
    assert release.public_task_slots["release_target"] == "microsoft/playwright"
    assert release.public_task_slots["owner"] == "microsoft"
    assert release.public_task_slots["repo"] == "playwright"
    assert release.public_task_slots["read_only_intent"] is True


def test_public_commands_with_unsafe_urls_preserve_safety_concerns():
    unsafe_protocol = RuleBasedNormalizer().normalize("Open file:///Users/example/private.txt and read it")
    private_network = RuleBasedNormalizer().normalize("Open http://127.0.0.1/admin and read it")
    credentialed = RuleBasedNormalizer().normalize("Open https://user:secret@github.com/search?q=agent")

    assert isinstance(unsafe_protocol, BrowserTaskRequest)
    assert "unsafe_protocol" in unsafe_protocol.safety_flags
    assert isinstance(private_network, BrowserTaskRequest)
    assert "private_network_target" in private_network.safety_flags
    assert isinstance(credentialed, BrowserTaskRequest)
    assert "credentialed_url" in credentialed.safety_flags


def test_public_broad_or_mutation_commands_do_not_become_safe_public_tasks():
    broad = RuleBasedNormalizer().normalize("Browse all public docs websites until you find everything")
    mutation = RuleBasedNormalizer().normalize("Open Python docs and download the PDF")

    assert isinstance(broad, ClarificationRequest)
    assert broad.reason == "unsupported_public_task_scope"
    assert isinstance(mutation, BrowserTaskRequest)
    assert "file_transfer" in mutation.safety_flags
    assert mutation.requires_confirmation is True


def test_github_repository_search_preserves_query_and_readonly_boundaries():
    output = RuleBasedNormalizer().normalize("Search GitHub repositories for agent tooling, do not log in")

    assert isinstance(output, BrowserTaskRequest)
    assert output.intent_type is BrowserIntentType.SEARCH_OPEN
    assert output.task == "Search GitHub repositories for agent tooling, do not log in"
    assert output.public_task_slots["target_site_hint"] == "github"
    assert output.public_task_slots["task_kind_hint"] == "github-repo-search"
    assert output.public_task_slots["search_query"] == "agent tooling"
    assert output.public_task_slots["read_only_intent"] is True
    assert "public_readonly" in output.constraints
    assert "stop_if_login_required" in output.stop_conditions
    assert output.safety_flags == []

    result = NormalizerValidator().validate(output)
    assert result.accepted is True
    assert result.requires_confirmation is False


def test_github_public_repository_read_preserves_repo_slug_and_read_target():
    output = RuleBasedNormalizer().normalize("Read the README for Raidriar7170/gui-agent-benchmark on GitHub")

    assert isinstance(output, BrowserTaskRequest)
    assert output.intent_type is BrowserIntentType.EXTRACT_COMPARE_VISIBLE_INFO
    assert output.public_task_slots["target_site_hint"] == "github"
    assert output.public_task_slots["task_kind_hint"] == "github-public-repo-read"
    assert output.public_task_slots["repo_slug"] == "Raidriar7170/gui-agent-benchmark"
    assert output.public_task_slots["owner"] == "Raidriar7170"
    assert output.public_task_slots["repo"] == "gui-agent-benchmark"
    assert output.public_task_slots["read_target"] == "README"
    assert output.public_task_slots["read_only_intent"] is True
    assert output.safety_flags == []


def test_unsupported_github_account_or_broad_research_commands_do_not_run_as_safe_public_tasks():
    account = RuleBasedNormalizer().normalize("Open GitHub and star Raidriar7170/gui-agent-benchmark")
    broad = RuleBasedNormalizer().normalize("Find the best GitHub agent projects and rank all of them")

    assert isinstance(account, BrowserTaskRequest)
    assert "github_account_action" in account.safety_flags
    assert account.requires_confirmation is True
    assert isinstance(broad, ClarificationRequest)
    assert broad.reason == "unsupported_public_task_scope"


def test_structured_output_normalizer_records_mock_llm_provenance():
    result = StructuredOutputNormalizer(
        llm_client=MockLLMNormalizerClient(),
        provider_mode="mock_llm",
        prompt_schema_version="normalizer.test",
    ).normalize_with_provenance("打开 GitHub 搜索 browser-use-vision，不要登录")

    assert isinstance(result.output, BrowserTaskRequest)
    assert result.output.public_task_slots["search_query"] == "browser-use-vision"
    assert result.provenance.provider_mode == "mock_llm"
    assert result.provenance.output_source == "llm"
    assert result.provenance.prompt_schema_version == "normalizer.test"
    assert result.provenance.schema_status == "passed"
    assert result.provenance.output_kind == "browser_task_request"
    assert result.provenance.fallback_reason is None


def test_structured_output_normalizer_falls_back_and_records_malformed_llm_output():
    class MalformedClient:
        provider_name = "malformed-test"

        def normalize(self, transcript_text):
            return "{not-json"

    result = StructuredOutputNormalizer(
        llm_client=MalformedClient(),
        provider_mode="mock_llm",
        fallback_policy="rule",
    ).normalize_with_provenance("点击右上角的放大镜图标")

    assert isinstance(result.output, BrowserTaskRequest)
    assert result.output.intent_type is BrowserIntentType.CLICK_VISUAL_TARGET
    assert result.provenance.provider_mode == "mock_llm"
    assert result.provenance.output_source == "fallback_rule"
    assert result.provenance.schema_status == "failed"
    assert "malformed" in result.provenance.fallback_reason


def test_structured_output_normalizer_can_emit_clarification_when_fallback_policy_is_clarify():
    class UnavailableClient:
        provider_name = "unavailable-test"

        def normalize(self, transcript_text):
            raise NormalizerProviderError("provider unavailable")

    result = StructuredOutputNormalizer(
        llm_client=UnavailableClient(),
        provider_mode="mock_llm",
        fallback_policy="clarify",
    ).normalize_with_provenance("打开 GitHub 搜索 browser-use-vision")

    assert isinstance(result.output, ClarificationRequest)
    assert result.output.reason == "llm_normalizer_unavailable"
    assert result.provenance.output_source == "clarification"
    assert result.provenance.schema_status == "failed"
    assert "provider unavailable" in result.provenance.fallback_reason


def test_structured_output_normalizer_rejects_unknown_fallback_policy():
    with pytest.raises(ValueError, match="fallback policy"):
        StructuredOutputNormalizer(fallback_policy="execute_anyway")
