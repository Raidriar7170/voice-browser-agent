## ADDED Requirements

### Requirement: Produce structured normalized output
The system SHALL convert ASR transcripts into either a Browser Task Request or a Clarification Request.

#### Scenario: Clear command becomes a Browser Task Request
- **WHEN** the transcript expresses one clear supported browser intent
- **THEN** the normalizer returns a Browser Task Request with task, intent type, constraints, visual references, confirmation requirement, and stop conditions

#### Scenario: Ambiguous command becomes a Clarification Request
- **WHEN** the transcript cannot be safely mapped to one supported browser task
- **THEN** the normalizer returns a Clarification Request instead of a Browser Task Request

### Requirement: Restrict browser intent types
The system SHALL restrict Browser Task Requests to the supported MVP Browser Intent Types.

#### Scenario: Supported intent is accepted
- **WHEN** the normalizer outputs search and open, click visual target, fill form, select filter or option, or extract/compare visible information
- **THEN** the validator accepts the intent type if all other required fields are valid

#### Scenario: Unsupported intent is rejected
- **WHEN** the normalizer outputs an unrestricted, long-horizon, login, purchase, deletion, posting, or private-data submission intent
- **THEN** the validator rejects the request or marks it for clarification or confirmation

### Requirement: Validate normalized requests deterministically
The system SHALL run a deterministic Normalizer Validator before any browser execution begins.

#### Scenario: Required field is missing
- **WHEN** a Browser Task Request is missing task, intent type, constraints, confirmation requirement, or stop conditions
- **THEN** the validator rejects the request before browser execution

#### Scenario: Visual reference is present
- **WHEN** a command refers to visible UI such as an icon, color swatch, card, chart, or spatial target
- **THEN** the Browser Task Request includes that reference in a structured visual references field

### Requirement: Identify safety-sensitive commands
The system SHALL mark destructive, private, or irreversible actions as requiring confirmation.

#### Scenario: Payment action is detected
- **WHEN** the transcript or normalized task implies checkout, purchase, payment, deletion, posting, login, private-data entry, or file transfer
- **THEN** the Browser Task Request has requires_confirmation set to true or is converted to a Clarification Request

### Requirement: Preserve normalization evidence
The system SHALL record the transcript, normalized output, validator result, and any clarification reason in the Execution Trace.

#### Scenario: Normalization completes
- **WHEN** the normalizer and validator finish processing a transcript
- **THEN** the trace includes the input transcript, normalized output type, validator decision, and reason for acceptance, rejection, or clarification
