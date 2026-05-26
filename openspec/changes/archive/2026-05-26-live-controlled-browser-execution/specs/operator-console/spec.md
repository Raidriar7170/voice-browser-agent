## ADDED Requirements

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
