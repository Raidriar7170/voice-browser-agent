## ADDED Requirements

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
