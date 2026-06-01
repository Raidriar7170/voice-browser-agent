## ADDED Requirements

### Requirement: Distinguish CI-backed validation from local review evidence
Final reviewer handoff surfaces SHALL distinguish GitHub Actions validation from
local/private generated evidence.

#### Scenario: Final handoff lists validation commands
- **WHEN** README, closeout checklist, public evidence page, or interview overview list project validation
- **THEN** they separate CI-backed workflow checks from local commands such as release-pack generation, public-readonly task-pack runs, normalizer comparison, Speech-to-Task dataset generation, and adaptation evaluation

#### Scenario: CI status is shown
- **WHEN** a public badge, workflow name, or CI status is shown in a handoff surface
- **THEN** the surrounding text describes only the checks that workflow actually runs and does not imply live public browsing, real-provider inference, recorded-audio evaluation, model training, or full local runtime reproduction unless those checks are part of the workflow

### Requirement: Reference reliability snapshots as generated summaries
Final evidence documentation SHALL describe reliability snapshots as generated
local summaries derived from existing evidence sources, not as new committed raw
evidence.

#### Scenario: Snapshot path is documented
- **WHEN** reviewer instructions mention the reliability snapshot manifest
- **THEN** they state that it is generated under ignored `runtime/` output and summarize the committed sanitized sources or optional local manifests it consumes

#### Scenario: Snapshot is absent
- **WHEN** a reviewer has not generated the reliability snapshot
- **THEN** handoff docs provide the command to regenerate it and avoid claiming snapshot metrics as already present in the checkout

### Requirement: Avoid stale local pass counts in public handoff
Public-facing handoff docs SHALL avoid hard-coded validation counts unless the
counts are generated or explicitly tied to the current verified closeout record.

#### Scenario: Test count is presented
- **WHEN** README, public evidence page, interview overview, closeout checklist, or release-pack index includes a concrete test count
- **THEN** the text identifies the source of that count or uses command-based wording such as `uv run pytest` instead of implying CI has reproduced a stale local count

#### Scenario: Validation wording is updated after CI changes
- **WHEN** the reliability workflow changes the CI-safe test scope
- **THEN** final handoff wording is updated to reflect the new CI/local split before the change is marked ready
