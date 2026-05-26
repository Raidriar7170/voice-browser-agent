## ADDED Requirements

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
