## ADDED Requirements

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
