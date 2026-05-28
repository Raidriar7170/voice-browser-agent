# operator-task-routing Specification

## Purpose
Defines deterministic command routing after normalization and validation, including controlled local targets, preview-only outcomes, clarification and blocked states, audio transcript provenance, and route evidence recorded for the Operator Console.
## Requirements
### Requirement: Select an execution route for each command
The system SHALL select an explicit execution route after normalization and validation and before browser execution.

#### Scenario: Command maps to controlled live task
- **WHEN** a validated Browser Task Request matches a supported controlled local target
- **THEN** the route decision identifies the controlled fixture id, target reference, execution mode, route reason, and user-visible explanation

#### Scenario: Command is preview-only
- **WHEN** a validated Browser Task Request describes a public showcase or unsupported live task that is not selected for controlled live execution
- **THEN** the route decision keeps the request in demo-preview mode and explains that no live browser action will be claimed

#### Scenario: Command requires clarification
- **WHEN** normalization produces a Clarification Request
- **THEN** the route decision prevents browser execution and preserves the clarification reason for the Operator Console

### Requirement: Route reviewed audio and typed transcript consistently
The system SHALL use the same route-selection rules for typed transcript commands and operator-reviewed audio transcripts.

#### Scenario: Reviewed audio matches controlled task
- **WHEN** reviewed audio transcript text maps to a supported controlled task and passes validation
- **THEN** the selected route uses the controlled target while preserving audio input and transcript-review provenance

#### Scenario: Typed transcript matches same controlled task
- **WHEN** typed transcript text maps to the same supported controlled task and passes validation
- **THEN** the selected route uses the same controlled target without requiring manual fixture or execution-mode dropdown selection

### Requirement: Preserve route decision evidence
The system SHALL record route decisions in the execution response or trace metadata.

#### Scenario: Route is selected
- **WHEN** a route decision is made for an execution attempt
- **THEN** the response includes route type, selected target when present, route reason, supported execution mode, and whether the result may be treated as live evidence

#### Scenario: Route is unsupported
- **WHEN** the command cannot be executed live under current safety and readiness boundaries
- **THEN** the response includes a user-visible unsupported-route explanation without presenting the run as successful live browser execution

### Requirement: Keep route selection deterministic and bounded
The system SHALL route only to bounded Browser Intent Types and configured targets.

#### Scenario: Command asks for broad web autonomy
- **WHEN** a command requires unrestricted browsing, login completion, posting, purchasing, deletion, private-data entry, or long-horizon planning
- **THEN** the route selector returns clarification, confirmation, blocked, or preview-only state instead of selecting live execution
