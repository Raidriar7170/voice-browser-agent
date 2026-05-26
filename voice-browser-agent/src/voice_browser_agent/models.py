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


class BrowserActionEvent(BaseModel):
    action_type: str
    description: str
    screenshot_ref: str | None = None
    grounding_evidence_refs: list[str] = Field(default_factory=list)
    browser_state: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class BrowserStateStop(BaseModel):
    reason: str
    detail: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class ExecutionTrace(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"exec-{uuid4().hex[:12]}")
    transcript: ASRTranscript | None = None
    normalized_output: NormalizedOutput | None = None
    validator_decision: ValidationResult | None = None
    confirmation_decision: ConfirmationDecision | None = None
    browser_actions: list[BrowserActionEvent] = Field(default_factory=list)
    grounding_evidence_refs: list[str] = Field(default_factory=list)
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
