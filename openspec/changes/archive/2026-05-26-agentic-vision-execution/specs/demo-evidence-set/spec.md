## ADDED Requirements

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
