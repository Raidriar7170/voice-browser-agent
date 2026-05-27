## ADDED Requirements

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
