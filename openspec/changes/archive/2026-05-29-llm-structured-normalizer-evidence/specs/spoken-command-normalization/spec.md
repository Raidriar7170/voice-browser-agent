## ADDED Requirements

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
