## ADDED Requirements

### Requirement: Create trace-derived training examples
The system SHALL convert an Execution Trace with transcript and normalized output into a sanitized Trace-Derived Training Example for later Speech-to-Task Adaptation.

#### Scenario: Browser task trace becomes training example
- **WHEN** an Execution Trace contains an ASR transcript, Browser Task Request, validator decision, and final status
- **THEN** the derived example includes the source execution id, transcript text, normalized output payload, validator outcome, final status, safety flags, and optional human correction

#### Scenario: Clarification trace becomes training example
- **WHEN** an Execution Trace contains an ASR transcript and Clarification Request
- **THEN** the derived example preserves the clarification reason and question as the target output instead of inventing a browser task

### Requirement: Preserve privacy in trace-derived examples
Trace-Derived Training Examples SHALL exclude raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, and unsanitized live browser state.

#### Scenario: Trace contains private nested fields
- **WHEN** a trace-derived example is created from a trace containing private nested fields
- **THEN** those private fields are omitted from the example payload

#### Scenario: Trace lacks required adaptation inputs
- **WHEN** an Execution Trace has no transcript or no normalized output
- **THEN** the system rejects training example creation with an explicit reason instead of producing a partial example
