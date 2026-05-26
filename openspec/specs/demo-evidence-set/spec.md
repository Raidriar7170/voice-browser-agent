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

