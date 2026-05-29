from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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


class NormalizerProvenance(BaseModel):
    provider_mode: str = "rule"
    provider_name: str = "rule-based"
    output_source: str = "rule"
    prompt_schema_version: str = "structured-normalizer.v1"
    output_kind: str | None = None
    schema_status: Literal["passed", "failed", "not_applicable"] = "not_applicable"
    fallback_reason: str | None = None


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
    public_target_class: str | None = None
    public_origin: str | None = None
    public_allowlist_id: str | None = None
    public_task_id: str | None = None
    public_task_kind: str | None = None
    public_task_category: str | None = None
    public_task_slots: dict[str, Any] = Field(default_factory=dict)
    public_completion_criteria_id: str | None = None
    public_completion_criteria_summary: list[str] = Field(default_factory=list)
    public_completion_state: PublicTaskCompletionState | None = None
    public_observed_proof_summary: dict[str, Any] = Field(default_factory=dict)
    public_unmet_criteria: list[str] = Field(default_factory=list)
    public_matrix_eligible: bool = False
    public_evidence_export_state: str = "not_applicable"
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

    @field_validator("required_proof")
    @classmethod
    def _require_task_specific_proof(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("required proof must include task-specific completion criteria")
        return value


class PublicTaskContract(BaseModel):
    task_id: str
    task_kind: str
    allowlist_id: str
    target_class: str | None = None
    task_category: str | None = None
    target_url: str | None = None
    target_url_template: str | None = None
    allowed_actions: list[str] = Field(default_factory=list)
    slots: list[str] = Field(default_factory=list)
    completion_criteria: PublicTaskCompletionCriteria
    max_steps: int = Field(default=3, ge=1, le=5)
    timeout_seconds: int = Field(default=15, ge=1, le=60)
    privacy_policy: str = "local_private"


class PublicReadonlyReliabilityAttemptEvidence(BaseModel):
    outcome: PublicTaskCompletionState
    final_status: ExecutionStatus
    observed_proof_summary: dict[str, Any] = Field(default_factory=dict)
    unmet_criteria: list[str] = Field(default_factory=list)
    stop_or_failure_reason: str | None = None
    evidence_privacy_state: EvidencePrivacyState = EvidencePrivacyState.LOCAL_PRIVATE
    sanitizer_status: SanitizerStatus = SanitizerStatus.PENDING
    visible_result_state: str = "not_captured"
    export_state: str = "local_private"
    regression_coverage: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_attempt_shape(self) -> "PublicReadonlyReliabilityAttemptEvidence":
        if self.outcome is PublicTaskCompletionState.COMPLETED:
            if not self.observed_proof_summary:
                raise ValueError("completed attempt evidence requires observed proof")
            if self.unmet_criteria:
                raise ValueError("completed attempt evidence cannot include unmet criteria")
            return self
        if not self.unmet_criteria and not self.stop_or_failure_reason:
            raise ValueError(
                "incomplete attempt evidence requires unmet criteria or stop/failure reason"
            )
        return self


class PublicReadonlyReliabilitySmokeTask(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="id")
    target_label: str
    target_class: str
    allowlist_id: str
    task_kind: str
    safe_slots: list[str] = Field(min_length=1)
    target_url: str | None = None
    target_url_template: str | None = Field(default=None, alias="url_template")
    allowed_actions: list[str] = Field(min_length=1)
    requested_slots: dict[str, Any] = Field(default_factory=dict)
    visual_artifact_policy: str | None = None
    completion_criteria: PublicTaskCompletionCriteria
    limits: dict[str, int]
    privacy_policy: str = "local_private"
    expected_matrix_coverage: PublicTaskCompletionState
    reliability_attempt_evidence: PublicReadonlyReliabilityAttemptEvidence
    regression_coverage: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_target_and_limits(self) -> "PublicReadonlyReliabilitySmokeTask":
        if not self.target_url and not self.target_url_template:
            raise ValueError("target URL or template is required")
        max_steps = self.limits.get("max_steps")
        timeout_seconds = self.limits.get("timeout_seconds")
        if max_steps is None or max_steps < 1 or max_steps > 5:
            raise ValueError("limits.max_steps must be between 1 and 5")
        if timeout_seconds is None or timeout_seconds < 1 or timeout_seconds > 60:
            raise ValueError("limits.timeout_seconds must be between 1 and 60")
        return self


class PublicReadonlyReliabilitySmokeSet(BaseModel):
    tasks: list[PublicReadonlyReliabilitySmokeTask] = Field(min_length=5, max_length=8)
    boundaries: list[str] = Field(default_factory=list)


USEFUL_TASK_PACK_REQUIRED_CATEGORIES = (
    "documentation",
    "reference",
    "package_metadata",
    "release_notes",
    "public_repository_search",
    "public_repository_read",
)


class PublicReadonlyUsefulTask(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="id")
    target_label: str
    target_class: str
    task_category: str
    allowlist_id: str
    browser_intent_type: str | None = None
    task_kind: str
    safe_slots: list[str] = Field(min_length=1)
    target_url: str | None = None
    target_url_template: str | None = Field(default=None, alias="url_template")
    allowed_actions: list[str] = Field(min_length=1)
    command: str | None = None
    requested_slots: dict[str, Any] = Field(default_factory=dict)
    completion_criteria: PublicTaskCompletionCriteria
    execution_mode: ExecutionMode = ExecutionMode.LIVE_PUBLIC_READONLY
    limits: dict[str, int]
    privacy_policy: str = "local_private"
    expected_task_pack_coverage: PublicTaskCompletionState
    task_pack_attempt_evidence: PublicReadonlyReliabilityAttemptEvidence
    regression_coverage: list[str] = Field(default_factory=list)
    safety_boundaries: list[str] = Field(default_factory=list)
    artifact_status: str = "local_private_until_sanitized"

    @model_validator(mode="after")
    def _validate_target_and_limits(self) -> "PublicReadonlyUsefulTask":
        if not self.target_url and not self.target_url_template:
            raise ValueError("target URL or template is required")
        max_steps = self.limits.get("max_steps")
        timeout_seconds = self.limits.get("timeout_seconds")
        if max_steps is None or max_steps < 1 or max_steps > 5:
            raise ValueError("limits.max_steps must be between 1 and 5")
        if timeout_seconds is None or timeout_seconds < 1 or timeout_seconds > 60:
            raise ValueError("limits.timeout_seconds must be between 1 and 60")
        return self


class PublicReadonlyUsefulTaskPack(BaseModel):
    tasks: list[PublicReadonlyUsefulTask] = Field(min_length=8, max_length=12)
    required_categories: list[str] = Field(
        default_factory=lambda: list(USEFUL_TASK_PACK_REQUIRED_CATEGORIES)
    )
    boundaries: list[str] = Field(default_factory=list)

    @property
    def category_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for task in self.tasks:
            counts[task.task_category] = counts.get(task.task_category, 0) + 1
        return counts


class PublicReadonlyReliabilityMatrixRow(BaseModel):
    task_id: str
    target_label: str
    target_class: str
    task_kind: str
    completion_criteria_id: str
    completion_criteria_summary: list[str] = Field(default_factory=list)
    outcome: PublicTaskCompletionState
    final_status: str
    observed_proof_summary: dict[str, Any] = Field(default_factory=dict)
    unmet_criteria: list[str] = Field(default_factory=list)
    stop_or_failure_reason: str | None = None
    evidence_privacy_state: EvidencePrivacyState
    sanitizer_status: SanitizerStatus
    visible_result_state: str
    export_state: str
    regression_coverage: list[str] = Field(default_factory=list)


class PublicReadonlyReliabilityMatrixSummary(BaseModel):
    task_count: int
    outcome_counts: dict[str, int]
    missing_outcomes: list[str] = Field(default_factory=list)
    is_complete: bool
    public_ready: bool
    rows: list[PublicReadonlyReliabilityMatrixRow] = Field(default_factory=list)


class PublicTaskCompletionResult(BaseModel):
    completion_state: PublicTaskCompletionState
    observed_proof: dict[str, Any] = Field(default_factory=dict)
    unmet_criteria: list[str] = Field(default_factory=list)
    stop_reason: str | None = None
    failure_reason: str | None = None


class PublicReadonlyVisualArtifact(BaseModel):
    artifact_id: str
    execution_id: str
    artifact_kind: Literal["step_screenshot", "final_screenshot", "blocked_screenshot"]
    action_label: str
    local_ref: str
    media_type: str = "image/png"
    page_title: str | None = None
    sanitized_origin: str | None = None
    completion_state: PublicTaskCompletionState
    privacy_state: EvidencePrivacyState = EvidencePrivacyState.LOCAL_PRIVATE
    sanitizer_status: SanitizerStatus = SanitizerStatus.PENDING
    step_index: int | None = None
    is_final: bool = False


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


class VisualVerificationResult(BaseModel):
    outcome: Literal["passed", "failed", "uncertain"]
    expected_condition: str
    observed_state_summary: str
    reason: str
    verifier_mode: str = "deterministic_controlled"
    provider_mode: str | None = None
    sanitized_evidence_refs: list[str] = Field(default_factory=list)
    provider_metadata: dict[str, Any] = Field(default_factory=dict)


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
    visual_verification_result: VisualVerificationResult | None = None
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
    normalizer_provenance: NormalizerProvenance | None = None
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
