## ADDED Requirements

### Requirement: Include live task-pack runner summaries
The evidence set SHALL include reviewer-readable public-readonly useful task-pack runner summaries as local/private evidence when a runner manifest is available.

#### Scenario: Release pack includes runner summary
- **WHEN** the evidence-pack workflow builds local reviewer output and a task-pack runner manifest exists
- **THEN** it includes run id, runner mode, selected task count, outcome counts, task ids, target labels, target classes, completion criteria ids, observed proof summaries, unmet criteria, stop or failure reasons, privacy states, sanitizer statuses, export states, and limitations

#### Scenario: Runner summary is incomplete or malformed
- **WHEN** a task-pack runner manifest is missing required row fields, outcome counts, privacy state, sanitizer status, completion criteria ids, or task-specific proof fields
- **THEN** the evidence workflow reports a clear completeness or privacy error instead of presenting the live runner summary as reviewer-ready

### Requirement: Exclude raw live task-pack artifacts from public evidence
The evidence set SHALL keep raw task-pack runner traces and visual artifacts out of committed public evidence unless explicit sanitizer approval passes.

#### Scenario: Release pack sees runner local artifact
- **WHEN** the release-pack workflow encounters a task-pack runner trace, screenshot, raw page text, browser profile, local file URI, private URL, credential, cookie, or raw runtime artifact
- **THEN** it excludes the raw artifact from public evidence and records only sanitizer-state metadata or a local/private exclusion reason

#### Scenario: Runner artifact is sanitizer-approved
- **WHEN** a task-pack runner artifact passes explicit public-readonly sanitizer checks
- **THEN** public evidence includes only approved summary metadata and privacy-scan status without exposing raw public page content or local runtime paths

### Requirement: Document live task-pack runner scope and limitations
The public evidence documentation SHALL describe live task-pack runner output as bounded local/private public-readonly evidence.

#### Scenario: Reviewer reads runner documentation
- **WHEN** README, demo docs, public evidence page, closeout checklist, video plan, or interview overview mention the live task-pack runner
- **THEN** they distinguish deterministic runner validation, live allowlisted public-readonly attempts, useful task-pack summaries, and raw local/private runtime artifacts while avoiding production, benchmark, SOTA, model-quality, captcha-bypass, account-automation, or broad-autonomy claims

#### Scenario: Runner live attempt is blocked or incomplete
- **WHEN** a live task-pack runner attempt is blocked, stopped, failed, or partial due to site variance, timeout, missing selector, login boundary, rate limit, captcha, network failure, or policy stop
- **THEN** public evidence records the outcome as reliability evidence and does not present it as successful public automation

### Requirement: Gate runner evidence privacy and completeness
The evidence workflow SHALL fail or mark runner evidence incomplete when required task-pack runner data is missing, ambiguous, malformed, or privacy-unsafe.

#### Scenario: Required runner row field is missing
- **WHEN** a runner manifest row lacks task id, outcome, completion criteria id, proof summary, privacy state, sanitizer status, or export state
- **THEN** the evidence workflow reports the missing field instead of presenting the runner summary as complete

#### Scenario: Private marker is detected
- **WHEN** a runner summary or generated release-pack artifact contains raw screenshots, raw page text, cookies, credentials, browser profile paths, local file URIs, private URLs, private data, remote host details, or unsanitized runtime fields
- **THEN** the workflow exits non-zero or marks the row sanitizer-failed and does not present it as public-ready
