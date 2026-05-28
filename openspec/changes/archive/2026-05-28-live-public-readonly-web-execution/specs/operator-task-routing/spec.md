## ADDED Requirements

### Requirement: Route allowlisted public commands to public-readonly execution
The system SHALL select a public-readonly route only when a validated Browser Task Request maps to an allowlisted public target and public-readonly execution is enabled.

#### Scenario: Allowlisted public command is routed
- **WHEN** a validated command targets an allowlisted public documentation, search, or read-only information page
- **THEN** the route decision identifies `live_public_readonly`, the sanitized target label, the route reason, execution limits, private evidence state, and user-visible explanation

#### Scenario: Public-readonly is disabled
- **WHEN** a public command would otherwise match a public-readonly target but public-readonly is disabled
- **THEN** the route decision keeps the command in controlled-showcase, demo-preview, or unsupported-route state and explains that public-readonly is disabled

### Requirement: Prevent public-readonly override bypass
The system SHALL prevent manual execution-mode, fixture, or client-side overrides from forcing public-readonly execution outside route policy.

#### Scenario: Manual override requests public-readonly for non-allowlisted target
- **WHEN** a request includes a public-readonly execution override for a non-allowlisted or unsafe target
- **THEN** the route selector returns blocked or preview-only output and records the unsupported-route reason

#### Scenario: Unsafe command requests public-readonly
- **WHEN** a command requires login, posting, purchasing, deletion, upload, download, private-data entry, or long-horizon browsing
- **THEN** the route selector returns clarification, confirmation, blocked, or preview-only state instead of public-readonly execution

### Requirement: Preserve public-readonly route evidence
The system SHALL record enough route evidence to audit why a public command did or did not execute.

#### Scenario: Public-readonly route is selected
- **WHEN** route selection chooses public-readonly execution
- **THEN** the response and trace include route type, execution mode, target label, sanitized origin, allowlist id, route reason, evidence privacy state, and live evidence eligibility

#### Scenario: Public command is unsupported
- **WHEN** route selection rejects public-readonly execution
- **THEN** the response and trace include a user-visible explanation without claiming live public webpage operation
