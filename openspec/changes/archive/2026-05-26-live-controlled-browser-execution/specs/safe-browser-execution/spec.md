## ADDED Requirements

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
