from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BrowserIntentType(str, Enum):
    SEARCH_OPEN = "search_open"
    CLICK_VISUAL_TARGET = "click_visual_target"
    FILL_FORM = "fill_form"
    SELECT_FILTER_OR_OPTION = "select_filter_or_option"
    EXTRACT_COMPARE_VISIBLE_INFO = "extract_compare_visible_info"


class ConfirmationState(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class EvidencePrivacyState(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    LOCAL_PRIVATE = "local_private"
    PUBLIC_SAFE = "public_safe"


class SanitizerStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class ExecutionMode(str, Enum):
    DEMO_PREVIEW = "demo_preview"
    LIVE_CONTROLLED = "live_controlled"
    LIVE_PUBLIC_READONLY = "live_public_readonly"


class RouteType(str, Enum):
    CONTROLLED_LIVE = "controlled_live"
    PUBLIC_READONLY = "public_readonly"
    DEMO_PREVIEW = "demo_preview"
    CLARIFICATION = "clarification"
    BLOCKED = "blocked"
    CONFIRMATION_REQUIRED = "confirmation_required"


class ExecutionStatus(str, Enum):
    CREATED = "created"
    CLARIFICATION_REQUIRED = "clarification_required"
    PENDING_CONFIRMATION = "pending_confirmation"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STOPPED = "stopped"
    BLOCKED = "blocked"


class PublicTaskCompletionState(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    STOPPED = "stopped"
    FAILED = "failed"
    BLOCKED = "blocked"


class VisualReference(BaseModel):
    kind: str
    text: str
    source: str = "transcript"
    confidence: float | None = Field(default=None, ge=0, le=1)


class SpokenCommandInput(BaseModel):
    source_type: Literal["upload", "recording", "fixture"]
    audio_id: str
    content_type: str
    size_bytes: int = Field(ge=0)
    storage_path: Path | None = Field(default=None, exclude=True)
    created_at: datetime = Field(default_factory=utc_now)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ASRTranscriptMetadata(BaseModel):
    adapter_name: str
    input_audio_id: str
    language_mode: str = "zh-first"
    created_at: datetime = Field(default_factory=utc_now)
    confidence: float | None = Field(default=None, ge=0, le=1)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class ASRTranscript(BaseModel):
    text: str
    metadata: ASRTranscriptMetadata


class BrowserTaskRequest(BaseModel):
    kind: Literal["browser_task_request"] = "browser_task_request"
    task: str
    intent_type: BrowserIntentType
    constraints: list[str]
    visual_references: list[VisualReference] = Field(default_factory=list)
    requires_confirmation: bool
    stop_conditions: list[str]
    safety_flags: list[str] = Field(default_factory=list)
    controlled_target_ref: str | None = None
    public_task_slots: dict[str, Any] = Field(default_factory=dict)


class ClarificationRequest(BaseModel):
    kind: Literal["clarification_request"] = "clarification_request"
    question: str
    reason: str
    transcript_text: str


NormalizedOutput = BrowserTaskRequest | ClarificationRequest


class ValidationResult(BaseModel):
    accepted: bool
    reason: str
    issues: list[str] = Field(default_factory=list)
    requires_confirmation: bool = False


class ConfirmationDecision(BaseModel):
    state: ConfirmationState
    reason: str
    decided_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class RouteDecision(BaseModel):
    route_type: RouteType
    execution_mode: ExecutionMode
    evidence_mode: str
    controlled_fixture_id: str | None = None
    controlled_target_ref: str | None = None
    public_target_label: str | None = None
    public_origin: str | None = None
    public_allowlist_id: str | None = None
    public_task_id: str | None = None
    public_task_kind: str | None = None
    public_task_slots: dict[str, Any] = Field(default_factory=dict)
    public_completion_criteria_id: str | None = None
    public_completion_state: PublicTaskCompletionState | None = None
    public_observed_proof_summary: dict[str, Any] = Field(default_factory=dict)
    public_unmet_criteria: list[str] = Field(default_factory=list)
    evidence_privacy_state: EvidencePrivacyState = EvidencePrivacyState.NOT_APPLICABLE
    sanitizer_status: SanitizerStatus = SanitizerStatus.NOT_REQUIRED
    execution_limits: dict[str, Any] = Field(default_factory=dict)
    route_reason: str
    user_message: str
    live_evidence_eligible: bool = False
    public_readonly_enabled: bool = False


class PublicTaskCompletionCriteria(BaseModel):
    criteria_id: str
    required_proof: list[str] = Field(default_factory=list)
    visible_markers: list[str] = Field(default_factory=list)
    url_path_contains: str | None = None
    title_contains: str | None = None


class PublicTaskContract(BaseModel):
    task_id: str
    task_kind: str
    allowlist_id: str
    target_url: str | None = None
    target_url_template: str | None = None
    allowed_actions: list[str] = Field(default_factory=list)
    slots: list[str] = Field(default_factory=list)
    completion_criteria: PublicTaskCompletionCriteria
    max_steps: int = Field(default=3, ge=1, le=5)
    timeout_seconds: int = Field(default=15, ge=1, le=60)
    privacy_policy: str = "local_private"


class PublicTaskCompletionResult(BaseModel):
    completion_state: PublicTaskCompletionState
    observed_proof: dict[str, Any] = Field(default_factory=dict)
    unmet_criteria: list[str] = Field(default_factory=list)
    stop_reason: str | None = None
    failure_reason: str | None = None


class BrowserActionEvent(BaseModel):
    action_type: str
    description: str
    screenshot_ref: str | None = None
    grounding_evidence_refs: list[str] = Field(default_factory=list)
    browser_state: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class AgenticActionResult(BaseModel):
    status: Literal["succeeded", "failed", "no_effect"]
    description: str
    browser_state: dict[str, Any] = Field(default_factory=dict)


class AgenticVerificationDecision(BaseModel):
    passed: bool
    reason: str


class AgenticRecoveryDecision(BaseModel):
    kind: Literal["none", "reobserve", "stop", "clarify"]
    reason: str


class AgenticVisionStep(BaseModel):
    step_index: int = Field(ge=1)
    observation_summary: str
    target_status: Literal["resolved", "missing", "ambiguous", "stale", "sensitive"]
    selected_target_ref: str | None = None
    target_candidates: list[str] = Field(default_factory=list)
    grounding_evidence_refs: list[str] = Field(default_factory=list)
    screenshot_ref: str | None = None
    selected_action: str | None = None
    action_result: AgenticActionResult | None = None
    verification_decision: AgenticVerificationDecision = Field(
        default_factory=lambda: AgenticVerificationDecision(
            passed=False,
            reason="not verified",
        )
    )
    recovery_decision: AgenticRecoveryDecision = Field(
        default_factory=lambda: AgenticRecoveryDecision(
            kind="none",
            reason="no recovery needed",
        )
    )


class BrowserStateStop(BaseModel):
    reason: str
    detail: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class ExecutionTrace(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"exec-{uuid4().hex[:12]}")
    execution_mode: ExecutionMode | None = None
    transcript: ASRTranscript | None = None
    normalized_output: NormalizedOutput | None = None
    validator_decision: ValidationResult | None = None
    confirmation_decision: ConfirmationDecision | None = None
    route_decision: RouteDecision | None = None
    browser_actions: list[BrowserActionEvent] = Field(default_factory=list)
    agentic_steps: list[AgenticVisionStep] = Field(default_factory=list)
    grounding_evidence_refs: list[str] = Field(default_factory=list)
    execution_runtime: dict[str, Any] = Field(default_factory=dict)
    evidence_privacy_state: EvidencePrivacyState = EvidencePrivacyState.NOT_APPLICABLE
    sanitizer_status: SanitizerStatus = SanitizerStatus.NOT_REQUIRED
    final_status: ExecutionStatus = ExecutionStatus.CREATED
    failure_reason: str | None = None
    stop_reason: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def add_browser_action(
        self,
        action_type: str,
        description: str,
        screenshot_ref: str | None = None,
        grounding_evidence_refs: list[str] | None = None,
    ) -> BrowserActionEvent:
        action = BrowserActionEvent(
            action_type=action_type,
            description=description,
            screenshot_ref=screenshot_ref,
            grounding_evidence_refs=grounding_evidence_refs or [],
        )
        self.browser_actions.append(action)
        self.grounding_evidence_refs.extend(action.grounding_evidence_refs)
        self.touch()
        return action
