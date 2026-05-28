## ADDED Requirements

### Requirement: Support controlled local showcase routes
The system SHALL support controlled local showcase targets for commands that would otherwise refer to public websites but can be demonstrated safely on local pages.

#### Scenario: GitHub-shaped command maps to controlled showcase
- **WHEN** a validated command such as "打开 GitHub" or "搜索 GitHub 项目" is routed for controlled live demonstration
- **THEN** the system may execute a configured local GitHub-like controlled page and record the run as controlled local live evidence rather than real github.com evidence

#### Scenario: Controlled showcase trace is exported
- **WHEN** a controlled showcase trace is exported for public evidence
- **THEN** the export identifies the local controlled target and excludes raw screenshots, local file URIs, cookies, credentials, private URLs, browser profiles, and remote host details

### Requirement: Keep public website execution preview-only by default
The system SHALL keep public website tasks in demo-preview mode unless an explicit safe public-readonly mode is configured and selected.

#### Scenario: Public GitHub command has no public-readonly mode
- **WHEN** a command asks to open or search GitHub and public-readonly mode is disabled
- **THEN** the system returns preview-only or controlled-showcase behavior and does not claim that github.com was operated live

#### Scenario: Public task reaches login or mutation state
- **WHEN** any public task reaches login, checkout, form submission, posting, deletion, private-data entry, or another mutation boundary
- **THEN** the system stops or blocks before taking the action and records the safety reason

### Requirement: Gate optional live public-readonly execution
The system SHALL treat `live_public_readonly` as an opt-in, disabled-by-default mode with strict safety boundaries.

#### Scenario: Public-readonly is enabled for allowlisted site
- **WHEN** public-readonly mode is explicitly enabled and the normalized request targets an allowlisted public page
- **THEN** the system uses an isolated browser context, avoids persistent cookies or logged-in profiles, enforces short step budgets, and records evidence as local/private unless sanitized explicitly

#### Scenario: Public-readonly target is not allowlisted
- **WHEN** public-readonly mode is requested for a non-allowlisted target
- **THEN** the system rejects live execution with a clear unsupported-route reason

#### Scenario: Public-readonly result lacks evidence
- **WHEN** a public-readonly run returns no meaningful browser action, page-state, or grounding evidence
- **THEN** the system marks the run failed or stopped with an explicit missing-evidence reason instead of counting it as live evidence
