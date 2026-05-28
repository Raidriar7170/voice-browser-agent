## ADDED Requirements

### Requirement: Document improved console demo flow
The project SHALL document a command-first Operator Console demo flow that distinguishes controlled live evidence, demo-preview evidence, and optional public-readonly experiments.

#### Scenario: Reviewer follows console demo flow
- **WHEN** a reviewer opens the console demo instructions
- **THEN** they can run a primary command-first flow without needing fixture or execution-mode dropdowns and can still find advanced replay and trace inspection controls

### Requirement: Include controlled showcase evidence
The evidence set SHALL include controlled local showcase evidence for at least one public-site-shaped command if that route is implemented.

#### Scenario: Controlled showcase evidence exists
- **WHEN** the evidence workflow includes a GitHub-shaped controlled showcase task
- **THEN** it includes sanitized trace evidence with controlled target metadata, route decision, final status, browser action evidence, and privacy-scan status

#### Scenario: Controlled showcase evidence is absent
- **WHEN** the controlled showcase route is not implemented in this change
- **THEN** documentation explicitly says public-site-shaped commands remain demo-preview or optional spike behavior

### Requirement: Preserve preview-vs-live evidence separation
The evidence set SHALL preserve a clear separation between preview, controlled live, real voice controlled, real vision controlled, and optional public-readonly artifacts.

#### Scenario: Release pack classifies routed traces
- **WHEN** the release-pack workflow describes traces produced by route selection
- **THEN** it classifies each trace by route/evidence mode and does not infer live execution only from user-facing command text

#### Scenario: Public-readonly artifact is local-only
- **WHEN** a public-readonly trace exists but has not passed explicit sanitization
- **THEN** it remains local/private and is not included as a public sanitized demo artifact
