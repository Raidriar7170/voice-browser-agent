## ADDED Requirements

### Requirement: Configure public-readonly execution explicitly
The system SHALL keep public-readonly webpage execution disabled unless explicit runtime configuration enables it with an allowlist.

#### Scenario: Public-readonly is disabled by default
- **WHEN** no public-readonly configuration is provided
- **THEN** public website commands are routed to controlled local, demo-preview, clarification, confirmation, or blocked outcomes without launching a real public webpage

#### Scenario: Public-readonly is enabled with allowlist
- **WHEN** public-readonly execution is enabled
- **THEN** the configuration includes allowed public origins or target templates, maximum step count, timeout budget, and private-trace policy

### Requirement: Restrict public-readonly navigation targets
The system SHALL only navigate public-readonly runs to allowlisted HTTP(S) targets that are derived from route rules, not arbitrary transcript text.

#### Scenario: Target is allowlisted
- **WHEN** a validated Browser Task Request maps to an allowlisted public target
- **THEN** the public-readonly route records the target label, sanitized origin, and execution limits

#### Scenario: Target is not allowlisted
- **WHEN** a validated Browser Task Request asks for a non-allowlisted public target
- **THEN** the system rejects live public execution with an unsupported-route reason

#### Scenario: Target uses unsafe protocol or private network
- **WHEN** a candidate public target uses `file:`, `data:`, `javascript:`, localhost, private-network, credential-bearing, or non-HTTP(S) URL forms
- **THEN** the system blocks public-readonly execution before navigation

### Requirement: Use isolated browser contexts
The system SHALL execute each public-readonly run in a fresh local browser context without persistent user profile, cookies, credentials, or storage reuse.

#### Scenario: Public-readonly run starts
- **WHEN** the executor starts a public-readonly run
- **THEN** it creates an isolated browser context and records that no persistent profile or cookie jar was used

#### Scenario: Browser state would reuse session
- **WHEN** execution would require a logged-in session, persistent profile, cookies, credentials, or private account state
- **THEN** the system stops or blocks the run before continuing

### Requirement: Limit actions to read-only or non-destructive interactions
The system SHALL allow only navigation, read-only search/filter/expand interactions, and visible information extraction during public-readonly execution.

#### Scenario: Read-only documentation search
- **WHEN** an allowlisted documentation search command is executed
- **THEN** the system may fill a public search field or click read-only navigation controls and record action evidence

#### Scenario: Mutation boundary appears
- **WHEN** execution reaches login, checkout, submit, posting, deletion, upload, download, private-data entry, or irreversible action UI
- **THEN** the system stops before taking the action and records the safety reason

### Requirement: Enforce bounded execution and evidence
The system SHALL enforce short step budgets and require meaningful page-state, action, or grounding evidence for public-readonly runs.

#### Scenario: Step budget is reached
- **WHEN** public-readonly execution reaches its configured step budget before completing the task
- **THEN** the system stops with a step-budget reason and preserves the evidence collected so far

#### Scenario: Execution returns no evidence
- **WHEN** public-readonly execution returns no action, page-state, or grounding evidence
- **THEN** the system marks the run failed or stopped with an explicit missing-evidence reason

### Requirement: Keep public-readonly traces private by default
The system SHALL store public-readonly traces as local/private runtime artifacts unless an explicit sanitizer marks them public-safe.

#### Scenario: Public-readonly trace is written
- **WHEN** a public-readonly run completes, fails, or stops
- **THEN** the trace records execution mode, route decision, sanitized origin or target label, browser actions, final status, and privacy state without publishing it by default

#### Scenario: Public artifact export is requested
- **WHEN** an operator requests a public export of a public-readonly trace
- **THEN** the export succeeds only if the public-readonly sanitizer removes or approves URLs, screenshots, page content, cookies, credentials, browser profiles, local paths, and third-party private data

### Requirement: Report public-readonly readiness
The system SHALL report whether public-readonly prerequisites are configured and ready.

#### Scenario: Readiness is requested
- **WHEN** the preflight command or readiness API runs
- **THEN** it reports public-readonly enabled state, allowlist summary, browser isolation readiness, sanitizer availability, and recommended actions without exposing private URLs or credentials
