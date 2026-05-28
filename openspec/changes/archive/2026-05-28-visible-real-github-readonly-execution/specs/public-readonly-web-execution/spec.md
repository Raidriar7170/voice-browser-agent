## ADDED Requirements

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
