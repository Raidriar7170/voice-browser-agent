## ADDED Requirements

### Requirement: Classify public-readonly safety outcomes for reliability
The public-readonly executor SHALL classify safety stops and policy blocks as explicit reliability outcomes.

#### Scenario: Policy blocks before navigation
- **WHEN** URL safety, private-network detection, manual override protection, validation, confirmation, or task-contract policy blocks a public-readonly reliability command before navigation
- **THEN** the executor records a blocked outcome with no claim that a public webpage was operated

#### Scenario: Sensitive public state appears after navigation
- **WHEN** execution observes login, captcha, verification, checkout, submit, posting, deletion, upload, download, password entry, private-data entry, account action, off-allowlist navigation, or irreversible action UI
- **THEN** the executor stops before the next action and records stopped or blocked outcome with the matched policy reason

### Requirement: Treat missing completion proof as non-success
The public-readonly executor SHALL NOT return success for reliability tasks unless completion verification passes.

#### Scenario: Page opens without required proof
- **WHEN** the executor opens an allowlisted public page but does not observe the task contract's required proof
- **THEN** the execution result records partial, stopped, or failed outcome with unmet criteria instead of succeeded status

#### Scenario: Task budget expires before proof
- **WHEN** a public-readonly reliability task reaches its step or timeout budget before satisfying completion criteria
- **THEN** the execution result records incomplete outcome, collected proof, unmet criteria, and budget reason

### Requirement: Preserve local/private visual evidence for matrix inspection
The executor SHALL preserve guarded local/private visual evidence for reliability tasks when visual artifact capture is enabled.

#### Scenario: Step visual artifact is captured
- **WHEN** a reliability task captures a step or final screenshot
- **THEN** the trace records guarded artifact reference, action label, page title, sanitized origin, completion state, and local/private privacy state without embedding raw screenshot bytes in public export payloads

#### Scenario: Visual artifact is unsafe for export
- **WHEN** sanitizer checks do not approve a public-readonly visual artifact
- **THEN** the export keeps the artifact local/private and the matrix row reports sanitizer-pending or sanitizer-failed status
