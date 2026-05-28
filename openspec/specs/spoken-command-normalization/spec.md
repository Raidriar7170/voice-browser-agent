# spoken-command-normalization Specification

## Purpose
Defines the Spoken Command Normalizer and deterministic validation contract that maps Chinese-first ASR transcripts into bounded Browser Task Requests or Clarification Requests before browser execution.
## Requirements
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

### Requirement: Preserve adaptation-ready normalized outputs
The system SHALL preserve normalized Browser Task Requests or Clarification Requests in a form that can be reused by later Speech-to-Task Adaptation.

#### Scenario: Accepted request is used for training example derivation
- **WHEN** a trace-derived example is created from an accepted Browser Task Request
- **THEN** the example includes the structured task, intent type, constraints, visual references, confirmation requirement, stop conditions, and safety flags

#### Scenario: Clarification request is used for training example derivation
- **WHEN** a trace-derived example is created from a Clarification Request
- **THEN** the example includes the clarification question, reason, and original transcript text

### Requirement: Normalize reviewed ASR transcript text
The normalizer SHALL accept operator-reviewed transcript text while preserving the original ASR provenance in the Execution Trace.

#### Scenario: Reviewed transcript differs from ASR output
- **WHEN** the operator edits the ASR transcript before normalization
- **THEN** the normalized Browser Task Request or Clarification Request is based on the reviewed transcript while the trace preserves original ASR text, edited text, edit status, and adapter metadata

### Requirement: Clarify uncertain real audio commands
The normalizer and validator SHALL prefer clarification over execution when real audio-derived transcript text is ambiguous or low-confidence.

#### Scenario: Real audio command is ambiguous
- **WHEN** an audio-derived reviewed transcript cannot be mapped to one bounded Browser Task Request
- **THEN** the system produces a Clarification Request and records the audio input source and transcript provenance without launching browser execution

### Requirement: Preserve public task slots during normalization
The normalizer SHALL preserve safe public task slots needed for public-readonly route selection and completion verification.

#### Scenario: Public documentation search command is normalized
- **WHEN** a transcript asks to search an allowlisted public documentation or reference site
- **THEN** the Browser Task Request preserves target site hint, search query, read-only intent, constraints, stop conditions, and safety flags needed by the public task router

#### Scenario: Public reference read command is normalized
- **WHEN** a transcript asks to read or extract visible information from an allowlisted public reference page
- **THEN** the Browser Task Request preserves target site hint, read target or extraction target, read-only intent, constraints, and stop conditions needed by the completion verifier

### Requirement: Clarify unsupported public task commands
The normalizer and validator SHALL prefer clarification or rejection when a public command cannot be mapped to one bounded read-only task.

#### Scenario: Public command is too broad
- **WHEN** a transcript asks the agent to browse broadly, compare many sites, keep searching until satisfied, use an account, bypass a barrier, or complete a long-horizon public web goal
- **THEN** the normalized output is rejected or converted to a Clarification Request instead of a public-readonly Browser Task Request

#### Scenario: Public command implies mutation
- **WHEN** a transcript asks to log in, submit, post, purchase, delete, upload, download, enter private data, or perform another non-read-only public action
- **THEN** the normalized output records safety flags and requires confirmation, clarification, or blocking before browser execution
