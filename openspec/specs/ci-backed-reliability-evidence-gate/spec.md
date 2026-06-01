# ci-backed-reliability-evidence-gate Specification

## Purpose
Define the CI-backed reliability gate, dependency strategy, generated snapshot
manifest, privacy checks, and handoff wording that let reviewers reproduce the
bounded Voice-to-Browser Agent evidence contract without widening local/private
runtime claims.

## Requirements
### Requirement: Run CI-backed reliability validation
The project SHALL provide a GitHub Actions reliability workflow that validates the
bounded Voice-to-Browser Agent evidence contract beyond the lightweight
front-door checks.

#### Scenario: Reliability workflow runs on repository changes
- **WHEN** a pull request, push to `main`, or manual workflow dispatch triggers the reliability workflow
- **THEN** the workflow runs OpenSpec strict validation, a CI-safe Python install path, and deterministic project tests that cover schemas, docs, evidence builders, privacy guards, and release-pack contracts

#### Scenario: Reliability workflow reports failures honestly
- **WHEN** OpenSpec validation, dependency installation, tests, or privacy checks fail
- **THEN** the workflow exits non-zero and does not present the reliability gate as passed

### Requirement: Resolve CI dependencies explicitly
The CI reliability gate SHALL define how `browser-use-vision` and browser-related
dependencies are resolved in a standalone GitHub checkout.

#### Scenario: Local sibling dependency is unavailable
- **WHEN** the GitHub Actions checkout does not contain the local editable sibling path for `browser-use-vision`
- **THEN** the workflow uses an explicit CI dependency strategy or an explicitly documented CI-safe test subset instead of relying on the missing local path

#### Scenario: Dependency strategy changes
- **WHEN** the dependency strategy uses a public Git source, local stub, optional extra, or test subset
- **THEN** README or reviewer documentation records what CI validates and what remains local-only validation

### Requirement: Generate a reliability snapshot manifest
The project SHALL provide a local command that builds a machine-readable
reliability snapshot from existing sanitized evidence and optional local/private
runtime manifests.

#### Scenario: Snapshot is generated from available evidence
- **WHEN** the snapshot command runs from the project checkout
- **THEN** it writes a manifest under ignored `runtime/` output with evidence source summaries, validation command provenance, demo trace coverage, visual verification outcome counts, public-readonly task-pack outcome counts, normalizer comparison metrics, Speech-to-Task adaptation evaluation metrics, and privacy-scan status

#### Scenario: Optional local manifests are absent
- **WHEN** normalizer comparison, public-readonly task-pack, Speech-to-Task dataset, or adaptation evaluation runtime manifests are absent
- **THEN** the snapshot records the missing optional evidence as unavailable without fabricating metrics or failing required committed-evidence checks

### Requirement: Preserve private artifact boundaries in reliability outputs
Reliability workflow logs, snapshot manifests, and documentation updates SHALL
exclude raw or local/private artifacts.

#### Scenario: Private marker is detected
- **WHEN** a candidate reliability snapshot, workflow-visible artifact, or public handoff document contains raw audio paths, raw screenshots, browser profile data, cookies, credentials, raw prompts, raw provider responses, local file URIs, private URLs, remote host details, raw public page text, unsanitized runtime fields, or checkpoint-like paths
- **THEN** the validation fails before presenting the evidence as public-safe

#### Scenario: Runtime output is generated
- **WHEN** reliability commands create manifests, logs, release packs, screenshots, or public-readonly runtime traces under `runtime/`
- **THEN** those outputs remain ignored or unstaged unless a separate sanitizer-approved OpenSpec change explicitly promotes a public-safe artifact

### Requirement: Separate CI validation from local-only evidence
The project SHALL distinguish what GitHub Actions validated from what was
generated or inspected locally.

#### Scenario: Reviewer reads validation status
- **WHEN** README, public evidence, closeout checklist, or interview handoff surfaces describe validation
- **THEN** they identify CI-backed checks separately from local commands, optional runtime-generated summaries, and private-by-default evidence paths

#### Scenario: Validation count is stale or unverifiable
- **WHEN** a public handoff surface includes a concrete test count or pass claim
- **THEN** the claim is either generated from fresh validation evidence or avoided in favor of command-based validation wording

### Requirement: Preserve bounded project claims
The reliability gate SHALL reinforce the existing bounded MVP scope instead of
expanding project claims.

#### Scenario: Reliability evidence is summarized
- **WHEN** CI status, reliability snapshots, README badges, release-pack summaries, or handoff pages describe the project
- **THEN** they avoid claims of model fine-tuning, checkpoint release, ASR/TTS benchmarking, production readiness, broad public-web autonomy, account automation, verification-barrier bypassing, public raw evidence release, leaderboard ranking, or state-of-the-art model quality
