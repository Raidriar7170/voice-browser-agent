## ADDED Requirements

### Requirement: Display latest live task-pack run status
The Operator Console SHALL display the latest public-readonly useful task-pack runner status when local/private run metadata is available.

#### Scenario: Console loads latest run status
- **WHEN** the Operator Console loads readiness or task-pack status after a runner manifest has been written
- **THEN** it shows run id, runner mode, selected task count, outcome counts, privacy state, sanitizer state, finished timestamp, and whether raw public runtime artifacts remain local/private

#### Scenario: No latest run exists
- **WHEN** no task-pack runner manifest is available
- **THEN** the console shows task-pack catalog and readiness state without implying that live public tasks have been attempted

### Requirement: Render live task-pack run rows
The Operator Console SHALL render live task-pack runner rows before raw trace JSON.

#### Scenario: Live task-pack row is rendered
- **WHEN** a runner manifest row is displayed
- **THEN** the console shows task id, task category, task kind, target class, target label, sanitized origin, completion criteria summary, outcome, observed proof summary, unmet criteria, stop or failure reason, visible result state, privacy state, sanitizer status, and export state

#### Scenario: Live task-pack row is incomplete
- **WHEN** a runner row opens a page but misses configured proof
- **THEN** the console styles the row as partial, stopped, failed, or blocked rather than successful public automation

### Requirement: Keep live task-pack artifacts privacy-aware in the console
The Operator Console SHALL keep task-pack runner traces and visual artifacts labeled local/private unless sanitizer approval is explicit.

#### Scenario: Runner visual artifact is available
- **WHEN** the console displays a local/private screenshot, visual result, trace reference, or guarded artifact reference from a task-pack runner row
- **THEN** it labels the artifact as local/private, shows sanitizer status, and does not present it as public release evidence unless sanitizer status is passed

#### Scenario: Runner artifact is unavailable
- **WHEN** no visual artifact is available for a runner row
- **THEN** the console falls back to proof summary, unmet criteria, and stop or failure reason without inventing visual evidence

### Requirement: Distinguish runner mode from broad public operation
The Operator Console SHALL distinguish deterministic runner mode, blocked/disabled runner state, and live public-readonly runner attempts.

#### Scenario: Deterministic run is displayed
- **WHEN** the latest runner manifest was produced in deterministic fake or dry-run mode
- **THEN** the console labels the run as non-network validation evidence rather than real public webpage operation

#### Scenario: Live run is displayed
- **WHEN** the latest runner manifest was produced in live mode
- **THEN** the console labels the run as allowlisted public-readonly local/private evidence and preserves the non-goals for login, mutation, account workflows, captcha bypass, and broad public-web automation
