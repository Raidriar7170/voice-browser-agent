## MODIFIED Requirements

### Requirement: Improve operator-console visual quality
The Operator Console SHALL use a polished, responsive, accessible operations-dashboard layout appropriate for repeated operator use and reviewer inspection.

#### Scenario: Console opens on desktop
- **WHEN** the operator opens the console on a desktop viewport
- **THEN** the primary command input, readiness, route decision, execution evidence, visible result, and latest status summary are visible with stable layout, readable hierarchy, and no overlapping controls

#### Scenario: Console opens on mobile-width viewport
- **WHEN** the operator opens the console on a narrow viewport
- **THEN** controls and result panels remain usable without text clipping, incoherent overlap, horizontal page scrolling, or layout shifts caused by dynamic status content

#### Scenario: Dynamic evidence content loads
- **WHEN** readiness, route cards, task-pack summaries, visual artifacts, timelines, or raw trace content load asynchronously
- **THEN** the console preserves stable panel dimensions or controlled overflow so newly loaded content does not push core controls into an unusable layout

#### Scenario: Operator uses keyboard navigation
- **WHEN** the operator tabs through command controls, upload controls, disclosures, export controls, and confirmation actions
- **THEN** each interactive element has a visible focus state, an accessible label or text label, and a stable interaction target

## ADDED Requirements

### Requirement: Present a command-first operations hierarchy
The Operator Console SHALL present command entry, readiness, route/evidence summary, visible result, and timeline inspection in an order that reflects the normal operator workflow.

#### Scenario: Operator starts from the default view
- **WHEN** the console loads before any command has been run
- **THEN** the default view emphasizes the command input and real-use readiness before advanced replay, task-pack rows, normalized JSON, or raw trace details

#### Scenario: Execution response is rendered
- **WHEN** an execution response has been rendered
- **THEN** the route decision, final status, stop or failure reason, visual result, and privacy/export state are visible before the raw trace JSON

### Requirement: Use consistent status and evidence treatments
The Operator Console SHALL use consistent text labels and visual treatments for readiness states, route states, execution outcomes, privacy states, sanitizer states, and export states.

#### Scenario: Non-success outcome is displayed
- **WHEN** a run is partial, stopped, failed, blocked, awaiting confirmation, awaiting clarification, or preview-only
- **THEN** the console displays that state with explicit text and does not style it as a successful live browser execution

#### Scenario: Local/private evidence is displayed
- **WHEN** a trace, task-pack row, visual artifact, or export result remains local/private or sanitizer-pending
- **THEN** the console labels the privacy and sanitizer state near the relevant evidence instead of requiring raw JSON inspection

### Requirement: Keep advanced evidence inspectable but secondary
The Operator Console SHALL keep fixture replay, task-pack row details, normalized JSON, and raw trace JSON available without letting them dominate the default command-first workflow.

#### Scenario: Operator inspects task-pack details
- **WHEN** task-pack catalog or latest-run rows are available
- **THEN** the console exposes them behind an explicit disclosure or secondary section that can be opened for audit

#### Scenario: Operator inspects raw trace
- **WHEN** raw trace JSON is available
- **THEN** the console keeps the raw trace inspectable while presenting the summarized route, evidence, and privacy status first
