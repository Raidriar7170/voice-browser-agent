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
