## ADDED Requirements

### Requirement: Provide command-first operator workflow
The Operator Console SHALL provide a primary command-first workflow that can be used without selecting fixture or execution-mode dropdowns.

#### Scenario: Operator runs typed command
- **WHEN** the operator enters a transcript command and activates the primary run action
- **THEN** the console sends the command through normalization, route selection, validation, confirmation handling, and execution or preview according to the route decision

#### Scenario: Operator runs reviewed audio command
- **WHEN** the operator reviews or edits an uploaded or recorded audio transcript and activates the primary run action
- **THEN** the console sends the reviewed transcript and audio id through the same route-selection and execution flow while preserving ASR provenance

### Requirement: Present advanced controls separately
The Operator Console SHALL keep fixture replay, execution-mode override, raw trace JSON, and sanitized export controls available as advanced or inspectable controls outside the primary workflow.

#### Scenario: Operator needs fixture replay
- **WHEN** the operator opens advanced replay controls
- **THEN** fixture selection and execution-mode override are available without dominating the default command-first flow

#### Scenario: Operator inspects raw trace
- **WHEN** an execution response has been rendered
- **THEN** the console provides access to raw trace JSON and sanitized export without exposing raw private artifacts by default

### Requirement: Display route and evidence summary
The Operator Console SHALL display route decision, execution mode, evidence mode, final status, browser state, and stop or failure reason in a compact result area.

#### Scenario: Controlled live run succeeds
- **WHEN** route selection executes a controlled live task successfully
- **THEN** the console displays the selected route, controlled target, page title or final browser state, browser action evidence, grounding references, and final status as live controlled evidence

#### Scenario: Preview-only run is rendered
- **WHEN** route selection keeps a command in demo-preview mode
- **THEN** the console clearly labels the result as preview-only and explains that no live browser action was executed

#### Scenario: Run fails or stops
- **WHEN** execution fails, stops, or requires confirmation or clarification
- **THEN** the console displays the reason near the result summary and does not visually present the run as successful

### Requirement: Improve operator-console visual quality
The Operator Console SHALL use a polished, responsive, accessible tool layout appropriate for repeated operator use.

#### Scenario: Console opens on desktop
- **WHEN** the operator opens the console on a desktop viewport
- **THEN** the primary command input, readiness, route decision, and execution evidence are visible with stable layout, readable hierarchy, and no overlapping controls

#### Scenario: Console opens on mobile-width viewport
- **WHEN** the operator opens the console on a narrow viewport
- **THEN** controls and result panels remain usable without text clipping, incoherent overlap, or layout shifts caused by dynamic status content
