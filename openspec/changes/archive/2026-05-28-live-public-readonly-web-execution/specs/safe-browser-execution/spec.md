## ADDED Requirements

### Requirement: Execute public-readonly requests through isolated local browser sessions
The system SHALL execute public-readonly Browser Task Requests only through local isolated browser sessions after validation, confirmation, and route policy accept the request.

#### Scenario: Public-readonly browser execution starts
- **WHEN** a Browser Task Request has a valid public-readonly route and no pending confirmation
- **THEN** the executor launches a local isolated browser context with no persistent profile, no stored cookies, and no reused logged-in state

#### Scenario: Public-readonly request is not route-approved
- **WHEN** a Browser Task Request lacks a valid public-readonly route decision
- **THEN** the executor does not launch a public browser session

### Requirement: Enforce public-readonly stop conditions during execution
The system SHALL stop public-readonly execution before mutation, authentication, private data, file transfer, or irreversible browser states.

#### Scenario: Sensitive public browser state appears
- **WHEN** the public browser state indicates login, checkout, submit, posting, deletion, upload, download, password entry, private-data entry, or irreversible action
- **THEN** the executor stops before the next action and records the matched stop reason

#### Scenario: Action policy rejects next action
- **WHEN** the next proposed action is outside read-only navigation, read-only search/filter/expand, or visible information extraction
- **THEN** the executor blocks the action and records an action-policy stop reason

### Requirement: Record public-readonly evidence without leaking private state
The system SHALL record public-readonly execution evidence while excluding browser profile paths, cookies, credentials, raw screenshots, local file URIs, private URLs, and remote host details from sanitized responses.

#### Scenario: Public-readonly run completes
- **WHEN** public-readonly execution succeeds, fails, or stops
- **THEN** the trace includes execution mode, route decision, page title or sanitized origin, action events, grounding references when available, final status, stop or failure reason, and privacy state

#### Scenario: Public-readonly sanitizer exports trace
- **WHEN** a public-readonly trace is exported through the sanitizer
- **THEN** the exported payload excludes raw browser state and marks whether the trace is public-safe or local-private
