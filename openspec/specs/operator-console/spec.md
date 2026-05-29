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

### Requirement: Provide command-first operator workflow
The Operator Console SHALL provide a primary command-first workflow that can be used without selecting fixture or execution-mode dropdowns.

#### Scenario: Operator runs typed command
- **WHEN** the operator enters a transcript command and activates the primary run action
- **THEN** the console sends the command through normalization, route selection, validation, confirmation handling, and execution or preview according to the route decision

#### Scenario: Operator runs reviewed audio command
- **WHEN** the operator reviews or edits an uploaded or recorded audio transcript and activates the primary run action
- **THEN** the console sends the reviewed transcript and audio id through the same route-selection and execution flow while preserving ASR provenance

### Requirement: Present advanced controls separately
The Operator Console SHALL keep fixture replay, execution-mode override, raw trace JSON, and sanitized export controls available as advanced or inspectable controls outside the primary workflow.

#### Scenario: Operator needs fixture replay
- **WHEN** the operator opens advanced replay controls
- **THEN** fixture selection and execution-mode override are available without dominating the default command-first flow

#### Scenario: Operator inspects raw trace
- **WHEN** an execution response has been rendered
- **THEN** the console provides access to raw trace JSON and sanitized export without exposing raw private artifacts by default

### Requirement: Display route and evidence summary
The Operator Console SHALL display route decision, execution mode, evidence mode, final status, browser state, and stop or failure reason in a compact result area.

#### Scenario: Controlled live run succeeds
- **WHEN** route selection executes a controlled live task successfully
- **THEN** the console displays the selected route, controlled target, page title or final browser state, browser action evidence, grounding references, and final status as live controlled evidence

#### Scenario: Preview-only run is rendered
- **WHEN** route selection keeps a command in demo-preview mode
- **THEN** the console clearly labels the result as preview-only and explains that no live browser action was executed

#### Scenario: Run fails or stops
- **WHEN** execution fails, stops, or requires confirmation or clarification
- **THEN** the console displays the reason near the result summary and does not visually present the run as successful

### Requirement: Improve operator-console visual quality
The Operator Console SHALL use a polished, responsive, accessible tool layout appropriate for repeated operator use.

#### Scenario: Console opens on desktop
- **WHEN** the operator opens the console on a desktop viewport
- **THEN** the primary command input, readiness, route decision, and execution evidence are visible with stable layout, readable hierarchy, and no overlapping controls

#### Scenario: Console opens on mobile-width viewport
- **WHEN** the operator opens the console on a narrow viewport
- **THEN** controls and result panels remain usable without text clipping, incoherent overlap, or layout shifts caused by dynamic status content

### Requirement: Display public-readonly readiness and policy state
The Operator Console SHALL display public-readonly availability, allowlist status, and private-trace policy before the operator runs a public command.

#### Scenario: Console loads readiness
- **WHEN** the Operator Console loads readiness information
- **THEN** it shows whether public-readonly execution is enabled, disabled, missing allowlist configuration, or unavailable due to browser/sanitizer prerequisites

#### Scenario: Public-readonly is disabled
- **WHEN** public-readonly execution is disabled
- **THEN** the console labels public commands as controlled-showcase, demo-preview, or unsupported rather than live public webpage operation

### Requirement: Render public-readonly route results distinctly
The Operator Console SHALL distinguish public-readonly evidence from controlled live, demo-preview, real voice, real vision, and failure evidence.

#### Scenario: Public-readonly route is selected
- **WHEN** an execution response includes a public-readonly route decision
- **THEN** the console displays target label, sanitized origin, allowlist id, private evidence state, execution limits, final status, and route reason

#### Scenario: Public-readonly route is rejected
- **WHEN** route selection rejects public-readonly execution
- **THEN** the console displays the unsupported-route or safety reason near the command result

### Requirement: Gate public-readonly export controls
The Operator Console SHALL prevent public-readonly traces from appearing as public-ready unless sanitizer checks explicitly pass.

#### Scenario: Operator exports public-readonly trace
- **WHEN** an operator requests sanitized export for a public-readonly trace
- **THEN** the console reports whether the export is public-safe or local-private and does not hide sanitizer failures

#### Scenario: Sanitizer has not approved trace
- **WHEN** a public-readonly trace has no public-safe sanitizer result
- **THEN** the console keeps the trace marked local/private and avoids presenting it as publishable evidence

### Requirement: Display public task plan and completion state
The Operator Console SHALL show public-readonly task plan and completion evidence distinctly from simple page-open evidence.

#### Scenario: Public task route is selected
- **WHEN** an execution response includes a public-readonly task route
- **THEN** the console displays task id, task kind, target label, sanitized origin, allowed action summary, completion criteria summary, execution limits, private evidence state, and route reason

#### Scenario: Public task finishes
- **WHEN** a public-readonly task completes, partially completes, stops, fails, or is blocked
- **THEN** the console displays completion state, final status, observed proof summary, stop or failure reason, and whether the trace remains local/private

### Requirement: Avoid misleading public task success styling
The Operator Console SHALL NOT present real public task attempts as successful unless completion criteria are satisfied.

#### Scenario: Page opens but task is incomplete
- **WHEN** a public task opens an allowlisted page but completion verification fails or remains partial
- **THEN** the console labels the run as incomplete, stopped, or failed rather than successful live public task execution

#### Scenario: Public task is blocked before navigation
- **WHEN** a public command is rejected by route, policy, validation, confirmation, or task-contract checks before navigation
- **THEN** the console displays the block reason without showing public webpage operation evidence

### Requirement: Surface public task privacy and export status
The Operator Console SHALL keep real public task traces local/private unless sanitizer approval is explicit.

#### Scenario: Operator requests public task export
- **WHEN** an operator exports a public task trace
- **THEN** the console reports whether the export is public-safe, local/private, or sanitizer-failed and shows the reason without exposing raw public page data

#### Scenario: Sanitizer approval is absent
- **WHEN** a public task trace has no public-safe sanitizer status
- **THEN** the console keeps the trace marked local/private and avoids presenting it as publishable evidence

### Requirement: Display visible result for real public tasks
The Operator Console SHALL display a visible result panel for real public-readonly task attempts when local/private visual artifacts are available.

#### Scenario: Public task visual result is available
- **WHEN** an execution response includes public-readonly visual artifact metadata
- **THEN** the console displays the final screenshot preview, page title, target label, sanitized origin, completion state, privacy state, and sanitizer status near the route and evidence panels

#### Scenario: Public task step screenshots are available
- **WHEN** an execution response includes multiple public-readonly step artifact references
- **THEN** the console displays a compact step timeline that lets the operator inspect navigation, search, read, and stop states without opening raw trace JSON

### Requirement: Display GitHub block states visibly
The Operator Console SHALL show GitHub public-readonly block states as visible outcomes rather than successful execution.

#### Scenario: GitHub captcha or verification blocks execution
- **WHEN** a GitHub public-readonly task stops on captcha, verification, abuse detection, or similar blocking state
- **THEN** the console displays the blocking screenshot or visual summary, stop reason, local/private privacy state, and non-completed task state

#### Scenario: GitHub login or rate-limit boundary blocks execution
- **WHEN** a GitHub public-readonly task reaches login, permission, private repository, rate-limit, or access-denied UI
- **THEN** the console displays the boundary reason and does not style the run as completed or successful public automation

### Requirement: Keep visual result UI privacy-aware
The Operator Console SHALL make local/private status visible whenever it displays real public webpage artifacts.

#### Scenario: Visual artifact is local/private
- **WHEN** the console renders a public-readonly screenshot or visual result
- **THEN** it labels the artifact as local/private and shows sanitizer status without offering it as public-ready evidence

#### Scenario: Visual artifact is unavailable
- **WHEN** no visual artifact is available for a public-readonly run
- **THEN** the console falls back to completion proof and trace evidence while explicitly saying that no visual result was captured

### Requirement: Display public-readonly reliability matrix status
The Operator Console SHALL display public-readonly reliability-matrix fields for public task attempts.

#### Scenario: Reliability task route is rendered
- **WHEN** an execution response includes a public-readonly reliability task route
- **THEN** the console displays task id, task kind, target class, target label, completion criteria summary, route reason, execution limits, evidence privacy state, and sanitizer status

#### Scenario: Reliability task finishes
- **WHEN** a public-readonly reliability task completes, partially completes, stops, fails, or is blocked
- **THEN** the console displays outcome classification, final status, observed proof summary, unmet criteria, stop or failure reason, visible result state, and export status near the primary result summary

### Requirement: Avoid misleading reliability success styling
The Operator Console SHALL style public-readonly reliability outcomes according to completion verification rather than page-open or action-count evidence.

#### Scenario: Opened page is incomplete
- **WHEN** a public-readonly reliability task opens a page but completion proof is missing
- **THEN** the console labels the run as partial, stopped, or failed and does not present it as successful public automation

#### Scenario: Task is blocked before navigation
- **WHEN** a reliability task is blocked before public navigation
- **THEN** the console displays the block reason without showing public webpage operation evidence

### Requirement: Surface reliability privacy and export state
The Operator Console SHALL keep reliability evidence privacy state visible whenever public-readonly artifacts are shown.

#### Scenario: Local/private artifact is displayed
- **WHEN** the console displays a public-readonly screenshot, visual result, proof summary, or trace reference
- **THEN** it labels the artifact as local/private or public-safe according to sanitizer status and does not offer it as public-ready evidence unless approved

#### Scenario: Sanitized export is requested
- **WHEN** the operator requests export for a public-readonly reliability task
- **THEN** the console reports public-safe, local/private, sanitizer-pending, or sanitizer-failed status without exposing raw public page data

### Requirement: Display useful task-pack catalog and readiness
The Operator Console SHALL display useful public-readonly task-pack availability, task count, category coverage, allowlist state, and private-trace policy.

#### Scenario: Console loads useful task-pack state
- **WHEN** the Operator Console loads readiness or task-pack status
- **THEN** it shows whether the useful task pack is available, how many task contracts are configured, which categories are covered, and whether public-readonly execution remains disabled or private-by-default

### Requirement: Display useful task-pack result summary
The Operator Console SHALL display useful task-pack outcome fields before raw trace JSON.

#### Scenario: Useful public task result is rendered
- **WHEN** a useful public-readonly execution response or task-pack summary row is rendered
- **THEN** the console shows task id, task category, task kind, target class, completion criteria summary, observed proof summary, unmet criteria, outcome, route reason, stop or failure reason, visible result state, privacy state, sanitizer status, and export state

#### Scenario: Useful public task is incomplete
- **WHEN** a useful public-readonly task opens a page but misses required proof
- **THEN** the console styles the result as partial, stopped, failed, or blocked rather than successful

### Requirement: Keep useful task-pack raw evidence guarded
The Operator Console SHALL guard raw useful task-pack traces and visual artifacts behind local/private labels.

#### Scenario: Local/private visual result is available
- **WHEN** a useful public-readonly result has a local/private screenshot or trace reference
- **THEN** the console labels it as local/private and does not present it as public release evidence unless sanitizer status is passed
