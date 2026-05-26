## ADDED Requirements

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
