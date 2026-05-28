## ADDED Requirements

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
