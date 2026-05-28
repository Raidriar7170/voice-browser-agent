## ADDED Requirements

### Requirement: Publish public-readonly reliability matrix summary
The evidence set SHALL include a reviewer-readable public-readonly reliability matrix summary.

#### Scenario: Reviewer opens reliability evidence
- **WHEN** a reviewer opens public evidence documentation or a generated release-pack index
- **THEN** they can inspect each reliability task row with task id, target label, target class, task kind, completion criteria, outcome, observed proof summary, unmet criteria, stop or failure reason, privacy state, sanitizer status, and regression coverage

#### Scenario: Matrix row has local/private runtime evidence
- **WHEN** a reliability matrix row references a trace, screenshot, page text, or public runtime artifact that is not sanitizer-approved
- **THEN** the public evidence includes only an approved summary or local/private marker and does not include raw runtime content

### Requirement: Gate reliability matrix completeness and privacy
The evidence workflow SHALL fail or mark the matrix incomplete when required reliability evidence is missing, ambiguous, malformed, or privacy-unsafe.

#### Scenario: Required outcome class is missing
- **WHEN** the reliability matrix lacks coverage for completed, partial, stopped, failed, or blocked outcome classes
- **THEN** the workflow reports the missing outcome class instead of presenting the matrix as complete

#### Scenario: Private marker is detected
- **WHEN** a candidate reliability summary or release-pack artifact contains raw screenshots, raw page text, cookies, credentials, browser profile paths, local file URIs, private URLs, private data, remote host details, or unsanitized runtime fields
- **THEN** the workflow exits non-zero or marks the row sanitizer-failed and does not present it as public-ready

### Requirement: Preserve bounded public-readonly positioning
The public evidence documentation SHALL describe the reliability matrix as bounded local read-only evidence, not production automation, broad public-web autonomy, or benchmark ranking.

#### Scenario: Reviewer reads matrix limitations
- **WHEN** public evidence docs describe the public-readonly reliability matrix
- **THEN** they state the allowlist, task-contract boundary, completion verifier, private-by-default trace policy, and non-goals for arbitrary URLs, login, mutation, account automation, captcha bypass, long-horizon browsing, production deployment, and benchmark claims
