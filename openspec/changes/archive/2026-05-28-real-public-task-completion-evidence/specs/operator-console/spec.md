## ADDED Requirements

### Requirement: Display public task plan and completion state
The Operator Console SHALL show public-readonly task plan and completion evidence distinctly from simple page-open evidence.

#### Scenario: Public task route is selected
- **WHEN** an execution response includes a public-readonly task route
- **THEN** the console displays task id, task kind, target label, sanitized origin, allowed action summary, completion criteria summary, execution limits, private evidence state, and route reason

#### Scenario: Public task finishes
- **WHEN** a public-readonly task completes, partially completes, stops, fails, or is blocked
- **THEN** the console displays completion state, final status, observed proof summary, stop or failure reason, and whether the trace remains local/private

### Requirement: Avoid misleading public task success styling
The Operator Console SHALL NOT present real public task attempts as successful unless completion criteria are satisfied.

#### Scenario: Page opens but task is incomplete
- **WHEN** a public task opens an allowlisted page but completion verification fails or remains partial
- **THEN** the console labels the run as incomplete, stopped, or failed rather than successful live public task execution

#### Scenario: Public task is blocked before navigation
- **WHEN** a public command is rejected by route, policy, validation, confirmation, or task-contract checks before navigation
- **THEN** the console displays the block reason without showing public webpage operation evidence

### Requirement: Surface public task privacy and export status
The Operator Console SHALL keep real public task traces local/private unless sanitizer approval is explicit.

#### Scenario: Operator requests public task export
- **WHEN** an operator exports a public task trace
- **THEN** the console reports whether the export is public-safe, local/private, or sanitizer-failed and shows the reason without exposing raw public page data

#### Scenario: Sanitizer approval is absent
- **WHEN** a public task trace has no public-safe sanitizer status
- **THEN** the console keeps the trace marked local/private and avoids presenting it as publishable evidence
