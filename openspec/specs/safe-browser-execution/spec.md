# safe-browser-execution Specification

## Purpose
Defines safe browser execution boundaries for validated Browser Task Requests, including local-first execution, `browser-use-vision` visual grounding dependency use, confirmation gates, stop conditions, trace evidence, live controlled mode, and agentic safety enforcement.
## Requirements
### Requirement: Execute only validated browser task requests
The system SHALL execute browser actions only after a Browser Task Request passes validation and any required confirmation.

#### Scenario: Valid request starts browser execution
- **WHEN** a Browser Task Request passes validation and does not require pending confirmation
- **THEN** the system starts browser execution for the normalized task

#### Scenario: Clarification request does not execute
- **WHEN** the normalizer returns a Clarification Request
- **THEN** the system does not start browser execution

### Requirement: Use browser-use-vision as visual grounding dependency
The system SHALL use `browser-use-vision` as a package dependency for visual grounding rather than copying or owning its internals.

#### Scenario: Visual grounding is enabled
- **WHEN** a task requires visual grounding
- **THEN** the browser executor uses `browser-use-vision` capabilities such as SoM, OCR, region captioning, or adaptive visual context through the dependency boundary

### Requirement: Keep browser execution local by default
The system SHALL run the Operator Console and browser execution locally while allowing heavy model inference to run through remote services.

#### Scenario: Remote vision backend is configured
- **WHEN** a Remote Vision Backend URL is configured
- **THEN** the visual grounding dependency can call the remote service while the browser session remains local

### Requirement: Apply confirmation gate before sensitive actions
The system SHALL pause or block destructive, private, or irreversible actions until operator confirmation is received.

#### Scenario: Request requires confirmation
- **WHEN** a Browser Task Request has requires_confirmation set to true
- **THEN** the system pauses before execution and asks the operator to confirm or cancel

#### Scenario: Browser state reaches sensitive step
- **WHEN** execution reaches checkout, payment, deletion, posting, login, private-data entry, or irreversible submission
- **THEN** the system pauses or stops even if the original request did not explicitly require confirmation

### Requirement: Respect stop conditions
The system SHALL stop execution when a normalized stop condition is reached.

#### Scenario: Login required stop condition is reached
- **WHEN** the browser reaches a login-required state listed in stop conditions
- **THEN** the system stops execution and records the stop reason

### Requirement: Produce execution traces
The system SHALL produce an Execution Trace for every Spoken Command Execution.

#### Scenario: Browser execution finishes
- **WHEN** execution succeeds, fails, is clarified, is cancelled, or is stopped by a gate
- **THEN** the trace records transcript, normalized output, validator decision, confirmation decision, browser actions, grounding evidence, final status, and failure or stop reason

### Requirement: Support live controlled execution mode
The system SHALL support a non-dry-run live controlled execution mode for selected controlled demo tasks while preserving the existing demo-preview mode.

#### Scenario: Live controlled mode starts browser executor
- **WHEN** a validated Browser Task Request for a selected controlled task is executed with live controlled mode enabled
- **THEN** the system invokes the browser executor through the `browser-use-vision` dependency instead of returning a demo-preview action

#### Scenario: Demo preview mode remains available
- **WHEN** the same fixture is executed with demo-preview mode enabled
- **THEN** the system returns a trace marked as preview execution without launching live browser actions

### Requirement: Record live browser execution evidence
The system SHALL record meaningful live execution evidence for every live controlled run.

#### Scenario: Live controlled run completes
- **WHEN** a live controlled browser run succeeds, fails, or stops
- **THEN** the Execution Trace includes execution mode, browser action events, grounding evidence references, final status, and failure or stop reason when applicable

#### Scenario: Live controlled run has no meaningful action evidence
- **WHEN** the browser executor returns no action event and no grounding evidence for a live controlled run
- **THEN** the system marks the trace as failed or stopped with an explicit reason instead of counting it as live evidence

### Requirement: Keep live browser execution local
The system SHALL keep browser execution local during live controlled runs while allowing optional remote model inference for visual grounding.

#### Scenario: Remote vision backend is configured for live controlled run
- **WHEN** a Remote Vision Backend URL is configured for a live controlled run
- **THEN** the browser session remains local and only visual inference may use the remote backend

#### Scenario: Remote browser details are absent from public artifacts
- **WHEN** a live controlled trace is exported as a sanitized artifact
- **THEN** the export contains no remote host details, browser profile path, cookies, credentials, or private live browser state

### Requirement: Route validated live requests through agentic vision execution
The system SHALL route selected validated live-controlled Browser Task Requests through the bounded agentic vision execution loop.

#### Scenario: Live controlled visual request is executed agentically
- **WHEN** a selected controlled visual task is executed in live-controlled mode and validation has accepted the Browser Task Request
- **THEN** the system invokes the agentic vision executor and records the execution style in runtime or trace metadata

#### Scenario: Demo preview remains non-agentic preview
- **WHEN** a fixture is executed in demo-preview mode
- **THEN** the system may return the existing preview trace without launching live browser actions or claiming agentic execution occurred

### Requirement: Enforce safety gates during agentic execution
The system SHALL enforce confirmation gates, stop conditions, and sensitive browser-state checks before and during the agentic loop.

#### Scenario: Sensitive state appears during loop
- **WHEN** an agentic step observes checkout, payment, deletion, posting, login, private-data entry, irreversible submission, or another configured sensitive state
- **THEN** the system pauses, blocks, or stops before the next action and records the safety decision

#### Scenario: Stop condition is reached during loop
- **WHEN** an agentic step observes a browser state that matches a normalized stop condition
- **THEN** the system stops execution and records the matched stop condition in the Execution Trace

### Requirement: Keep agentic browser execution local
The system SHALL keep browser sessions local during agentic live-controlled runs while allowing optional remote inference only through configured model backends.

#### Scenario: Remote visual inference is configured
- **WHEN** a remote vision backend URL is configured for an agentic live-controlled run
- **THEN** the browser session remains local and the trace records only sanitized backend references, not remote host details

### Requirement: Reject empty agentic live evidence
The system SHALL reject agentic live-controlled results that do not contain meaningful step, action, or grounding evidence.

#### Scenario: Agentic adapter returns empty evidence
- **WHEN** the agentic executor returns no steps, no action events, and no grounding evidence references
- **THEN** the system marks the run as failed or stopped with an explicit missing agentic evidence reason

### Requirement: Explain unsupported live-controlled fixture requests
The system SHALL return an explicit user-visible reason when a fixture is requested in live-controlled mode but is not selected for live-controlled execution.

#### Scenario: Unsupported fixture requests live-controlled mode
- **WHEN** a fixture outside the selected live-controlled task set is requested with `execution_mode` set to `live_controlled`
- **THEN** the API rejects the request with a clear explanation that the fixture is preview-only or not selected for live-controlled execution

#### Scenario: Public showcase task remains preview-only
- **WHEN** a public non-destructive showcase task such as GitHub search is run from the console
- **THEN** the system presents it as demo-preview evidence unless it has been explicitly selected as a controlled live target

### Requirement: Execute real audio-derived controlled requests safely
The system SHALL route real audio-derived Browser Task Requests through the same validation, confirmation, stop-condition, and controlled execution boundaries used by fixture and transcript requests.

#### Scenario: Real voice controlled execution succeeds
- **WHEN** an audio-derived transcript normalizes to a supported controlled visual task and passes validation without pending confirmation
- **THEN** the system executes only the selected controlled local page, records `real_voice_controlled` evidence metadata, browser action evidence, grounding references, final status, and sanitized runtime metadata

#### Scenario: Real voice controlled execution requires confirmation
- **WHEN** an audio-derived transcript normalizes to a safety-sensitive Browser Task Request
- **THEN** the system pauses at the Confirmation Gate and records the pending confirmation state before any browser action is executed

### Requirement: Reject unsafe real voice execution shortcuts
The system SHALL NOT treat fixture transcripts, direct text input, or unchecked ASR output as successful real voice evidence.

#### Scenario: Fixture is mislabeled as real voice
- **WHEN** evidence generation attempts to mark fixture-only or transcript-only input as `real_voice_controlled`
- **THEN** the workflow fails with a clear source-mismatch reason

#### Scenario: Unreviewed low-confidence ASR is unsafe
- **WHEN** ASR metadata reports low confidence or an unavailable diagnostic and the operator has not reviewed the transcript
- **THEN** the system requires transcript review or produces a clarification/failure trace instead of executing blindly

### Requirement: Support controlled local showcase routes
The system SHALL support controlled local showcase targets for commands that would otherwise refer to public websites but can be demonstrated safely on local pages.

#### Scenario: GitHub-shaped command maps to controlled showcase
- **WHEN** a validated command such as "打开 GitHub" or "搜索 GitHub 项目" is routed for controlled live demonstration
- **THEN** the system may execute a configured local GitHub-like controlled page and record the run as controlled local live evidence rather than real github.com evidence

#### Scenario: Controlled showcase trace is exported
- **WHEN** a controlled showcase trace is exported for public evidence
- **THEN** the export identifies the local controlled target and excludes raw screenshots, local file URIs, cookies, credentials, private URLs, browser profiles, and remote host details

### Requirement: Keep public website execution preview-only by default
The system SHALL keep public website tasks in demo-preview mode unless an explicit safe public-readonly mode is configured and selected.

#### Scenario: Public GitHub command has no public-readonly mode
- **WHEN** a command asks to open or search GitHub and public-readonly mode is disabled
- **THEN** the system returns preview-only or controlled-showcase behavior and does not claim that github.com was operated live

#### Scenario: Public task reaches login or mutation state
- **WHEN** any public task reaches login, checkout, form submission, posting, deletion, private-data entry, or another mutation boundary
- **THEN** the system stops or blocks before taking the action and records the safety reason

### Requirement: Gate optional live public-readonly execution
The system SHALL treat `live_public_readonly` as an opt-in, disabled-by-default mode with strict safety boundaries.

#### Scenario: Public-readonly is enabled for allowlisted site
- **WHEN** public-readonly mode is explicitly enabled and the normalized request targets an allowlisted public page
- **THEN** the system uses an isolated browser context, avoids persistent cookies or logged-in profiles, enforces short step budgets, and records evidence as local/private unless sanitized explicitly

#### Scenario: Public-readonly target is not allowlisted
- **WHEN** public-readonly mode is requested for a non-allowlisted target
- **THEN** the system rejects live execution with a clear unsupported-route reason

#### Scenario: Public-readonly result lacks evidence
- **WHEN** a public-readonly run returns no meaningful browser action, page-state, or grounding evidence
- **THEN** the system marks the run failed or stopped with an explicit missing-evidence reason instead of counting it as live evidence
