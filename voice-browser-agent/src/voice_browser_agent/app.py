from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import quote, quote_plus

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
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
    EvidencePrivacyState,
    ExecutionMode,
    ExecutionStatus,
    ExecutionTrace,
    PublicTaskContract,
    RouteDecision,
    RouteType,
    SanitizerStatus,
    SpokenCommandInput,
)
from .normalizer import StructuredOutputNormalizer
from .preflight import build_readiness_report
from .public_readonly import PublicReadonlyRoutingConfig, PublicReadonlyTarget, parse_public_readonly_targets
from .routing import select_execution_route
from .safety import ConfirmationGate
from .trace_writer import TraceWriter, sanitize_trace_dict
from .tts import StatusVoiceFeedback
from .validator import NormalizerValidator


class CommandPayload(BaseModel):
    transcript_text: str | None = None
    reviewed_transcript_text: str | None = None
    audio_id: str | None = None
    fixture_id: str | None = None
    controlled_fixture_id: str | None = None
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

    @app.get("/api/readiness")
    def readiness() -> dict[str, Any]:
        return build_readiness_report(config=state.config)

    @app.post("/api/audio/{audio_id}/transcript")
    async def audio_transcript(audio_id: str) -> dict[str, Any]:
        transcript = await state.transcript_for_payload(CommandPayload(audio_id=audio_id))
        return transcript.model_dump(mode="json")

    @app.post("/api/executions")
    async def start_execution(payload: CommandPayload) -> dict[str, Any]:
        trace = await state.prepare_trace(payload)
        trace.route_decision = state.route_for_trace(trace, payload)
        if isinstance(trace.normalized_output, ClarificationRequest):
            trace.final_status = ExecutionStatus.CLARIFICATION_REQUIRED
            state.apply_route_metadata(trace)
            state.writer.write(trace)
            return state.trace_response(trace)

        if trace.validator_decision is None or not trace.validator_decision.accepted:
            trace.final_status = ExecutionStatus.BLOCKED
            trace.failure_reason = trace.validator_decision.reason if trace.validator_decision else "not validated"
            state.apply_route_metadata(trace)
            state.writer.write(trace)
            return state.trace_response(trace)

        if trace.confirmation_decision and trace.confirmation_decision.state is ConfirmationState.PENDING:
            trace.final_status = ExecutionStatus.PENDING_CONFIRMATION
            state.apply_route_metadata(trace)
            state.writer.write(trace)
            return state.trace_response(trace)

        assert isinstance(trace.normalized_output, BrowserTaskRequest)
        if trace.route_decision and trace.route_decision.route_type is RouteType.BLOCKED:
            trace.final_status = ExecutionStatus.BLOCKED
            trace.stop_reason = trace.route_decision.route_reason
            state.apply_route_metadata(trace)
            state.writer.write(trace)
            return state.trace_response(trace)

        controlled_task = state.controlled_task_for_route(trace.route_decision)
        if controlled_task is not None:
            request = state.with_controlled_target(trace.normalized_output, controlled_task)
            trace.normalized_output = request
            executor = state.executor_for_mode(
                trace.route_decision.execution_mode if trace.route_decision else state.execution_mode_for_payload(payload),
                controlled_task,
                trace.route_decision,
            )
        else:
            request = trace.normalized_output
            executor = state.executor_for_mode(
                trace.route_decision.execution_mode if trace.route_decision else state.execution_mode_for_payload(payload),
                None,
                trace.route_decision,
            )
        result = await executor.execute(request, trace.execution_id)
        state.apply_execution_result(trace, result)
        state.apply_route_metadata(trace)
        state.apply_real_voice_metadata(trace, payload)
        state.writer.write(trace)
        return state.trace_response(trace)

    @app.get("/api/fixtures")
    def fixtures() -> dict[str, Any]:
        return {"fixtures": state.fixture_metadata()}

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
                controlled_task = state.controlled_task_for_route(trace.route_decision)
                executor = state.executor_for_mode(
                    trace.route_decision.execution_mode
                    if trace.route_decision
                    else ExecutionMode.DEMO_PREVIEW,
                    controlled_task,
                    trace.route_decision,
                )
                result = await executor.execute(trace.normalized_output, trace.execution_id)
                state.apply_execution_result(trace, result)
                state.apply_route_metadata(trace)
        else:
            raise HTTPException(status_code=400, detail="decision must be confirm or cancel")

        state.writer.write(trace)
        return state.trace_response(trace)

    @app.get("/api/traces/{execution_id}")
    def trace(execution_id: str) -> dict[str, Any]:
        return state.trace_response(state.get_trace(execution_id))

    @app.get("/api/traces/{execution_id}/export")
    def export_trace(execution_id: str) -> JSONResponse:
        trace = state.get_trace(execution_id)
        return JSONResponse(state.writer.export_sanitized(trace))

    @app.get("/api/executions/{execution_id}/visual-artifacts/{artifact_id}")
    def visual_artifact(execution_id: str, artifact_id: str) -> FileResponse:
        trace = state.get_trace(execution_id)
        artifact = state.visual_artifact_for_trace(trace, artifact_id)
        artifact_path = state.resolve_visual_artifact_path(artifact)
        if not artifact_path.exists() or not artifact_path.is_file():
            raise HTTPException(status_code=404, detail="visual artifact not found")
        return FileResponse(
            artifact_path,
            media_type=str(artifact.get("media_type") or "image/png"),
        )

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

    def route_for_trace(self, trace: ExecutionTrace, payload: CommandPayload) -> RouteDecision:
        if trace.normalized_output is None:
            return RouteDecision(
                route_type=RouteType.BLOCKED,
                execution_mode=ExecutionMode.DEMO_PREVIEW,
                evidence_mode="blocked",
                route_reason="missing normalized output",
                user_message="No normalized command was available for routing.",
                live_evidence_eligible=False,
            )
        return select_execution_route(
            trace.normalized_output,
            trace.validator_decision,
            trace.confirmation_decision,
            public_readonly_config=PublicReadonlyRoutingConfig.from_runtime_config(self.config),
            requested_execution_mode=payload.execution_mode,
        )

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
            transcript = await self.asr_orchestrator.transcribe(command_input)
            if payload.reviewed_transcript_text:
                return self.reviewed_transcript(transcript, payload.reviewed_transcript_text)
            return transcript
        except ASRAdapterError as exc:
            raise HTTPException(status_code=503, detail=f"ASR unavailable: {exc}") from exc

    def reviewed_transcript(
        self,
        transcript: ASRTranscript,
        reviewed_text: str,
    ) -> ASRTranscript:
        original_text = transcript.text
        diagnostics = dict(transcript.metadata.diagnostics)
        diagnostics["input_source"] = "audio"
        diagnostics["transcript_review"] = {
            "status": "edited" if reviewed_text != original_text else "accepted",
            "original_text": original_text,
            "reviewed_text": reviewed_text,
        }
        return ASRTranscript(
            text=reviewed_text,
            metadata=transcript.metadata.model_copy(update={"diagnostics": diagnostics}),
        )

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

    def fixture_metadata(self) -> list[dict[str, Any]]:
        fixture_dir = Path(__file__).resolve().parents[2] / "fixtures" / "audio"
        fixtures: list[dict[str, Any]] = []
        for fixture_path in sorted(fixture_dir.glob("*.fixture.json")):
            payload = json.loads(fixture_path.read_text(encoding="utf-8"))
            fixture_id = str(payload.get("audio_id") or fixture_path.name.removesuffix(".fixture.json"))
            expected_transcript = str(payload.get("expected_transcript") or payload.get("spoken_text") or "")
            controlled_task = get_live_controlled_task(fixture_id)
            supported_modes = [ExecutionMode.DEMO_PREVIEW.value]
            if controlled_task is not None:
                supported_modes.append(ExecutionMode.LIVE_CONTROLLED.value)
            normalized = self.normalizer.normalize(expected_transcript)
            fixtures.append(
                {
                    "id": fixture_id,
                    "label": fixture_id.replace("-", " ").title(),
                    "expected_transcript": expected_transcript,
                    "source": payload.get("source", "fixture"),
                    "supported_execution_modes": supported_modes,
                    "visual_heavy": isinstance(normalized, BrowserTaskRequest)
                    and bool(normalized.visual_references),
                    "target_ref": controlled_task.target_ref if controlled_task else None,
                }
            )
        return fixtures

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
        if result.runtime.get("evidence_privacy_state"):
            trace.evidence_privacy_state = EvidencePrivacyState(result.runtime["evidence_privacy_state"])
        if result.runtime.get("sanitizer_status"):
            trace.sanitizer_status = SanitizerStatus(result.runtime["sanitizer_status"])

    def apply_route_metadata(self, trace: ExecutionTrace) -> None:
        if trace.route_decision is None:
            return
        trace.execution_mode = trace.execution_mode or trace.route_decision.execution_mode
        route_payload = trace.route_decision.model_dump(mode="json")
        trace.execution_runtime["route_decision"] = route_payload
        trace.execution_runtime.setdefault("evidence_mode", trace.route_decision.evidence_mode)
        trace.execution_runtime.setdefault("route_type", trace.route_decision.route_type.value)
        trace.evidence_privacy_state = trace.route_decision.evidence_privacy_state
        trace.sanitizer_status = trace.route_decision.sanitizer_status
        if trace.route_decision.controlled_fixture_id:
            trace.execution_runtime.setdefault(
                "controlled_fixture_id",
                trace.route_decision.controlled_fixture_id,
            )
        if trace.route_decision.controlled_target_ref:
            trace.execution_runtime.setdefault(
                "controlled_target_ref",
                trace.route_decision.controlled_target_ref,
            )

    def extend_grounding_refs(self, trace: ExecutionTrace, refs: list[str]) -> None:
        for ref in refs:
            if ref not in trace.grounding_evidence_refs:
                trace.grounding_evidence_refs.append(ref)

    def apply_real_voice_metadata(self, trace: ExecutionTrace, payload: CommandPayload) -> None:
        if not payload.audio_id or not payload.reviewed_transcript_text:
            return
        if trace.route_decision is None or not trace.route_decision.live_evidence_eligible:
            trace.execution_runtime["input_source"] = "audio"
            return
        trace.execution_runtime["evidence_mode"] = "real_voice_controlled"
        trace.execution_runtime["input_source"] = "audio"
        trace.execution_runtime["audio"] = {
            "input_audio_id": payload.audio_id,
            "source_audio_discarded": True,
        }
        if trace.transcript is not None:
            diagnostics = trace.transcript.metadata.diagnostics
            trace.execution_runtime["asr"] = {
                "adapter_name": trace.transcript.metadata.adapter_name,
                "confidence": trace.transcript.metadata.confidence,
                "diagnostics": diagnostics,
            }
            trace.execution_runtime["transcript_review"] = diagnostics.get(
                "transcript_review",
                {"status": "absent"},
            )
        trace.execution_runtime["privacy_scan"] = {"status": "passed"}

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
                detail=(
                    f"Fixture '{fixture_id}' is preview-only or not selected "
                    "for live-controlled execution"
                ),
            )
        return controlled_task

    def controlled_task_for_execution(
        self,
        payload: CommandPayload,
    ) -> ControlledDemoTask | None:
        if payload.controlled_fixture_id is None:
            return None
        return self.controlled_task_for_mode(
            payload.controlled_fixture_id,
            self.execution_mode_for_payload(payload),
        )

    def controlled_task_for_route(
        self,
        route_decision: RouteDecision | None,
    ) -> ControlledDemoTask | None:
        if route_decision is None:
            return None
        if route_decision.route_type is not RouteType.CONTROLLED_LIVE:
            return None
        if route_decision.controlled_fixture_id is None:
            return None
        return self.controlled_task_for_mode(
            route_decision.controlled_fixture_id,
            route_decision.execution_mode,
        )

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
        route_decision: RouteDecision | None = None,
    ) -> BrowserExecutorAdapter:
        public_target = self.public_readonly_target_for_route(route_decision)
        public_contract = self.public_readonly_contract_for_route(route_decision)
        return BrowserExecutorAdapter(
            BrowserExecutorConfig(
                remote_vision_backend_url=self.config.remote_vision_backend_url,
                local_browser=True,
                dry_run=mode is ExecutionMode.DEMO_PREVIEW,
                execution_mode=mode,
                max_steps=self.public_readonly_max_steps_for_route(route_decision)
                if mode is ExecutionMode.LIVE_PUBLIC_READONLY
                else 8,
                agentic_execution=mode is ExecutionMode.LIVE_CONTROLLED,
                controlled_fixture_id=controlled_task.fixture_id if controlled_task else None,
                controlled_target_ref=controlled_task.target_ref if controlled_task else None,
                controlled_target_url=controlled_task.target_url if controlled_task else None,
                public_target_url=self.public_readonly_target_url_for_route(
                    route_decision,
                    public_target,
                    public_contract,
                ),
                public_target_label=route_decision.public_target_label if route_decision else None,
                public_origin=route_decision.public_origin if route_decision else None,
                public_allowlist_id=route_decision.public_allowlist_id if route_decision else None,
                public_task_contract=public_contract,
                public_task_slots=route_decision.public_task_slots if route_decision else {},
                public_timeout_seconds=self.public_readonly_timeout_seconds_for_route(route_decision),
                public_sanitizer_required=self.config.public_readonly_sanitizer_required,
                public_visual_artifacts_dir=self.config.public_readonly_artifacts_dir,
                public_headed_debug=self.config.public_readonly_headed_debug,
            ),
            agent_factory=self.agent_factory,
        )

    def public_readonly_max_steps_for_route(self, route_decision: RouteDecision | None) -> int:
        if route_decision is None:
            return self.config.public_readonly_max_steps
        max_steps = route_decision.execution_limits.get("max_steps")
        return int(max_steps) if max_steps is not None else self.config.public_readonly_max_steps

    def public_readonly_timeout_seconds_for_route(self, route_decision: RouteDecision | None) -> int:
        if route_decision is None:
            return self.config.public_readonly_timeout_seconds
        timeout_seconds = route_decision.execution_limits.get("timeout_seconds")
        return (
            int(timeout_seconds)
            if timeout_seconds is not None
            else self.config.public_readonly_timeout_seconds
        )

    def public_readonly_target_for_route(
        self,
        route_decision: RouteDecision | None,
    ) -> PublicReadonlyTarget | None:
        if route_decision is None or route_decision.route_type is not RouteType.PUBLIC_READONLY:
            return None
        targets = parse_public_readonly_targets(self.config)
        for target in targets:
            if target.allowlist_id == route_decision.public_allowlist_id:
                return target
        return None

    def public_readonly_contract_for_route(
        self,
        route_decision: RouteDecision | None,
    ) -> PublicTaskContract | None:
        target = self.public_readonly_target_for_route(route_decision)
        if target is None or route_decision is None or not route_decision.public_task_id:
            return None
        for contract in target.task_contracts:
            if contract.task_id == route_decision.public_task_id:
                return contract
        return None

    def public_readonly_target_url_for_route(
        self,
        route_decision: RouteDecision | None,
        public_target: PublicReadonlyTarget | None,
        public_contract: PublicTaskContract | None,
    ) -> str | None:
        if public_contract is None:
            return public_target.url if public_target else None
        if public_contract.target_url_template:
            try:
                return public_contract.target_url_template.format(
                    **_format_public_url_slots(
                        route_decision.public_task_slots if route_decision else {}
                    )
                )
            except KeyError:
                return public_contract.target_url or (public_target.url if public_target else None)
        return public_contract.target_url or (public_target.url if public_target else None)

    def get_trace(self, execution_id: str) -> ExecutionTrace:
        path = self.config.traces_dir / f"{execution_id}.json"
        if not path.exists():
            raise HTTPException(status_code=404, detail="trace not found")
        return self.writer.read(execution_id)

    def trace_response(self, trace: ExecutionTrace) -> dict[str, Any]:
        payload = sanitize_trace_dict(trace.model_dump(mode="json"))
        payload["status_voice"] = self.voice_feedback.render_status(
            status=trace.final_status.value,
            reason=trace.stop_reason or trace.failure_reason,
        )
        return payload

    def visual_artifact_for_trace(
        self,
        trace: ExecutionTrace,
        artifact_id: str,
    ) -> dict[str, Any]:
        artifacts = trace.execution_runtime.get("public_visual_artifacts") or []
        if not isinstance(artifacts, list):
            raise HTTPException(status_code=404, detail="visual artifact not found")
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            if artifact.get("artifact_id") == artifact_id and artifact.get("execution_id") == trace.execution_id:
                return artifact
        raise HTTPException(status_code=404, detail="visual artifact not found")

    def resolve_visual_artifact_path(self, artifact: dict[str, Any]) -> Path:
        local_ref = str(artifact.get("local_ref") or "")
        local_path = Path(local_ref)
        if not local_ref or local_path.is_absolute() or ".." in local_path.parts:
            raise HTTPException(status_code=404, detail="visual artifact not found")
        execution_id = str(artifact.get("execution_id") or "")
        expected_prefix = ("artifacts", "public-readonly", execution_id)
        if not execution_id or local_path.parts[:3] != expected_prefix or len(local_path.parts) < 4:
            raise HTTPException(status_code=404, detail="visual artifact not found")
        runtime_root = self.config.runtime_dir.resolve()
        artifact_path = (runtime_root / local_path).resolve()
        try:
            artifact_path.relative_to(runtime_root)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="visual artifact not found") from exc
        return artifact_path


def _format_public_url_slots(slots: dict[str, Any]) -> dict[str, str]:
    formatted: dict[str, str] = {}
    for key, value in slots.items():
        text = str(value)
        if key == "search_query":
            formatted[key] = quote_plus(text)
        elif key in {"owner", "repo"}:
            formatted[key] = quote(text, safe="")
        else:
            formatted[key] = text
    return formatted


app = create_app()
