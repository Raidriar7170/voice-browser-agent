from __future__ import annotations

import asyncio
import json
from pathlib import Path

from voice_browser_agent.executor import BrowserExecutorAdapter, BrowserExecutorConfig
from voice_browser_agent.models import (
    ASRTranscript,
    ASRTranscriptMetadata,
    BrowserTaskRequest,
    ClarificationRequest,
    ConfirmationState,
    ExecutionStatus,
    ExecutionTrace,
)
from voice_browser_agent.normalizer import RuleBasedNormalizer
from voice_browser_agent.safety import ConfirmationGate
from voice_browser_agent.trace_writer import TraceWriter
from voice_browser_agent.validator import NormalizerValidator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = PROJECT_ROOT / "fixtures/audio"
TRACE_DIR = PROJECT_ROOT / "fixtures/traces/sanitized"


async def build_trace(fixture_path: Path) -> None:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    demo_id = fixture["audio_id"]
    transcript = ASRTranscript(
        text=fixture["expected_transcript"],
        metadata=ASRTranscriptMetadata(
            adapter_name="fixture-asr",
            input_audio_id=demo_id,
            language_mode=fixture["language_mode"],
            confidence=0.99,
            diagnostics={"fixture": True, "sanitized_public": True},
        ),
    )
    normalizer = RuleBasedNormalizer()
    validator = NormalizerValidator()
    gate = ConfirmationGate()
    normalized = normalizer.normalize(transcript.text)
    validation = validator.validate(normalized)
    trace = ExecutionTrace(
        execution_id=f"demo-{demo_id}",
        transcript=transcript,
        normalized_output=normalized,
        validator_decision=validation,
    )

    if isinstance(normalized, ClarificationRequest):
        trace.final_status = ExecutionStatus.CLARIFICATION_REQUIRED
    elif not validation.accepted:
        trace.final_status = ExecutionStatus.BLOCKED
        trace.failure_reason = validation.reason
    elif isinstance(normalized, BrowserTaskRequest):
        decision = gate.evaluate(normalized, validation)
        trace.confirmation_decision = decision
        if decision.state is ConfirmationState.PENDING:
            trace.final_status = ExecutionStatus.PENDING_CONFIRMATION
        else:
            result = await BrowserExecutorAdapter(BrowserExecutorConfig(dry_run=True)).execute(
                normalized,
                execution_id=trace.execution_id,
            )
            trace.browser_actions.extend(result.actions)
            trace.grounding_evidence_refs.extend(result.grounding_evidence_refs)
            trace.final_status = result.final_status
            trace.failure_reason = result.failure_reason
            trace.stop_reason = result.stop_reason

    writer = TraceWriter(TRACE_DIR)
    writer.write_sanitized(trace, export_dir=TRACE_DIR)


async def main() -> None:
    for fixture_path in sorted(FIXTURE_DIR.glob("*.fixture.json")):
        await build_trace(fixture_path)


if __name__ == "__main__":
    asyncio.run(main())
