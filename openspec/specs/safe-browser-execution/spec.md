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

### Requirement: Execute public-readonly requests through isolated local browser sessions
The system SHALL execute public-readonly Browser Task Requests only through local isolated browser sessions after validation, confirmation, and route policy accept the request.

#### Scenario: Public-readonly browser execution starts
- **WHEN** a Browser Task Request has a valid public-readonly route and no pending confirmation
- **THEN** the executor launches a local isolated browser context with no persistent profile, no stored cookies, and no reused logged-in state

#### Scenario: Public-readonly request is not route-approved
- **WHEN** a Browser Task Request lacks a valid public-readonly route decision
- **THEN** the executor does not launch a public browser session

### Requirement: Enforce public-readonly stop conditions during execution
The system SHALL stop public-readonly execution before mutation, authentication, private data, file transfer, or irreversible browser states.

#### Scenario: Sensitive public browser state appears
- **WHEN** the public browser state indicates login, checkout, submit, posting, deletion, upload, download, password entry, private-data entry, or irreversible action
- **THEN** the executor stops before the next action and records the matched stop reason

#### Scenario: Action policy rejects next action
- **WHEN** the next proposed action is outside read-only navigation, read-only search/filter/expand, or visible information extraction
- **THEN** the executor blocks the action and records an action-policy stop reason

### Requirement: Record public-readonly evidence without leaking private state
The system SHALL record public-readonly execution evidence while excluding browser profile paths, cookies, credentials, raw screenshots, local file URIs, private URLs, and remote host details from sanitized responses.

#### Scenario: Public-readonly run completes
- **WHEN** public-readonly execution succeeds, fails, or stops
- **THEN** the trace includes execution mode, route decision, page title or sanitized origin, action events, grounding references when available, final status, stop or failure reason, and privacy state

#### Scenario: Public-readonly sanitizer exports trace
- **WHEN** a public-readonly trace is exported through the sanitizer
- **THEN** the exported payload excludes raw browser state and marks whether the trace is public-safe or local-private

### Requirement: Record real browser-use-vision controlled evidence
The system SHALL provide a controlled execution evidence path that invokes `browser-use-vision` visual grounding functionality through the installed package dependency boundary and records a sanitized Execution Trace.

#### Scenario: Real visual grounding path runs on controlled page
- **WHEN** a selected controlled visual task is executed in real-vision controlled mode
- **THEN** the system invokes `browser-use-vision` visual grounding code and records evidence mode, provider metadata, adapter metadata, grounding references, final status, and failure or stop reason when present

#### Scenario: Real visual evidence is separated from deterministic evidence
- **WHEN** the real-vision controlled trace is exported as a public artifact
- **THEN** its file path or metadata distinguishes it from demo-preview, deterministic live-controlled, and deterministic agentic live-controlled traces

### Requirement: Gate real-vision evidence honesty
The system SHALL NOT count deterministic controlled adapter output as real `browser-use-vision` visual grounding evidence.

#### Scenario: browser-use-vision entry point is unavailable
- **WHEN** the installed `browser-use-vision` package or required visual grounding entry point cannot be imported or invoked
- **THEN** the real-vision evidence workflow fails or marks the trace unavailable with a clear reason instead of producing passing real-vision evidence

#### Scenario: Visual grounding produces no meaningful evidence
- **WHEN** real-vision controlled mode returns no provider metadata, no grounding references, and no visual evidence summary
- **THEN** the system marks the run as failed or unavailable instead of counting it as real-vision evidence

### Requirement: Preserve privacy in real-vision controlled traces
The system SHALL export only sanitized real-vision controlled traces.

#### Scenario: Real-vision trace is committed or packaged
- **WHEN** a real-vision controlled trace is included in committed evidence or a release pack
- **THEN** it excludes raw screenshots, raw audio, browser profile data, cookies, credentials, private URLs, remote host details, absolute local file URIs, and unsanitized runtime state

### Requirement: Execute public tasks with completion-aware verifier
The public-readonly executor SHALL run allowed public task actions and then verify task-specific completion criteria before returning success.

#### Scenario: Public task verifier passes
- **WHEN** the executor performs the configured read-only task steps and observes the required task-specific proof
- **THEN** the execution result records succeeded status, completed public task state, observed proof summary, browser action evidence, and grounding references when available

#### Scenario: Public task verifier fails
- **WHEN** the executor performs safe actions but cannot observe the required task-specific proof
- **THEN** the execution result is failed or stopped with a missing public task completion reason instead of succeeded

### Requirement: Preserve policy stops during public task execution
The public-readonly executor SHALL enforce URL, action, browser-state, and stop-condition policy checks before and during task execution.

#### Scenario: Sensitive state appears before completion
- **WHEN** a public task reaches login, captcha, checkout, submit, posting, deletion, upload, download, password entry, private-data entry, off-allowlist navigation, or another configured sensitive state
- **THEN** the executor stops before the next action and records the matched policy reason and incomplete task state

#### Scenario: Next action is outside task policy
- **WHEN** the next proposed action is not listed in the task contract's allowed read-only action classes
- **THEN** the executor blocks the action and records an action-policy stop reason

### Requirement: Classify real public task outcomes
The execution result SHALL distinguish completed, partial, stopped, failed, and blocked public task outcomes.

#### Scenario: Public task partially completes
- **WHEN** the run collects useful public page evidence but does not meet all completion criteria before a safe stop or budget limit
- **THEN** the trace records partial completion state with collected proof and the remaining unmet criteria

#### Scenario: Public task is blocked before navigation
- **WHEN** validation, confirmation, route policy, URL safety, or task contract policy blocks a public command before opening a public page
- **THEN** the trace records blocked outcome without claiming that a public webpage was operated

### Requirement: Capture local visual evidence for public-readonly execution
The public-readonly executor SHALL capture local/private visual artifacts for real public tasks when visual result capture is enabled.

#### Scenario: Public task step screenshot is captured
- **WHEN** a public-readonly task completes a meaningful navigation, search, read, or stop step
- **THEN** the executor records a screenshot artifact reference, page title, sanitized origin, action type, completion state, and local/private privacy state in the trace runtime metadata

#### Scenario: Public task final screenshot is captured
- **WHEN** a public-readonly task finishes, stops, fails, or is blocked after navigation
- **THEN** the executor records a final visual result artifact that the local Operator Console can display without embedding raw screenshot bytes in exported public trace JSON

### Requirement: Preserve isolation for visible public browser runs
The executor SHALL preserve public-readonly isolation even when the operator enables a visible headed browser debug mode.

#### Scenario: Headed public browser mode is enabled
- **WHEN** the operator configures public-readonly execution to use a visible local browser window
- **THEN** the executor still launches a fresh ephemeral browser context with no persistent user profile, no reused cookies, no stored credentials, and the same read-only action policy

#### Scenario: Headed public browser mode is disabled
- **WHEN** headed browser mode is not configured
- **THEN** the executor may run headless while still capturing local/private visual artifacts for the Operator Console

### Requirement: Protect local visual artifacts from public export
The system SHALL prevent local public-readonly visual artifacts from being treated as public-safe evidence unless sanitizer approval is explicit.

#### Scenario: Public visual artifact is in local runtime
- **WHEN** a trace references public-readonly visual artifacts under the local runtime directory
- **THEN** sanitized API responses expose only guarded local artifact references and metadata needed by the local console

#### Scenario: Public visual artifact fails sanitizer checks
- **WHEN** an export workflow sees raw screenshots, raw page text, private URLs, cookies, credentials, browser profile paths, local file URIs, or remote host details in a public-readonly visual artifact
- **THEN** the export fails or marks the trace local/private and does not present the artifact as public-ready

### Requirement: Classify public-readonly safety outcomes for reliability
The public-readonly executor SHALL classify safety stops and policy blocks as explicit reliability outcomes.

#### Scenario: Policy blocks before navigation
- **WHEN** URL safety, private-network detection, manual override protection, validation, confirmation, or task-contract policy blocks a public-readonly reliability command before navigation
- **THEN** the executor records a blocked outcome with no claim that a public webpage was operated

#### Scenario: Sensitive public state appears after navigation
- **WHEN** execution observes login, captcha, verification, checkout, submit, posting, deletion, upload, download, password entry, private-data entry, account action, off-allowlist navigation, or irreversible action UI
- **THEN** the executor stops before the next action and records stopped or blocked outcome with the matched policy reason

### Requirement: Treat missing completion proof as non-success
The public-readonly executor SHALL NOT return success for reliability tasks unless completion verification passes.

#### Scenario: Page opens without required proof
- **WHEN** the executor opens an allowlisted public page but does not observe the task contract's required proof
- **THEN** the execution result records partial, stopped, or failed outcome with unmet criteria instead of succeeded status

#### Scenario: Task budget expires before proof
- **WHEN** a public-readonly reliability task reaches its step or timeout budget before satisfying completion criteria
- **THEN** the execution result records incomplete outcome, collected proof, unmet criteria, and budget reason

### Requirement: Preserve local/private visual evidence for matrix inspection
The executor SHALL preserve guarded local/private visual evidence for reliability tasks when visual artifact capture is enabled.

#### Scenario: Step visual artifact is captured
- **WHEN** a reliability task captures a step or final screenshot
- **THEN** the trace records guarded artifact reference, action label, page title, sanitized origin, completion state, and local/private privacy state without embedding raw screenshot bytes in public export payloads

#### Scenario: Visual artifact is unsafe for export
- **WHEN** sanitizer checks do not approve a public-readonly visual artifact
- **THEN** the export keeps the artifact local/private and the matrix row reports sanitizer-pending or sanitizer-failed status
