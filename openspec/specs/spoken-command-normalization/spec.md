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

### Requirement: Preserve bounded GitHub public task slots
The normalizer SHALL preserve safe GitHub task slots needed for public-readonly route selection, execution, and completion verification.

#### Scenario: GitHub repository search command is normalized
- **WHEN** a transcript asks to search GitHub for public repositories or projects
- **THEN** the Browser Task Request preserves target site hint `GitHub`, normalized search query, repository search intent, read-only constraints, stop conditions, and safety flags without hardcoding an unrelated query

#### Scenario: GitHub public repository read command is normalized
- **WHEN** a transcript asks to open or read a specific public GitHub repository
- **THEN** the Browser Task Request preserves target site hint `GitHub`, owner/repository or repository slug slot when present, read target, read-only constraints, stop conditions, and safety flags

### Requirement: Clarify or reject unsupported GitHub commands
The normalizer and validator SHALL avoid converting broad or account-oriented GitHub commands into live public-readonly Browser Task Requests.

#### Scenario: GitHub command asks for account action
- **WHEN** a transcript asks to log in, star, fork, watch, comment, create an issue, open a pull request, edit a file, upload, download, or access a private repository on GitHub
- **THEN** the normalized output requires clarification, confirmation, or blocking instead of live GitHub public-readonly execution

#### Scenario: GitHub command is broad research
- **WHEN** a transcript asks to browse GitHub broadly, compare many repositories, keep searching until good projects are found, or make a ranking recommendation
- **THEN** the normalized output is a clarification request or a bounded search task that states the missing narrowing criteria

### Requirement: Preserve expanded public-readonly task slots
The normalizer SHALL preserve safe task slots required by the expanded public-readonly reliability smoke set.

#### Scenario: Documentation search command is normalized
- **WHEN** a transcript asks to search an allowlisted documentation or reference site
- **THEN** the Browser Task Request preserves target site hint, search query, read-only intent, constraints, stop conditions, and safety flags needed by the matching reliability task contract

#### Scenario: Public repository read command is normalized
- **WHEN** a transcript asks to read a specific public repository or public reference page
- **THEN** the Browser Task Request preserves target site hint, owner/repository or read target slots when present, read-only intent, constraints, stop conditions, and safety flags needed by completion verification

### Requirement: Clarify unsupported reliability commands
The normalizer and validator SHALL prefer clarification, rejection, or blocking when a public command cannot map to one bounded reliability task.

#### Scenario: Command is broad public browsing
- **WHEN** a transcript asks the agent to browse broadly, compare many sites, keep searching until satisfied, make an open-ended recommendation, use an account, bypass a barrier, or complete a long-horizon public web goal
- **THEN** the normalized output is rejected or converted to a Clarification Request instead of a public-readonly reliability Browser Task Request

#### Scenario: Command implies mutation or private data
- **WHEN** a transcript asks to log in, submit, post, purchase, delete, star, fork, comment, create an issue, open a pull request, upload, download, enter private data, or perform another non-read-only action
- **THEN** the normalized output records safety flags and requires clarification, confirmation, or blocking before route selection

#### Scenario: Command includes arbitrary URL
- **WHEN** a transcript includes an arbitrary URL, unsafe protocol, private-network host, credential-bearing URL, or mixed-origin target outside configured task slots
- **THEN** the normalizer or validator preserves the safety concern so route selection cannot treat it as an approved reliability task

### Requirement: Normalize safe useful public-readonly slots
The normalizer SHALL preserve structured slots needed for useful public-readonly documentation, reference, package metadata, release-note, and public repository read/search tasks.

#### Scenario: Useful public command is normalized
- **WHEN** a spoken or typed command asks to read documentation, inspect reference material, check package metadata, inspect release notes, search public repositories, or read a public repository page
- **THEN** the normalized Browser Task Request preserves safe slots such as target site hint, search query, read target, package ecosystem, package name, release target, owner, repository, repository slug, and task category without emitting arbitrary navigation URLs

### Requirement: Reject unsupported useful public-readonly commands
The normalizer and validator SHALL reject or clarify useful public commands that are broad, ambiguous, account-oriented, mutation-oriented, or private-data-oriented.

#### Scenario: Useful public command exceeds bounded scope
- **WHEN** a command asks for unrestricted browsing, open-ended comparison across arbitrary sites, login, account mutation, repository write action, comment, issue, pull request, star, fork, form submission, purchase, upload, download, private data entry, captcha bypass, or a credential-bearing/private-network URL
- **THEN** the normalized result is a clarification request, validation rejection, confirmation gate, or blocked state rather than an executable useful public-readonly task

### Requirement: Configure LLM structured-output normalization
The system SHALL support a configurable LLM structured-output normalizer path while preserving the rule-based normalizer as the default keyless mode and fallback baseline.

#### Scenario: Rule mode is selected
- **WHEN** runtime configuration selects rule-based normalization or no LLM provider is configured
- **THEN** the system uses the deterministic rule-based normalizer and records rule provenance without requiring API keys or network access

#### Scenario: LLM mode is selected
- **WHEN** runtime configuration selects an LLM normalizer provider
- **THEN** the system sends the transcript through a provider adapter that is expected to return either a Browser Task Request payload or a Clarification Request payload

#### Scenario: Mock LLM mode is selected
- **WHEN** runtime configuration selects a deterministic mock LLM provider
- **THEN** the system exercises the same schema parsing, fallback, validation, and provenance path used by real providers without external network access

### Requirement: Gate LLM output through schema and deterministic validation
The system SHALL treat LLM output as a candidate normalized output that must pass schema parsing and deterministic validation before any browser execution can begin.

#### Scenario: LLM output is schema-valid
- **WHEN** the LLM provider returns a payload that validates as a Browser Task Request or Clarification Request
- **THEN** the system applies the existing Normalizer Validator, Confirmation Gate, and route selection behavior before execution

#### Scenario: LLM output is malformed
- **WHEN** the LLM provider returns malformed JSON, an unknown output kind, unsupported fields, or a payload that fails schema validation
- **THEN** the system records the schema failure and falls back to rule normalization or emits a Clarification Request according to configured fallback policy

#### Scenario: LLM output is unsafe
- **WHEN** the LLM provider returns a schema-valid request that implies unsupported long-horizon browsing, login, mutation, private data entry, arbitrary URL navigation, or another unsafe action
- **THEN** deterministic validation, confirmation, route policy, or blocking behavior prevents direct browser execution

### Requirement: Preserve LLM normalizer provenance
The system SHALL record normalizer provenance in execution traces and sanitized exports without exposing provider credentials or raw private provider data.

#### Scenario: Normalization completes
- **WHEN** rule, mock LLM, real LLM, or fallback normalization produces a normalized output
- **THEN** the trace records selected provider mode, output source, prompt or schema version, output kind, fallback reason when present, schema status, and validator decision

#### Scenario: Sanitized trace is exported
- **WHEN** a trace containing LLM normalizer metadata is exported for review
- **THEN** the export includes safe provenance fields while excluding API keys, request headers, raw secret-bearing prompts, raw provider responses, private transcripts, and remote host details

### Requirement: Compare normalizer outputs locally
The system SHALL provide a local comparison workflow for rule and LLM-style normalizer outputs over committed fixture transcripts and reviewed normalizer examples.

#### Scenario: Comparison workflow runs without provider credentials
- **WHEN** the comparison workflow is run in keyless mode
- **THEN** it compares rule-based normalization with deterministic mock LLM outputs and records schema validity, validator outcome, output source, and fallback behavior

#### Scenario: Optional real provider comparison runs
- **WHEN** a real LLM provider is explicitly configured for comparison
- **THEN** the workflow records provider mode and sanitized outcome metadata without requiring raw provider prompts or responses to be committed
