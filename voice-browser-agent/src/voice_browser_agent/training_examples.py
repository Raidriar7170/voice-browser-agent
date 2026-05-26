from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .models import ExecutionTrace, utc_now
from .trace_writer import sanitize_trace_dict


class TraceDerivedTrainingExample(BaseModel):
    source_execution_id: str
    input: dict[str, Any]
    target_output: dict[str, Any]
    validator_decision: dict[str, Any] | None = None
    final_status: str
    safety_flags: list[str] = Field(default_factory=list)
    human_correction: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)


def training_example_from_trace(
    trace: ExecutionTrace,
    human_correction: dict[str, Any] | None = None,
) -> TraceDerivedTrainingExample:
    if trace.transcript is None or trace.normalized_output is None:
        raise ValueError("Trace-derived training examples require transcript and normalized output")

    target_output = sanitize_trace_dict(trace.normalized_output.model_dump(mode="json"))
    input_payload = sanitize_trace_dict(
        {
            "transcript_text": trace.transcript.text,
            "transcript_metadata": trace.transcript.metadata.model_dump(mode="json"),
        }
    )
    validator_decision = (
        sanitize_trace_dict(trace.validator_decision.model_dump(mode="json"))
        if trace.validator_decision is not None
        else None
    )
    correction = sanitize_trace_dict(human_correction) if human_correction is not None else None

    return TraceDerivedTrainingExample(
        source_execution_id=trace.execution_id,
        input=input_payload,
        target_output=target_output,
        validator_decision=validator_decision,
        final_status=trace.final_status.value,
        safety_flags=target_output.get("safety_flags", []) if isinstance(target_output, dict) else [],
        human_correction=correction,
    )
