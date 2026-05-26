## ADDED Requirements

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
