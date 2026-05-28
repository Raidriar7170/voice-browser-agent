## ADDED Requirements

### Requirement: Display visible result for real public tasks
The Operator Console SHALL display a visible result panel for real public-readonly task attempts when local/private visual artifacts are available.

#### Scenario: Public task visual result is available
- **WHEN** an execution response includes public-readonly visual artifact metadata
- **THEN** the console displays the final screenshot preview, page title, target label, sanitized origin, completion state, privacy state, and sanitizer status near the route and evidence panels

#### Scenario: Public task step screenshots are available
- **WHEN** an execution response includes multiple public-readonly step artifact references
- **THEN** the console displays a compact step timeline that lets the operator inspect navigation, search, read, and stop states without opening raw trace JSON

### Requirement: Display GitHub block states visibly
The Operator Console SHALL show GitHub public-readonly block states as visible outcomes rather than successful execution.

#### Scenario: GitHub captcha or verification blocks execution
- **WHEN** a GitHub public-readonly task stops on captcha, verification, abuse detection, or similar blocking state
- **THEN** the console displays the blocking screenshot or visual summary, stop reason, local/private privacy state, and non-completed task state

#### Scenario: GitHub login or rate-limit boundary blocks execution
- **WHEN** a GitHub public-readonly task reaches login, permission, private repository, rate-limit, or access-denied UI
- **THEN** the console displays the boundary reason and does not style the run as completed or successful public automation

### Requirement: Keep visual result UI privacy-aware
The Operator Console SHALL make local/private status visible whenever it displays real public webpage artifacts.

#### Scenario: Visual artifact is local/private
- **WHEN** the console renders a public-readonly screenshot or visual result
- **THEN** it labels the artifact as local/private and shows sanitizer status without offering it as public-ready evidence

#### Scenario: Visual artifact is unavailable
- **WHEN** no visual artifact is available for a public-readonly run
- **THEN** the console falls back to completion proof and trace evidence while explicitly saying that no visual result was captured
