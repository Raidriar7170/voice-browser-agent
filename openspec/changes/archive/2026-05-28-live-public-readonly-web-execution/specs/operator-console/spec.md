## ADDED Requirements

### Requirement: Display public-readonly readiness and policy state
The Operator Console SHALL display public-readonly availability, allowlist status, and private-trace policy before the operator runs a public command.

#### Scenario: Console loads readiness
- **WHEN** the Operator Console loads readiness information
- **THEN** it shows whether public-readonly execution is enabled, disabled, missing allowlist configuration, or unavailable due to browser/sanitizer prerequisites

#### Scenario: Public-readonly is disabled
- **WHEN** public-readonly execution is disabled
- **THEN** the console labels public commands as controlled-showcase, demo-preview, or unsupported rather than live public webpage operation

### Requirement: Render public-readonly route results distinctly
The Operator Console SHALL distinguish public-readonly evidence from controlled live, demo-preview, real voice, real vision, and failure evidence.

#### Scenario: Public-readonly route is selected
- **WHEN** an execution response includes a public-readonly route decision
- **THEN** the console displays target label, sanitized origin, allowlist id, private evidence state, execution limits, final status, and route reason

#### Scenario: Public-readonly route is rejected
- **WHEN** route selection rejects public-readonly execution
- **THEN** the console displays the unsupported-route or safety reason near the command result

### Requirement: Gate public-readonly export controls
The Operator Console SHALL prevent public-readonly traces from appearing as public-ready unless sanitizer checks explicitly pass.

#### Scenario: Operator exports public-readonly trace
- **WHEN** an operator requests sanitized export for a public-readonly trace
- **THEN** the console reports whether the export is public-safe or local-private and does not hide sanitizer failures

#### Scenario: Sanitizer has not approved trace
- **WHEN** a public-readonly trace has no public-safe sanitizer result
- **THEN** the console keeps the trace marked local/private and avoids presenting it as publishable evidence
