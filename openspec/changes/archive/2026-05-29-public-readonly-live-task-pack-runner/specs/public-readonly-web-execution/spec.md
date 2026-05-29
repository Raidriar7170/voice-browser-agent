## ADDED Requirements

### Requirement: Execute useful task pack through an opt-in live runner
The system SHALL provide a local runner that attempts useful public-readonly task-pack tasks only when public-readonly execution is explicitly enabled and every selected task has a validated task contract.

#### Scenario: Runner selects explicit tasks
- **WHEN** an operator invokes the task-pack runner with one or more task ids
- **THEN** the runner loads the useful task-pack manifest, validates each selected task contract, rejects unknown task ids, and attempts only the selected contracts

#### Scenario: Runner selects the full pack
- **WHEN** an operator invokes the task-pack runner for the full useful task pack
- **THEN** the runner validates pack size, category coverage, task ids, safe slots, target URL or template safety, allowed read-only actions, completion criteria, execution limits, and privacy policy before any live attempt

#### Scenario: Public-readonly execution is not enabled
- **WHEN** the task-pack runner is invoked without enabled public-readonly configuration
- **THEN** it records disabled or blocked outcomes without launching real public webpages and explains the missing configuration

### Requirement: Write local private task-pack run manifests
The system SHALL write every task-pack runner execution to a local/private versioned run manifest under `runtime/`.

#### Scenario: Task-pack run finishes
- **WHEN** the runner finishes a selected-task or full-pack attempt
- **THEN** it writes a manifest containing run id, manifest version, started and finished timestamps, selected task ids, runner mode, configuration summary, outcome counts, privacy state, sanitizer state, limitation notes, and one row per attempted task

#### Scenario: Task-pack row is recorded
- **WHEN** an individual task attempt completes, partially completes, stops, fails, or is blocked
- **THEN** the manifest row records task id, task category, task kind, target class, target label, sanitized origin, completion criteria id, outcome, observed proof summary, unmet criteria, stop or failure reason, route or execution reason, visible result state, evidence privacy state, sanitizer status, and export state

#### Scenario: Manifest references runtime artifacts
- **WHEN** a manifest row references a trace, screenshot, page text, or visual artifact
- **THEN** the manifest includes only guarded local/private references or sanitizer-state metadata and excludes raw screenshots, raw page text, cookies, credentials, browser profiles, local file URIs, private data, and remote host details

### Requirement: Preserve deterministic runner mode for tests
The task-pack runner SHALL support deterministic non-network execution for tests and local documentation examples.

#### Scenario: Deterministic runner mode is used
- **WHEN** the runner is invoked in deterministic fake or dry-run mode
- **THEN** it validates the same task contracts and writes the same manifest schema without opening public network pages

#### Scenario: Deterministic mode simulates outcome classes
- **WHEN** deterministic runner mode is configured with completed, partial, stopped, failed, or blocked task evidence
- **THEN** the runner records those outcome classes using the same proof, unmet criteria, privacy, sanitizer, and export-state fields as live mode

### Requirement: Classify live task-pack site variance honestly
The task-pack runner SHALL treat public-site variance as explicit task outcomes rather than bypassing, hiding, or retrying it into success.

#### Scenario: Public site blocks or varies
- **WHEN** a useful task attempt encounters captcha, verification, rate limit, unavailable page, access denial, permission boundary, redirect, selector drift, timeout, or network failure
- **THEN** the task-pack run manifest records stopped, failed, blocked, or partial outcome with a precise public-site variance reason and does not mark the task completed

#### Scenario: Page opens without task proof
- **WHEN** a useful task attempt opens an allowlisted public page but misses required completion proof
- **THEN** the task-pack run manifest records partial, stopped, or failed outcome with unmet criteria instead of completed outcome
