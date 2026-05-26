import json

import pytest

from voice_browser_agent.models import (
    ASRTranscript,
    ASRTranscriptMetadata,
    BrowserIntentType,
    BrowserTaskRequest,
    ClarificationRequest,
    ExecutionStatus,
    ExecutionTrace,
    ValidationResult,
)
from voice_browser_agent.training_examples import training_example_from_trace


def _transcript(text: str = "点击右上角的放大镜图标") -> ASRTranscript:
    return ASRTranscript(
        text=text,
        metadata=ASRTranscriptMetadata(
            adapter_name="fixture-asr",
            input_audio_id="icon-search",
            language_mode="zh-first",
            confidence=0.97,
            diagnostics={"fixture": True, "token": "secret-token"},
        ),
    )


def test_browser_task_trace_becomes_sanitized_training_example():
    trace = ExecutionTrace(
        execution_id="exec-training-task",
        transcript=_transcript(),
        normalized_output=BrowserTaskRequest(
            task="Click the top-right search icon.",
            intent_type=BrowserIntentType.CLICK_VISUAL_TARGET,
            constraints=["controlled demo page only"],
            visual_references=[{"kind": "icon", "text": "top-right magnifying glass"}],
            requires_confirmation=False,
            stop_conditions=["login_required"],
            safety_flags=[],
        ),
        validator_decision=ValidationResult(
            accepted=True,
            reason="request accepted by deterministic validator",
        ),
        final_status=ExecutionStatus.SUCCEEDED,
        execution_runtime={
            "remote_vision_backend_url": "https://private.invalid/vision",
            "cookies": ["session=secret"],
        },
    )

    example = training_example_from_trace(
        trace,
        human_correction={"task": "Click the search icon in the toolbar."},
    )
    exported = example.model_dump(mode="json")
    exported_text = json.dumps(exported, ensure_ascii=False)

    assert exported["source_execution_id"] == "exec-training-task"
    assert exported["input"]["transcript_text"] == "点击右上角的放大镜图标"
    assert exported["target_output"]["kind"] == "browser_task_request"
    assert exported["target_output"]["intent_type"] == "click_visual_target"
    assert exported["validator_decision"]["accepted"] is True
    assert exported["final_status"] == "succeeded"
    assert exported["human_correction"]["task"] == "Click the search icon in the toolbar."
    assert "secret-token" not in exported_text
    assert "remote_vision_backend_url" not in exported_text
    assert "cookies" not in exported_text


def test_clarification_trace_preserves_question_as_training_target():
    trace = ExecutionTrace(
        execution_id="exec-training-clarify",
        transcript=_transcript("打开那个页面"),
        normalized_output=ClarificationRequest(
            question="请说明要打开的网站、页面或可见目标。",
            reason="ambiguous_target",
            transcript_text="打开那个页面",
        ),
        final_status=ExecutionStatus.CLARIFICATION_REQUIRED,
    )

    example = training_example_from_trace(trace)

    assert example.target_output["kind"] == "clarification_request"
    assert example.target_output["reason"] == "ambiguous_target"
    assert example.target_output["question"] == "请说明要打开的网站、页面或可见目标。"


def test_training_example_requires_transcript_and_normalized_output():
    with pytest.raises(ValueError, match="transcript and normalized output"):
        training_example_from_trace(ExecutionTrace(execution_id="exec-empty"))
