from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .asr import (
    ASRAdapterError,
    FixtureManifestASRAdapter,
    FallbackASRAdapter,
    RemoteASRAdapter,
    TranscriptOrchestrator,
    UnavailableASRAdapter,
)
from .config import RuntimeConfig, load_config
from .demo_tasks import ControlledDemoTask, get_live_controlled_task
from .executor import BrowserExecutorAdapter, BrowserExecutorConfig
from .ingestion import AudioIngestor, IngestionError
from .models import (
    ASRTranscript,
    ASRTranscriptMetadata,
    BrowserTaskRequest,
    ClarificationRequest,
    ConfirmationState,
    ExecutionMode,
    ExecutionStatus,
    ExecutionTrace,
    SpokenCommandInput,
)
from .normalizer import StructuredOutputNormalizer
from .safety import ConfirmationGate
from .trace_writer import TraceWriter
from .tts import StatusVoiceFeedback
from .validator import NormalizerValidator


class CommandPayload(BaseModel):
    transcript_text: str | None = None
    audio_id: str | None = None
    fixture_id: str | None = None
    execution_mode: ExecutionMode | None = None


class ConfirmationPayload(BaseModel):
    decision: str
    decided_by: str = "operator"


def create_app(runtime_dir: str | Path | None = None) -> FastAPI:
    config = load_config(runtime_dir)
    app = FastAPI(title="Voice-to-Browser Agent", version="0.1.0")
    state = AppState(config)
    app.state.voice_browser = state

    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    def console() -> str:
        index = static_dir / "index.html"
        if index.exists():
            return index.read_text(encoding="utf-8")
        return "<main><h1>Voice-to-Browser Agent</h1></main>"

    @app.post("/api/ingest")
    async def ingest(file: UploadFile = File(...)) -> dict[str, Any]:
        data = await file.read()
        try:
            command_input = state.ingestor.ingest_upload(
                filename=file.filename or "command",
                content_type=file.content_type or "application/octet-stream",
                data=data,
            )
        except IngestionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        state.register_input(command_input)
        return command_input.model_dump(mode="json")

    @app.post("/api/recordings")
    async def recording(file: UploadFile = File(...)) -> dict[str, Any]:
        data = await file.read()
        try:
            command_input = state.ingestor.ingest_recording(
                data=data,
                content_type=file.content_type or "audio/webm",
            )
        except IngestionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        state.register_input(command_input)
        return command_input.model_dump(mode="json")

    @app.post("/api/normalize")
    async def normalize(payload: CommandPayload) -> dict[str, Any]:
        trace = await state.prepare_trace(payload)
        state.writer.write(trace)
        return state.trace_response(trace)

    @app.post("/api/executions")
    async def start_execution(payload: CommandPayload) -> dict[str, Any]:
        trace = await state.prepare_trace(payload)
        if isinstance(trace.normalized_output, ClarificationRequest):
            trace.final_status = ExecutionStatus.CLARIFICATION_REQUIRED
            state.writer.write(trace)
            return state.trace_response(trace)

        if trace.validator_decision is None or not trace.validator_decision.accepted:
            trace.final_status = ExecutionStatus.BLOCKED
            trace.failure_reason = trace.validator_decision.reason if trace.validator_decision else "not validated"
            state.writer.write(trace)
            return state.trace_response(trace)

        if trace.confirmation_decision and trace.confirmation_decision.state is ConfirmationState.PENDING:
            trace.final_status = ExecutionStatus.PENDING_CONFIRMATION
            state.writer.write(trace)
            return state.trace_response(trace)

        assert isinstance(trace.normalized_output, BrowserTaskRequest)
        result = await state.executor.execute(trace.normalized_output, trace.execution_id)
        state.apply_execution_result(trace, result)
        state.writer.write(trace)
        return state.trace_response(trace)

    @app.post("/api/fixtures/{fixture_id}/executions")
    async def start_fixture_execution(fixture_id: str, payload: CommandPayload | None = None) -> dict[str, Any]:
        payload = payload or CommandPayload()
        mode = state.execution_mode_for_payload(payload)
        controlled_task = state.controlled_task_for_mode(fixture_id, mode)
        trace = await state.prepare_trace(CommandPayload(fixture_id=fixture_id))
        trace.execution_mode = mode
        if isinstance(trace.normalized_output, BrowserTaskRequest) and trace.confirmation_decision:
            if trace.confirmation_decision.state is ConfirmationState.PENDING:
                trace.final_status = ExecutionStatus.PENDING_CONFIRMATION
            elif trace.validator_decision and trace.validator_decision.accepted:
                request = state.with_controlled_target(trace.normalized_output, controlled_task)
                trace.normalized_output = request
                result = await state.executor_for_mode(mode, controlled_task).execute(
                    request,
                    trace.execution_id,
                )
                state.apply_execution_result(trace, result)
        elif isinstance(trace.normalized_output, ClarificationRequest):
            trace.final_status = ExecutionStatus.CLARIFICATION_REQUIRED
        state.writer.write(trace)
        return state.trace_response(trace)

    @app.post("/api/executions/{execution_id}/confirmation")
    async def confirmation(execution_id: str, payload: ConfirmationPayload) -> dict[str, Any]:
        trace = state.get_trace(execution_id)
        if trace.confirmation_decision is None:
            raise HTTPException(status_code=409, detail="No confirmation is pending")
        if (
            trace.confirmation_decision.state is not ConfirmationState.PENDING
            or trace.final_status is not ExecutionStatus.PENDING_CONFIRMATION
        ):
            raise HTTPException(status_code=409, detail="Confirmation has already been decided")

        if payload.decision == "cancel":
            trace.confirmation_decision = state.gate.cancel(
                trace.confirmation_decision,
                decided_by=payload.decided_by,
            )
            trace.final_status = ExecutionStatus.CANCELLED
            trace.stop_reason = "operator_cancelled"
        elif payload.decision == "confirm":
            trace.confirmation_decision = state.gate.confirm(
                trace.confirmation_decision,
                decided_by=payload.decided_by,
            )
            if isinstance(trace.normalized_output, BrowserTaskRequest):
                result = await state.executor.execute(trace.normalized_output, trace.execution_id)
                state.apply_execution_result(trace, result)
        else:
            raise HTTPException(status_code=400, detail="decision must be confirm or cancel")

        state.writer.write(trace)
        return state.trace_response(trace)

    @app.get("/api/traces/{execution_id}")
    def trace(execution_id: str) -> dict[str, Any]:
        return state.get_trace(execution_id).model_dump(mode="json")

    @app.get("/api/traces/{execution_id}/export")
    def export_trace(execution_id: str) -> JSONResponse:
        trace = state.get_trace(execution_id)
        return JSONResponse(state.writer.export_sanitized(trace))

    @app.get("/api/status-voice")
    def status_voice(status: str, reason: str | None = None) -> dict[str, str | bool]:
        return state.voice_feedback.render_status(status=status, reason=reason)

    return app


class AppState:
    def __init__(self, config: RuntimeConfig):
        self.config = config
        self.ingestor = AudioIngestor(config.uploads_dir)
        self.command_inputs: dict[str, SpokenCommandInput] = {}
        self.fixture_asr = FixtureManifestASRAdapter()
        self.asr_orchestrator = TranscriptOrchestrator(
            primary=RemoteASRAdapter(config.primary_asr_url)
            if config.primary_asr_url
            else UnavailableASRAdapter(),
            fallback=FallbackASRAdapter(config.fallback_asr_model),
        )
        self.normalizer = StructuredOutputNormalizer()
        self.validator = NormalizerValidator()
        self.gate = ConfirmationGate()
        self.writer = TraceWriter(config.traces_dir)
        self.agent_factory = None
        self.executor = BrowserExecutorAdapter(
            BrowserExecutorConfig(
                remote_vision_backend_url=config.remote_vision_backend_url,
                local_browser=True,
                dry_run=config.demo_dry_run,
            )
        )
        self.voice_feedback = StatusVoiceFeedback(enabled=config.enable_status_voice_feedback)

    def register_input(self, command_input: SpokenCommandInput) -> None:
        self.command_inputs[command_input.audio_id] = command_input

    async def prepare_trace(self, payload: CommandPayload) -> ExecutionTrace:
        transcript = await self.transcript_for_payload(payload)
        normalized = self.normalizer.normalize(transcript.text)
        validation = self.validator.validate(normalized)
        trace = ExecutionTrace(
            transcript=transcript,
            normalized_output=normalized,
            validator_decision=validation,
        )
        if isinstance(normalized, BrowserTaskRequest):
            trace.confirmation_decision = self.gate.evaluate(normalized, validation)
        return trace

    async def transcript_for_payload(self, payload: CommandPayload) -> ASRTranscript:
        if payload.transcript_text:
            return ASRTranscript(
                text=payload.transcript_text,
                metadata=ASRTranscriptMetadata(
                    adapter_name="direct-preview",
                    input_audio_id="transcript-preview",
                    language_mode="zh-first",
                    diagnostics={"source": "api"},
                ),
            )
        command_input = self.command_input_for_payload(payload)
        try:
            if command_input.source_type == "fixture":
                return await self.fixture_asr.transcribe(command_input)
            return await self.asr_orchestrator.transcribe(command_input)
        except ASRAdapterError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    def command_input_for_payload(self, payload: CommandPayload) -> SpokenCommandInput:
        if payload.audio_id:
            command_input = self.command_inputs.get(payload.audio_id)
            if command_input is None:
                raise HTTPException(status_code=404, detail="audio_id not found")
            return command_input
        if payload.fixture_id:
            return self.load_fixture_input(payload.fixture_id)
        raise HTTPException(status_code=400, detail="Provide transcript_text, audio_id, or fixture_id")

    def load_fixture_input(self, fixture_id: str) -> SpokenCommandInput:
        safe_id = fixture_id.replace("/", "").replace("\\", "")
        fixture_path = Path(__file__).resolve().parents[2] / "fixtures" / "audio" / f"{safe_id}.fixture.json"
        if not fixture_path.exists():
            raise HTTPException(status_code=404, detail="fixture not found")
        command_input = SpokenCommandInput(
            source_type="fixture",
            audio_id=safe_id,
            content_type="application/vnd.voice-browser.fixture+json",
            size_bytes=fixture_path.stat().st_size,
            storage_path=fixture_path,
        )
        self.register_input(command_input)
        return command_input

    def apply_execution_result(self, trace: ExecutionTrace, result) -> None:
        trace.execution_mode = result.execution_mode
        trace.execution_runtime = result.runtime
        for action in result.actions:
            trace.browser_actions.append(action)
            self.extend_grounding_refs(trace, action.grounding_evidence_refs)
        trace.agentic_steps.extend(result.agentic_steps)
        for step in result.agentic_steps:
            self.extend_grounding_refs(trace, step.grounding_evidence_refs)
        trace.final_status = result.final_status
        trace.failure_reason = result.failure_reason
        trace.stop_reason = result.stop_reason

    def extend_grounding_refs(self, trace: ExecutionTrace, refs: list[str]) -> None:
        for ref in refs:
            if ref not in trace.grounding_evidence_refs:
                trace.grounding_evidence_refs.append(ref)

    def execution_mode_for_payload(self, payload: CommandPayload) -> ExecutionMode:
        if payload.execution_mode is not None:
            return payload.execution_mode
        return ExecutionMode.DEMO_PREVIEW if self.config.demo_dry_run else ExecutionMode.LIVE_CONTROLLED

    def controlled_task_for_mode(
        self,
        fixture_id: str,
        mode: ExecutionMode,
    ) -> ControlledDemoTask | None:
        if mode is ExecutionMode.DEMO_PREVIEW:
            return None
        controlled_task = get_live_controlled_task(fixture_id)
        if controlled_task is None:
            raise HTTPException(
                status_code=400,
                detail=f"Fixture '{fixture_id}' is not selected for live controlled execution",
            )
        return controlled_task

    def with_controlled_target(
        self,
        request: BrowserTaskRequest,
        controlled_task: ControlledDemoTask | None,
    ) -> BrowserTaskRequest:
        if controlled_task is None:
            return request
        return request.model_copy(
            update={
                "controlled_target_ref": controlled_task.target_ref,
                "constraints": [
                    *request.constraints,
                    f"controlled target: {controlled_task.target_ref}",
                ],
            }
        )

    def executor_for_mode(
        self,
        mode: ExecutionMode,
        controlled_task: ControlledDemoTask | None,
    ) -> BrowserExecutorAdapter:
        return BrowserExecutorAdapter(
            BrowserExecutorConfig(
                remote_vision_backend_url=self.config.remote_vision_backend_url,
                local_browser=True,
                dry_run=mode is ExecutionMode.DEMO_PREVIEW,
                execution_mode=mode,
                agentic_execution=mode is ExecutionMode.LIVE_CONTROLLED,
                controlled_fixture_id=controlled_task.fixture_id if controlled_task else None,
                controlled_target_ref=controlled_task.target_ref if controlled_task else None,
                controlled_target_url=controlled_task.target_url if controlled_task else None,
            ),
            agent_factory=self.agent_factory,
        )

    def get_trace(self, execution_id: str) -> ExecutionTrace:
        path = self.config.traces_dir / f"{execution_id}.json"
        if not path.exists():
            raise HTTPException(status_code=404, detail="trace not found")
        return self.writer.read(execution_id)

    def trace_response(self, trace: ExecutionTrace) -> dict[str, Any]:
        payload = trace.model_dump(mode="json")
        payload["status_voice"] = self.voice_feedback.render_status(
            status=trace.final_status.value,
            reason=trace.stop_reason or trace.failure_reason,
        )
        return payload


app = create_app()
