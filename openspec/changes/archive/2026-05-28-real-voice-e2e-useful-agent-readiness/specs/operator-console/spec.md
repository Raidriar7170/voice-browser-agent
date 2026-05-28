## ADDED Requirements

### Requirement: Display real-use readiness in the console
The Operator Console SHALL show whether the local environment is ready for real audio execution before the operator runs an uploaded or recorded command.

#### Scenario: Console loads readiness
- **WHEN** the Operator Console loads
- **THEN** it displays ASR readiness, browser automation readiness, real visual grounding readiness, runtime privacy status, and any missing setup action in a compact status area

### Requirement: Support transcript review for audio execution
The Operator Console SHALL let the operator review and edit ASR transcript text before normalization and execution of an uploaded or recorded audio command.

#### Scenario: Audio transcript is reviewed before execution
- **WHEN** an uploaded or recorded audio command is transcribed
- **THEN** the console displays the ASR transcript, adapter metadata, confidence or diagnostics when available, an editable transcript field, and separate controls for normalize-preview and execute

#### Scenario: Edited transcript is executed
- **WHEN** the operator edits the transcript and starts execution
- **THEN** the console sends both the audio id and edited transcript text or correction metadata so the resulting trace identifies the run as audio-based with transcript review provenance

### Requirement: Surface real-use failure states
The Operator Console SHALL make real-use failures visible without presenting them as successful executions.

#### Scenario: ASR unavailable in console
- **WHEN** audio execution cannot proceed because ASR is unavailable
- **THEN** the console displays the unavailable-ASR reason, keeps the execution result out of the success state, and points the operator to preflight setup guidance
