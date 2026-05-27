## ADDED Requirements

### Requirement: Explain unsupported live-controlled fixture requests
The system SHALL return an explicit user-visible reason when a fixture is requested in live-controlled mode but is not selected for live-controlled execution.

#### Scenario: Unsupported fixture requests live-controlled mode
- **WHEN** a fixture outside the selected live-controlled task set is requested with `execution_mode` set to `live_controlled`
- **THEN** the API rejects the request with a clear explanation that the fixture is preview-only or not selected for live-controlled execution

#### Scenario: Public showcase task remains preview-only
- **WHEN** a public non-destructive showcase task such as GitHub search is run from the console
- **THEN** the system presents it as demo-preview evidence unless it has been explicitly selected as a controlled live target
