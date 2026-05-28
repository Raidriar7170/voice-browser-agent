## ADDED Requirements

### Requirement: Display public-readonly reliability matrix status
The Operator Console SHALL display public-readonly reliability-matrix fields for public task attempts.

#### Scenario: Reliability task route is rendered
- **WHEN** an execution response includes a public-readonly reliability task route
- **THEN** the console displays task id, task kind, target class, target label, completion criteria summary, route reason, execution limits, evidence privacy state, and sanitizer status

#### Scenario: Reliability task finishes
- **WHEN** a public-readonly reliability task completes, partially completes, stops, fails, or is blocked
- **THEN** the console displays outcome classification, final status, observed proof summary, unmet criteria, stop or failure reason, visible result state, and export status near the primary result summary

### Requirement: Avoid misleading reliability success styling
The Operator Console SHALL style public-readonly reliability outcomes according to completion verification rather than page-open or action-count evidence.

#### Scenario: Opened page is incomplete
- **WHEN** a public-readonly reliability task opens a page but completion proof is missing
- **THEN** the console labels the run as partial, stopped, or failed and does not present it as successful public automation

#### Scenario: Task is blocked before navigation
- **WHEN** a reliability task is blocked before public navigation
- **THEN** the console displays the block reason without showing public webpage operation evidence

### Requirement: Surface reliability privacy and export state
The Operator Console SHALL keep reliability evidence privacy state visible whenever public-readonly artifacts are shown.

#### Scenario: Local/private artifact is displayed
- **WHEN** the console displays a public-readonly screenshot, visual result, proof summary, or trace reference
- **THEN** it labels the artifact as local/private or public-safe according to sanitizer status and does not offer it as public-ready evidence unless approved

#### Scenario: Sanitized export is requested
- **WHEN** the operator requests export for a public-readonly reliability task
- **THEN** the console reports public-safe, local/private, sanitizer-pending, or sanitizer-failed status without exposing raw public page data
