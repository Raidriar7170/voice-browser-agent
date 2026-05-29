## ADDED Requirements

### Requirement: Display useful task-pack catalog and readiness
The Operator Console SHALL display useful public-readonly task-pack availability, task count, category coverage, allowlist state, and private-trace policy.

#### Scenario: Console loads useful task-pack state
- **WHEN** the Operator Console loads readiness or task-pack status
- **THEN** it shows whether the useful task pack is available, how many task contracts are configured, which categories are covered, and whether public-readonly execution remains disabled or private-by-default

### Requirement: Display useful task-pack result summary
The Operator Console SHALL display useful task-pack outcome fields before raw trace JSON.

#### Scenario: Useful public task result is rendered
- **WHEN** a useful public-readonly execution response or task-pack summary row is rendered
- **THEN** the console shows task id, task category, task kind, target class, completion criteria summary, observed proof summary, unmet criteria, outcome, route reason, stop or failure reason, visible result state, privacy state, sanitizer status, and export state

#### Scenario: Useful public task is incomplete
- **WHEN** a useful public-readonly task opens a page but misses required proof
- **THEN** the console styles the result as partial, stopped, failed, or blocked rather than successful

### Requirement: Keep useful task-pack raw evidence guarded
The Operator Console SHALL guard raw useful task-pack traces and visual artifacts behind local/private labels.

#### Scenario: Local/private visual result is available
- **WHEN** a useful public-readonly result has a local/private screenshot or trace reference
- **THEN** the console labels it as local/private and does not present it as public release evidence unless sanitizer status is passed
