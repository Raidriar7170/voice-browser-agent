## ADDED Requirements

### Requirement: Display visual verification summary
The Operator Console SHALL display post-action visual verification status in the execution summary and agentic timeline.

#### Scenario: Verification passes
- **WHEN** an execution response contains a visual verification result with outcome `passed`
- **THEN** the console displays the verified outcome, expected condition, observed state summary, proof or evidence reference summary, and final status without requiring the operator to open raw JSON

#### Scenario: Verification fails or is uncertain
- **WHEN** an execution response contains a visual verification result with outcome `failed` or `uncertain`
- **THEN** the console displays the failed or uncertain reason, unmet condition or uncertainty summary, recovery or stop decision, and final status without styling the run as successfully verified

### Requirement: Display visual verification recovery flow
The Operator Console SHALL make bounded re-observation, recovery, and stop decisions visible for visual verification failures.

#### Scenario: Verification triggers recovery
- **WHEN** a failed or uncertain visual verification result triggers re-observation or a bounded recovery action
- **THEN** the console shows the verification result, recovery decision, next observation, and subsequent verification outcome in chronological order

#### Scenario: Verification stops execution
- **WHEN** visual verification remains failed or uncertain after the allowed recovery budget
- **THEN** the console shows the stop reason near the agentic step timeline and result summary

### Requirement: Preserve visual verification privacy in console surfaces
The Operator Console SHALL display only sanitized verification metadata and safe evidence references by default.

#### Scenario: Verification evidence is rendered
- **WHEN** a trace includes visual verification evidence references or provider metadata
- **THEN** the console renders safe outcome, reason, provider mode, verifier mode, and sanitized reference fields while excluding raw screenshots, raw annotated images, raw provider prompts, raw provider responses, request headers, API keys, credentials, cookies, browser profiles, private URLs, local file URIs, and remote host details

### Requirement: Display verifier readiness
The Operator Console SHALL show whether visual verification is running in deterministic, mock, real-provider, unavailable, or disabled mode.

#### Scenario: Console loads readiness
- **WHEN** the Operator Console loads readiness information
- **THEN** it displays visual verifier mode, whether controlled verification is available, whether real-provider verification is configured, and any missing setup action without exposing credentials or remote host details
