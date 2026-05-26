import json

from voice_browser_agent.models import (
    AgenticActionResult,
    AgenticRecoveryDecision,
    AgenticVerificationDecision,
    AgenticVisionStep,
    ASRTranscript,
    ASRTranscriptMetadata,
    BrowserIntentType,
    BrowserTaskRequest,
    ClarificationRequest,
    ConfirmationDecision,
    ConfirmationState,
    ExecutionStatus,
    ExecutionTrace,
    ValidationResult,
    VisualReference,
)
from voice_browser_agent.trace_writer import TraceWriter


def test_browser_task_request_requires_bounded_intent_and_stop_conditions():
    request = BrowserTaskRequest(
        task="打开 GitHub 并搜索 browser-use-vision",
        intent_type=BrowserIntentType.SEARCH_OPEN,
        constraints=["不要登录", "只查看公开页面"],
        visual_references=[],
        requires_confirmation=False,
        stop_conditions=["login_required", "payment_or_checkout"],
    )

    assert request.intent_type is BrowserIntentType.SEARCH_OPEN
    assert "login_required" in request.stop_conditions


def test_clarification_request_serializes_as_normalized_output():
    clarification = ClarificationRequest(
        question="你想打开哪个网站？",
        reason="missing_target",
        transcript_text="打开那个网站",
    )

    assert clarification.kind == "clarification_request"
    assert clarification.model_dump()["reason"] == "missing_target"


def test_trace_writer_persists_complete_sanitized_execution_trace(tmp_path):
    transcript = ASRTranscript(
        text="点击右上角的放大镜图标",
        metadata=ASRTranscriptMetadata(
            adapter_name="fixture-asr",
            input_audio_id="fixture-icon-search",
            language_mode="zh-first",
            confidence=0.94,
            diagnostics={"fixture": True},
        ),
    )
    normalized = BrowserTaskRequest(
        task="Click the search icon in the top-right toolbar.",
        intent_type=BrowserIntentType.CLICK_VISUAL_TARGET,
        constraints=["controlled demo page only"],
        visual_references=[
            VisualReference(kind="icon", text="top-right magnifying glass", source="transcript")
        ],
        requires_confirmation=False,
        stop_conditions=["login_required", "irreversible_submit"],
    )
    trace = ExecutionTrace(
        execution_id="exec-001",
        transcript=transcript,
        normalized_output=normalized,
        validator_decision=ValidationResult(
            accepted=True,
            reason="supported intent with visual reference",
            issues=[],
            requires_confirmation=False,
        ),
        confirmation_decision=ConfirmationDecision(
            state=ConfirmationState.CONFIRMED,
            reason="no confirmation required",
        ),
        final_status=ExecutionStatus.SUCCEEDED,
    )
    trace.add_browser_action(
        action_type="click",
        description="clicked visual target search icon",
        screenshot_ref="screenshots/sanitized/icon-search.png",
        grounding_evidence_refs=["grounding/icon-search.json"],
    )

    path = TraceWriter(tmp_path).write(trace)
    saved = json.loads(path.read_text())

    assert saved["execution_id"] == "exec-001"
    assert saved["transcript"]["metadata"]["adapter_name"] == "fixture-asr"
    assert saved["normalized_output"]["kind"] == "browser_task_request"
    assert saved["browser_actions"][0]["grounding_evidence_refs"] == ["grounding/icon-search.json"]
    assert "raw_audio_path" not in json.dumps(saved)


def test_agentic_step_trace_serializes_and_sanitizes_private_nested_fields(tmp_path):
    trace = ExecutionTrace(execution_id="exec-agentic", final_status=ExecutionStatus.STOPPED)
    trace.agentic_steps.append(
        AgenticVisionStep(
            step_index=1,
            observation_summary="Saw an icon-only toolbar with one magnifying-glass button.",
            target_status="resolved",
            selected_target_ref="som:button-1",
            grounding_evidence_refs=["grounding/agentic/icon-search-step-1.json"],
            screenshot_ref="screenshots/sanitized/agentic/icon-search-step-1.png",
            selected_action="click som:button-1",
            action_result=AgenticActionResult(
                status="succeeded",
                description="clicked search icon",
                browser_state={
                    "visible_text": "Search opened",
                    "raw_screenshot": "/private/raw.png",
                    "cookies": ["session=secret"],
                },
            ),
            verification_decision=AgenticVerificationDecision(
                passed=True,
                reason="search panel opened",
            ),
            recovery_decision=AgenticRecoveryDecision(kind="none", reason="progress verified"),
        )
    )

    writer = TraceWriter(tmp_path)
    saved = json.loads(writer.write(trace).read_text(encoding="utf-8"))
    exported = writer.export_sanitized(trace)
    exported_text = json.dumps(exported)

    assert saved["agentic_steps"][0]["step_index"] == 1
    assert saved["agentic_steps"][0]["selected_target_ref"] == "som:button-1"
    assert "raw_screenshot" not in exported_text
    assert "cookies" not in exported_text
    assert "/private/raw.png" not in exported_text
