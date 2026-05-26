# demo-evidence-set Specification

## Purpose
TBD - created by archiving change voice-browser-agent. Update Purpose after archive.
## Requirements
### Requirement: Provide reproducible demo task suite
The project SHALL include a Demo Task Suite of 8-12 controlled or public non-destructive tasks.

#### Scenario: Demo task suite is listed
- **WHEN** a reviewer opens the demo task documentation
- **THEN** the documentation lists each task, audio fixture, expected browser intent type, expected stop condition, and whether visual grounding is required

### Requirement: Include visual-grounding-heavy tasks
At least half of the Demo Task Suite SHALL be Visual-Grounding-Heavy Tasks.

#### Scenario: Demo suite contains eight tasks
- **WHEN** the Demo Task Suite contains eight tasks
- **THEN** at least four tasks depend on visual UI evidence such as icons, color swatches, canvas/SVG content, image-like cards, or spatial references

### Requirement: Use reproducible audio fixtures
The project SHALL provide Reproducible Audio Fixtures for the stable demo path.

#### Scenario: Demo task is run from fixture
- **WHEN** a demo task is executed from its saved audio fixture
- **THEN** the system can reproduce the ASR-to-execution flow without requiring live microphone input

### Requirement: Store sanitized demo artifacts
The project SHALL store only sanitized public demo artifacts in the repository.

#### Scenario: Public trace artifact is committed
- **WHEN** a trace artifact is included in public documentation or version control
- **THEN** it contains no credentials, private URLs, personal data, raw user recordings, remote host details, or live browser state

### Requirement: Include demo ablations
The project SHALL include 2-3 Demo Ablations that show why major modules are needed without presenting a benchmark leaderboard.

#### Scenario: Visual grounding ablation is shown
- **WHEN** the documentation demonstrates a task without visual grounding
- **THEN** it explains the observed failure or limitation without claiming a benchmark result or SOTA comparison

### Requirement: Avoid benchmark positioning
The public documentation SHALL position the project as a bounded voice-driven browser agent demo, not as a benchmark or general autonomous assistant.

#### Scenario: README describes project scope
- **WHEN** a reviewer reads the README
- **THEN** the README describes bounded Chinese-first voice-driven browser execution, explicit safety stops, traceable artifacts, and no unrestricted web autonomy claim

### Requirement: Provide live controlled sanitized traces
The project SHALL include sanitized live controlled trace artifacts for at least two controlled visual-grounding-heavy demo tasks.

#### Scenario: Reviewer opens live controlled artifacts
- **WHEN** a reviewer opens the live controlled trace artifact directory
- **THEN** it contains sanitized traces for at least two selected controlled visual tasks and each trace is marked as live controlled evidence

#### Scenario: Live controlled task fails
- **WHEN** a selected live controlled task fails or stops
- **THEN** the sanitized trace records the final status, failure or stop reason, and any available browser action or grounding evidence references

### Requirement: Distinguish preview and live evidence sets
The project SHALL clearly distinguish demo-preview artifacts from live-controlled artifacts in file paths and documentation.

#### Scenario: Demo documentation lists evidence modes
- **WHEN** a reviewer reads the demo task documentation
- **THEN** the documentation identifies which artifacts are demo-preview traces and which artifacts are live-controlled traces

#### Scenario: Sanitized artifacts are committed
- **WHEN** sanitized preview and live artifacts are committed
- **THEN** their directory names or metadata make the execution mode unambiguous

### Requirement: Preserve public artifact privacy for live runs
The project SHALL publish only sanitized live controlled artifacts.

#### Scenario: Live trace is exported for public evidence
- **WHEN** a live controlled trace is written to the public artifact directory
- **THEN** it excludes raw audio, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, and unsanitized live browser state

### Requirement: Provide sanitized agentic execution traces
The project SHALL include sanitized agentic execution trace artifacts for selected controlled visual-grounding-heavy demo tasks.

#### Scenario: Reviewer opens agentic trace artifacts
- **WHEN** a reviewer opens the public agentic trace artifact directory
- **THEN** it contains sanitized traces for at least two selected controlled visual tasks and each trace includes agentic step evidence

#### Scenario: Agentic task fails or stops
- **WHEN** a selected agentic visual task fails, stops, or requires clarification
- **THEN** the sanitized trace records the final status, step evidence, and failure, stop, recovery, or clarification reason

### Requirement: Distinguish agentic evidence from preview evidence
The project SHALL clearly distinguish agentic live-controlled evidence from demo-preview evidence in documentation, paths, or trace metadata.

#### Scenario: Demo documentation lists evidence modes
- **WHEN** a reviewer reads the demo task documentation
- **THEN** the documentation identifies which artifacts are demo-preview traces, live-controlled action-list traces, and agentic live-controlled traces

### Requirement: Include agentic demo ablations
The project SHALL include small Demo Ablations that explain why re-observation and visual target resolution matter for agentic execution.

#### Scenario: Re-observation ablation is documented
- **WHEN** the documentation demonstrates a visual task without re-observation after action
- **THEN** it explains the observed failure or limitation without presenting a benchmark, leaderboard, or SOTA claim

#### Scenario: Visual target resolution ablation is documented
- **WHEN** the documentation demonstrates a visual task without visual grounding target resolution
- **THEN** it explains the observed failure or limitation using controlled demo evidence

### Requirement: Preserve privacy in agentic artifacts
The project SHALL publish only sanitized agentic execution artifacts.

#### Scenario: Agentic trace is committed
- **WHEN** an agentic execution trace is included in public documentation or version control
- **THEN** it excludes raw audio, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, and unsanitized live browser state

