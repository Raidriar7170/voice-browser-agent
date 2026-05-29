## ADDED Requirements

### Requirement: Define public-readonly useful task pack
The system SHALL define an 8-12 task useful public-readonly task pack using explicit public task contracts.

#### Scenario: Useful task pack is loaded
- **WHEN** useful public-readonly evidence is generated or inspected
- **THEN** the task pack lists 8-12 task contracts with task id, target label, target class, task category, allowlist id, task kind, safe input slots, target URL or template, allowed read-only actions, completion criteria, execution limits, privacy policy, and expected task-pack coverage

#### Scenario: Useful task pack has insufficient coverage
- **WHEN** the task pack has fewer than 8 tasks, more than 12 tasks, missing task categories, missing completion criteria, or non-read-only actions
- **THEN** the system rejects the task pack for useful public-readonly evidence

### Requirement: Cover stable public-readonly task categories
The useful task pack SHALL include stable read-only targets across documentation, reference, package metadata, release notes, and public repository read/search categories.

#### Scenario: Category coverage is inspected
- **WHEN** the task pack is loaded
- **THEN** it includes at least four target classes or task categories and avoids search-engine, login, account, mutation, upload, download, and private-network workflows

### Requirement: Generate local useful task-pack summary
The system SHALL generate a local/private useful task-pack summary from explicit task contracts and task attempt evidence.

#### Scenario: Useful task-pack summary is generated
- **WHEN** the local task-pack summary workflow runs
- **THEN** it writes a machine-readable summary under `runtime/` with task id, task category, target class, completion criteria id, outcome, observed proof summary, unmet criteria, stop or failure reason, evidence privacy state, sanitizer status, visible result state, and export state

#### Scenario: Summary references runtime evidence
- **WHEN** a summary row references a trace, screenshot, page text, or visual artifact
- **THEN** public outputs include only guarded local/private references or sanitizer-state metadata and exclude raw URLs, raw screenshots, raw page text, cookies, credentials, browser profiles, local file URIs, private data, and remote host details

### Requirement: Preserve useful task-pack outcome honesty
The system SHALL preserve task-specific completion proof and honest outcome classification for every useful public-readonly task.

#### Scenario: Page opens without useful-task proof
- **WHEN** a useful task opens an allowlisted public page but misses one or more configured proof fields
- **THEN** the task-pack summary records partial, stopped, or failed outcome with unmet criteria and does not mark the task completed

#### Scenario: Useful task is blocked before navigation
- **WHEN** validation, route policy, task-contract policy, URL safety, confirmation, or manual override protection prevents navigation
- **THEN** the task-pack summary records blocked outcome without claiming real public webpage operation
