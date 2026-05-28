# public-readonly-web-execution Specification

## Purpose
Define the bounded public-readonly execution lane for allowlisted public webpages, including configuration gates, isolated browser sessions, read-only action policy, private-by-default evidence, and readiness reporting.
## Requirements
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

### Requirement: Define public-readonly task contracts
The system SHALL execute real public webpage tasks only when an allowlisted public task contract defines the target, allowed actions, input slots, completion criteria, execution limits, and privacy policy.

#### Scenario: Public task contract is configured
- **WHEN** public-readonly execution is enabled for a public task
- **THEN** the task contract records task id, target label, allowlist id, task kind, target URL or template, allowed read-only action classes, completion criteria, max step count, timeout budget, and private-trace policy

#### Scenario: Public target has no task contract
- **WHEN** a command maps to an allowlisted origin but no public task contract matches the requested task
- **THEN** the system rejects live public task execution with an unsupported public task reason before navigation

### Requirement: Verify real public task completion
The system SHALL verify task-specific completion criteria before marking a public-readonly task as succeeded.

#### Scenario: Documentation search completes
- **WHEN** an allowlisted documentation search task is executed
- **THEN** the trace records the searched query, action evidence, final page state or result evidence, and a completion state indicating that the configured search criteria were satisfied

#### Scenario: Page opens but task criteria are not satisfied
- **WHEN** the executor opens an allowlisted public page but does not satisfy the requested search, read, filter, expand, or extraction criteria
- **THEN** the run is marked partial, stopped, or failed with an explicit missing completion reason instead of succeeded

#### Scenario: Public site variance prevents proof
- **WHEN** network failure, timeout, changed selectors, captcha, redirect, or unavailable public content prevents completion proof
- **THEN** the trace preserves collected evidence and records a precise public task failure or stop reason

### Requirement: Record public task completion evidence privately
The system SHALL record public task completion evidence as local/private runtime evidence unless an explicit public-readonly sanitizer approves export.

#### Scenario: Public task trace is written
- **WHEN** a public-readonly task completes, partially completes, stops, fails, or is blocked
- **THEN** the trace records task id, task kind, target label, sanitized origin, requested slots, completion criteria summary, observed proof summary, completion state, final status, stop or failure reason, and evidence privacy state

#### Scenario: Public task export is requested
- **WHEN** an operator exports a real public task trace for public evidence
- **THEN** the export includes only sanitizer-approved metadata, completion state, target label, sanitized origin, and proof summary while excluding raw URLs, raw page text, screenshots, cookies, credentials, profile paths, local file URIs, private data, and remote host details

### Requirement: Keep real public tasks read-only and bounded
The system SHALL preserve read-only action and execution limits for every real public task attempt.

#### Scenario: Action policy rejects next public action
- **WHEN** a proposed task action would log in, submit, post, purchase, delete, upload, download, enter private data, bypass captcha, or leave the configured task boundary
- **THEN** execution stops before the action and records the policy reason as part of task completion evidence

#### Scenario: Task budget is exhausted
- **WHEN** a public task reaches its configured step or timeout budget before satisfying completion criteria
- **THEN** execution stops with a budget reason and records whether the task is incomplete or partially complete
