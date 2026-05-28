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

### Requirement: Execute bounded GitHub public-readonly tasks
The system SHALL support explicitly configured GitHub public-readonly task contracts for public repository search and public repository page reading.

#### Scenario: GitHub repository search contract is configured
- **WHEN** public-readonly execution is enabled with a `github-repo-search` task contract for `https://github.com/search`
- **THEN** the contract records the GitHub allowlist id, task kind, search query slot, repository search URL template, allowed read-only actions, completion criteria, execution limits, and local/private artifact policy

#### Scenario: GitHub public repository read contract is configured
- **WHEN** public-readonly execution is enabled with a `github-public-repo-read` task contract
- **THEN** the contract records owner and repository slots, the public repository URL template, allowed read-only extraction actions, completion criteria, execution limits, and local/private artifact policy

#### Scenario: GitHub task contract is absent
- **WHEN** a GitHub command matches the GitHub allowlist but no configured GitHub public task contract matches the requested search or read task
- **THEN** the system rejects real GitHub public-readonly execution before navigation and records a task-contract mismatch reason

### Requirement: Verify GitHub task-specific completion
The system SHALL verify GitHub-specific completion criteria before marking a GitHub public-readonly task completed.

#### Scenario: GitHub repository search completes
- **WHEN** a GitHub repository search task executes successfully
- **THEN** the trace records the searched query, search-result page evidence, sanitized GitHub origin, visible repository result marker or result count evidence, final page title, and completed public task state

#### Scenario: GitHub public repository read completes
- **WHEN** a GitHub public repository page read task executes successfully
- **THEN** the trace records the owner/repository slug, public repository page evidence, visible README or repository description marker, final page title, and completed public task state

#### Scenario: GitHub page opens without task proof
- **WHEN** GitHub opens but the configured search, repository, README, or result evidence is not observed
- **THEN** the run is marked partial, stopped, or failed with an explicit missing GitHub completion reason instead of succeeded

### Requirement: Handle GitHub public-site variance honestly
The system SHALL classify common unauthenticated GitHub variance as explicit public task outcomes rather than bypassing or hiding it.

#### Scenario: GitHub requires verification or captcha
- **WHEN** the GitHub page shows captcha, abuse detection, device verification, suspicious activity, or similar verification UI
- **THEN** execution stops before further action, records a `public_task_captcha_or_verification` reason, and preserves local/private visual evidence when safe

#### Scenario: GitHub requires login or account state
- **WHEN** the GitHub task reaches sign-in, account-only, private repository, or permission-required UI
- **THEN** execution stops before login or account interaction and records a `public_task_login_boundary` reason

#### Scenario: GitHub rate-limits or blocks unauthenticated access
- **WHEN** GitHub returns rate-limit, abuse-limit, unavailable, or access-denied state for the public task
- **THEN** the trace records a blocked, stopped, or failed outcome with a precise GitHub site-variance reason and does not claim task completion

### Requirement: Record GitHub visual result artifacts privately
The system SHALL record local/private visual result artifacts for GitHub public-readonly tasks without making them public evidence by default.

#### Scenario: GitHub visual artifact is captured
- **WHEN** a GitHub public-readonly task captures a step or final screenshot
- **THEN** the trace records a local/private artifact reference, action label, page title, sanitized origin, completion state, and sanitizer status without embedding raw screenshot bytes in public trace payloads

#### Scenario: GitHub visual artifact is exported publicly
- **WHEN** a public export is requested for a GitHub public-readonly trace
- **THEN** raw screenshots and raw page text remain excluded unless the public-readonly sanitizer explicitly approves them as public-safe

### Requirement: Define public-readonly reliability smoke set
The system SHALL define a public-readonly reliability smoke set containing 5-8 allowlisted read-only task contracts.

#### Scenario: Reliability smoke set is loaded
- **WHEN** public-readonly reliability evidence is generated or inspected
- **THEN** the smoke set lists 5-8 task contracts with task id, target label, target class, allowlist id, task kind, safe input slots, target URL or template, allowed read-only actions, completion criteria, execution limits, privacy policy, and expected matrix coverage

#### Scenario: Task contract lacks completion criteria
- **WHEN** a public-readonly smoke task lacks task-specific completion criteria
- **THEN** the system rejects the task contract for reliability-matrix use instead of allowing page-open success

### Requirement: Record public-readonly reliability outcomes
The system SHALL record a reliability outcome for every public-readonly smoke task attempt.

#### Scenario: Public task completes
- **WHEN** a public-readonly task satisfies all configured completion criteria
- **THEN** the matrix row records `completed` outcome, observed proof summary, task id, target class, final status, evidence privacy state, and sanitizer status

#### Scenario: Public task does not fully complete
- **WHEN** a public-readonly task opens a page or collects useful evidence but misses one or more completion criteria
- **THEN** the matrix row records `partial`, `stopped`, or `failed` with observed proof, unmet criteria, stop reason or failure reason, and private evidence state

#### Scenario: Public task is blocked before navigation
- **WHEN** validation, route policy, task-contract policy, URL safety, confirmation, or manual override protection prevents public navigation
- **THEN** the matrix row records `blocked` without claiming real public webpage operation

### Requirement: Preserve reliability safety boundaries
The public-readonly reliability matrix SHALL preserve the bounded read-only safety contract for every task row.

#### Scenario: Task attempts mutation or account action
- **WHEN** a public-readonly reliability task would log in, submit, post, purchase, delete, star, fork, comment, create an issue, open a pull request, upload, download, enter private data, or reuse account state
- **THEN** execution stops or blocks before the action and records the policy reason as the reliability outcome reason

#### Scenario: Task encounters captcha or verification
- **WHEN** a public-readonly reliability task encounters captcha, verification, abuse detection, rate limit, permission boundary, or similar public-site variance
- **THEN** the matrix row records stopped, blocked, or failed outcome with a precise site-variance reason and does not claim completion

### Requirement: Keep matrix evidence private by default
The system SHALL keep raw public-readonly reliability evidence local/private unless sanitizer approval is explicit.

#### Scenario: Matrix references runtime artifact
- **WHEN** a matrix row references a public-readonly trace, screenshot, page text, or visual artifact
- **THEN** public outputs include only approved metadata or guarded local/private references and exclude raw URLs, raw page text, raw screenshots, cookies, credentials, browser profiles, local file URIs, private data, and remote host details

#### Scenario: Sanitizer approves summary
- **WHEN** the public-readonly sanitizer approves a matrix summary for export
- **THEN** the exported summary includes target label, sanitized origin, task kind, completion state, observed proof summary, stop or failure reason, privacy-scan status, and limitations without raw runtime content
