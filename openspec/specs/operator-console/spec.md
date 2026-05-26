# operator-console Specification

## Purpose
TBD - created by archiving change voice-browser-agent. Update Purpose after archive.
## Requirements
### Requirement: Provide a minimal operator console
The system SHALL provide a web Operator Console for running and inspecting Spoken Command Executions.

#### Scenario: Operator opens console
- **WHEN** the operator opens the application UI
- **THEN** the console shows controls for audio upload, optional browser recording, execution start, and trace inspection

### Requirement: Display command interpretation
The Operator Console SHALL display the ASR transcript and normalized output before or during execution.

#### Scenario: Normalization succeeds
- **WHEN** a Browser Task Request is produced
- **THEN** the console displays the transcript, request fields, validator decision, and confirmation requirement

#### Scenario: Clarification is required
- **WHEN** a Clarification Request is produced
- **THEN** the console displays the clarification question and does not start browser execution

### Requirement: Display execution progress
The Operator Console SHALL display execution status, timeline events, screenshots or screenshot references, and final browser state.

#### Scenario: Browser action is recorded
- **WHEN** the browser executor performs an action
- **THEN** the console updates the execution timeline with the action and related trace evidence

### Requirement: Support confirmation decisions
The Operator Console SHALL let the operator confirm or cancel a pending Confirmation Gate.

#### Scenario: Sensitive action is paused
- **WHEN** execution pauses at a Confirmation Gate
- **THEN** the console shows the reason and provides confirm and cancel actions

### Requirement: Provide optional status voice feedback
The Operator Console SHALL support optional Status Voice Feedback for confirmations, final status, and failure explanations.

#### Scenario: Status voice feedback is enabled
- **WHEN** execution reaches a confirmation prompt, success state, failure state, or stopped state
- **THEN** the system can play spoken feedback describing the status

### Requirement: Avoid exposing private artifacts by default
The Operator Console SHALL avoid marking raw recordings, live website traces, secrets, or browser state as public artifacts.

#### Scenario: Trace is exported
- **WHEN** the operator exports a trace intended for public documentation
- **THEN** the exported artifact is sanitized or explicitly marked as private/local

### Requirement: Display execution mode
The Operator Console SHALL show whether an execution is running in demo-preview mode or live-controlled mode.

#### Scenario: Preview execution is displayed
- **WHEN** a fixture execution returns a demo-preview trace
- **THEN** the console labels the execution as preview and does not imply live browser execution occurred

#### Scenario: Live controlled execution is displayed
- **WHEN** a fixture execution runs in live-controlled mode
- **THEN** the console labels the execution as live controlled and shows the live final status

### Requirement: Display live controlled evidence timeline
The Operator Console SHALL display live controlled browser action events and grounding evidence references from the trace.

#### Scenario: Live browser action is recorded
- **WHEN** a live controlled trace includes a browser action event
- **THEN** the console timeline displays the action description, screenshot reference if present, grounding evidence references, and final status

#### Scenario: Live controlled run stops or fails
- **WHEN** a live controlled run stops or fails
- **THEN** the console displays the stop reason or failure reason alongside the timeline

### Requirement: Keep public export state explicit
The Operator Console SHALL make sanitized export state explicit for live controlled traces.

#### Scenario: Operator exports live controlled trace
- **WHEN** the operator exports a live controlled trace for public documentation
- **THEN** the console returns the sanitized export and does not expose raw runtime trace fields

