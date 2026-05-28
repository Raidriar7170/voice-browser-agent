## ADDED Requirements

### Requirement: Provide final project closeout handoff pack
The project SHALL provide a final closeout handoff pack that ties together the bounded MVP evidence, validation commands, generated local artifacts, and archive readiness.

#### Scenario: Reviewer follows closeout checklist
- **WHEN** a reviewer opens the closeout checklist
- **THEN** it identifies the required commands for demo evidence release-pack generation, Speech-to-Task dataset generation, OpenSpec strict validation, full test execution, diff whitespace checks, and git ignored-output review

#### Scenario: Checklist distinguishes committed sources from generated artifacts
- **WHEN** the checklist describes release-pack or adaptation dataset outputs
- **THEN** it states that generated runtime artifacts stay local and points back to committed sanitized trace sources

### Requirement: Provide browser-openable interview briefing
The project SHALL include a browser-openable interview/project briefing derived from repository evidence.

#### Scenario: Reviewer opens briefing locally
- **WHEN** a reviewer opens the briefing HTML file from the repository
- **THEN** it explains the problem, bounded scope, architecture, execution flow, evidence modes, safety and privacy gates, adaptation dataset output, validation surface, limitations, and interview talk track

#### Scenario: Briefing links to evidence sources
- **WHEN** the briefing discusses project claims
- **THEN** it references the README, demo task suite, ablations, video plan, release-pack workflow, adaptation dataset workflow, sanitized trace directories, and OpenSpec validation surface

### Requirement: Guard final handoff positioning
The final handoff pack SHALL preserve bounded Voice-to-Browser Agent positioning and avoid unsupported claims.

#### Scenario: Final handoff wording is checked
- **WHEN** README, closeout checklist, demo docs, or interview briefing are reviewed by automated wording guards
- **THEN** they avoid benchmark, SOTA, production automation, unrestricted autonomy, ASR/TTS quality, model checkpoint, and public raw-dataset claims

#### Scenario: Limitations are stated
- **WHEN** a reviewer reads the briefing
- **THEN** it states that model fine-tuning, expanded dataset collection, public hosting, and broad public-web automation are out of scope for the closeout MVP
