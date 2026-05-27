# operator-console Specification

## Purpose
Defines the local Operator Console surfaces for spoken command input, fixture replay, normalization visibility, confirmation decisions, execution timelines, status feedback, and sanitized trace inspection/export.
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

### Requirement: Display agentic step timeline
The Operator Console SHALL display agentic vision execution steps as an inspectable timeline.

#### Scenario: Agentic trace is rendered
- **WHEN** a trace contains agentic execution steps
- **THEN** the console shows each step's observation summary, selected action, action result, verification decision, recovery or stop decision, and final status

### Requirement: Show visual grounding evidence references
The Operator Console SHALL show sanitized visual grounding evidence references for agentic steps.

#### Scenario: Step has grounding references
- **WHEN** an agentic step includes grounding evidence references or a sanitized screenshot reference
- **THEN** the console displays those references without exposing raw screenshots, browser profile data, cookies, credentials, private URLs, or remote host details

### Requirement: Surface agentic recovery and stop decisions
The Operator Console SHALL make recovery, clarification, confirmation, failed verification, and stop reasons visible for agentic execution.

#### Scenario: Step stops after failed verification
- **WHEN** an agentic step fails verification and the execution stops
- **THEN** the console displays the failed verification reason and final stop or failure reason next to the step timeline

#### Scenario: Step triggers safety confirmation
- **WHEN** an agentic step observes a sensitive state that requires confirmation
- **THEN** the console displays the confirmation reason and does not present the execution as complete

### Requirement: Export sanitized agentic traces
The Operator Console SHALL export agentic traces through the same sanitized artifact boundary as existing traces.

#### Scenario: Operator exports agentic trace
- **WHEN** the operator exports a trace containing agentic steps
- **THEN** the exported payload includes sanitized step summaries and evidence references while excluding raw screenshots, raw audio, private browser state, credentials, cookies, private URLs, and remote host details

### Requirement: Gate optional status voice playback
The Operator Console SHALL play Status Voice Feedback only when feedback is enabled and browser speech synthesis is available.

#### Scenario: Status voice feedback is enabled
- **WHEN** an execution response includes enabled Status Voice Feedback
- **THEN** the console requests browser-native speech playback for the status, confirmation, stop, or failure text

#### Scenario: Status voice feedback is disabled
- **WHEN** an execution response includes disabled Status Voice Feedback
- **THEN** the console does not request spoken playback and continues to display the textual status

#### Scenario: Browser speech synthesis is unavailable
- **WHEN** Status Voice Feedback is enabled but the browser has no speech synthesis capability
- **THEN** the console silently keeps textual feedback without creating raw audio artifacts

### Requirement: Distinguish execution input sources
The Operator Console SHALL present transcript execution, fixture replay, and uploaded or recorded audio execution as distinct user actions.

#### Scenario: Operator runs transcript text
- **WHEN** the operator enters text and activates transcript execution
- **THEN** the console sends the transcript text to the execution API and labels the result as transcript-based execution

#### Scenario: Operator runs selected fixture
- **WHEN** the operator selects a fixture and activates fixture replay
- **THEN** the console sends the fixture id and selected execution mode to the fixture execution API and labels the result as fixture-based execution

#### Scenario: Operator runs uploaded audio
- **WHEN** the operator has uploaded or recorded one audio clip and activates audio execution
- **THEN** the console sends the stored audio id to the execution API and labels the result as audio-based execution

### Requirement: Show fixture mode support
The Operator Console SHALL show which execution modes are supported by each demo fixture.

#### Scenario: Fixture supports live-controlled mode
- **WHEN** the operator selects a fixture that is selected for live-controlled execution
- **THEN** the console allows live-controlled mode and displays that the task runs against a controlled local page

#### Scenario: Fixture is preview-only
- **WHEN** the operator selects a fixture that is not selected for live-controlled execution
- **THEN** the console prevents or explains live-controlled selection and keeps demo-preview mode available

### Requirement: Summarize execution evidence
The Operator Console SHALL display a compact execution summary before or alongside the raw trace JSON.

#### Scenario: Execution completes or stops
- **WHEN** an execution response is rendered
- **THEN** the console shows input source, execution mode, final status, stop reason, failure reason, clarification reason, or confirmation state when present

#### Scenario: Timeline contains mixed evidence
- **WHEN** a trace contains agentic steps, browser actions, confirmation state, or clarification state
- **THEN** the timeline labels those evidence types separately so the operator can distinguish preview stops, live actions, agentic verification, clarification, and confirmation prompts
