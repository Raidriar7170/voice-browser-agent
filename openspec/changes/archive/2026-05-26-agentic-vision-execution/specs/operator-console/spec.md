## ADDED Requirements

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
