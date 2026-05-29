## ADDED Requirements

### Requirement: Display normalizer provenance
The Operator Console SHALL display which normalizer source produced the current normalized output and whether fallback occurred.

#### Scenario: Rule normalization is rendered
- **WHEN** an execution response contains rule-based normalizer provenance
- **THEN** the console labels the result as rule-based normalization and displays the validator decision with the normalized request or clarification

#### Scenario: LLM normalization is rendered
- **WHEN** an execution response contains mock or real LLM normalizer provenance
- **THEN** the console labels the provider mode, output source, schema status, fallback state, and validator decision without exposing secrets or raw private provider responses

#### Scenario: Fallback is rendered
- **WHEN** LLM normalization falls back to rule-based normalization or clarification
- **THEN** the console displays the fallback reason near the normalized output and does not present the result as a clean LLM success

### Requirement: Surface LLM normalizer readiness
The Operator Console SHALL make optional LLM normalizer readiness visible before the operator expects live-provider normalization.

#### Scenario: Console loads readiness
- **WHEN** the Operator Console loads readiness information
- **THEN** it shows whether the active normalizer mode is rule, deterministic mock LLM, configured real provider, or unavailable/misconfigured provider

#### Scenario: Real provider is unavailable
- **WHEN** the selected real LLM provider is missing required configuration or fails readiness checks
- **THEN** the console explains that normalization will use fallback or clarification behavior rather than silently implying live LLM execution

### Requirement: Preserve safe operator messaging for LLM-normalized commands
The Operator Console SHALL keep validation, confirmation, clarification, route, and stop states visible for LLM-normalized commands.

#### Scenario: LLM output requires confirmation
- **WHEN** an LLM-normalized Browser Task Request triggers the Confirmation Gate
- **THEN** the console displays the confirmation reason and prevents the result from appearing complete before operator confirmation

#### Scenario: LLM output is blocked
- **WHEN** an LLM-normalized request is rejected by validation or route policy
- **THEN** the console displays the blocking reason alongside normalizer provenance and does not start browser execution
