# trace-derived-training-examples Specification

## Purpose
Defines how sanitized Execution Trace content plus optional human correction can become Speech-to-Task training examples for later adaptation work without committing raw private traces, raw audio, browser state, checkpoints, or benchmark claims.
## Requirements
### Requirement: Create trace-derived training examples
The system SHALL convert an Execution Trace with transcript and normalized output into a sanitized Trace-Derived Training Example for later Speech-to-Task Adaptation.

#### Scenario: Browser task trace becomes training example
- **WHEN** an Execution Trace contains an ASR transcript, Browser Task Request, validator decision, and final status
- **THEN** the derived example includes the source execution id, transcript text, normalized output payload, validator outcome, final status, safety flags, and optional human correction

#### Scenario: Clarification trace becomes training example
- **WHEN** an Execution Trace contains an ASR transcript and Clarification Request
- **THEN** the derived example preserves the clarification reason and question as the target output instead of inventing a browser task

### Requirement: Preserve privacy in trace-derived examples
Trace-Derived Training Examples SHALL exclude raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, and unsanitized live browser state.

#### Scenario: Trace contains private nested fields
- **WHEN** a trace-derived example is created from a trace containing private nested fields
- **THEN** those private fields are omitted from the example payload

#### Scenario: Trace lacks required adaptation inputs
- **WHEN** an Execution Trace has no transcript or no normalized output
- **THEN** the system rejects training example creation with an explicit reason instead of producing a partial example

### Requirement: Build curated Speech-to-Task adaptation dataset
The system SHALL build a local Speech-to-Task adaptation dataset from checked-in sanitized Execution Trace artifacts.

#### Scenario: Dataset is generated from sanitized traces
- **WHEN** the dataset workflow is run from the project checkout
- **THEN** it creates a dataset directory containing a machine-readable manifest and JSONL examples derived only from checked-in sanitized trace sources

#### Scenario: Dataset records source provenance
- **WHEN** a trace-derived example is included in the dataset
- **THEN** the manifest records a stable example id, source execution id, source trace path, evidence mode, final status, validator outcome when present, safety flags, and privacy-scan status

#### Scenario: Release-pack manifest is available
- **WHEN** the demo evidence release-pack manifest is provided as an input
- **THEN** the dataset workflow uses it as provenance context without requiring generated release artifacts to be committed

### Requirement: Preserve original and corrected adaptation targets
The dataset workflow SHALL preserve the original trace-derived target and any human correction as separate auditable fields.

#### Scenario: Correction overlay is applied
- **WHEN** a human correction overlay contains a correction for an included example
- **THEN** the exported example includes the original target output, corrected target output, correction reason or note, and correction status without mutating the source trace

#### Scenario: No correction is provided
- **WHEN** an included example has no correction overlay entry
- **THEN** the exported example marks the correction status as absent and keeps the original trace-derived target as the active target

#### Scenario: Correction references unknown example
- **WHEN** a correction overlay references an execution id or example id that is not included in the dataset
- **THEN** the workflow exits non-zero with a clear reason naming the unknown correction target

### Requirement: Gate dataset privacy and quality
The dataset workflow SHALL fail when source traces, correction overlays, or generated dataset files are missing required adaptation data, malformed, duplicated, or privacy-unsafe.

#### Scenario: Trace lacks adaptation inputs
- **WHEN** a candidate trace lacks an ASR transcript or normalized output
- **THEN** the workflow exits non-zero with a clear reason naming the source trace

#### Scenario: Duplicate example id is detected
- **WHEN** two candidate traces or correction entries resolve to the same stable example id
- **THEN** the workflow exits non-zero with a clear duplicate-id reason

#### Scenario: Private marker is detected
- **WHEN** a source trace, correction overlay, manifest, or JSONL example contains raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, local file URIs, or unsanitized runtime fields
- **THEN** the workflow exits non-zero and does not present the dataset as adaptation-ready

### Requirement: Document bounded dataset use
The project SHALL document the adaptation dataset as local Speech-to-Task preparation evidence rather than a public benchmark or model-quality claim.

#### Scenario: Reviewer reads dataset documentation
- **WHEN** a reviewer reads the README or demo documentation for the dataset workflow
- **THEN** the documentation explains how to build and inspect the dataset and states that it is not an ASR/TTS corpus, benchmark leaderboard, production automation dataset, model checkpoint, or unrestricted public-web autonomy claim

### Requirement: Build modest Speech-to-Task adaptation seed set
The project SHALL provide a local workflow or documented command that produces a modest Speech-to-Task adaptation seed set from sanitized trace-derived examples plus reviewed variants or corrections.

#### Scenario: Seed set is generated
- **WHEN** the seed-set workflow is run from the project checkout
- **THEN** it produces a local manifest and example stream containing between 20 and 50 examples derived from committed sanitized evidence sources or reviewed correction/variant overlays

#### Scenario: Seed set distinguishes provenance
- **WHEN** the seed-set manifest lists examples
- **THEN** it distinguishes original trace-derived examples from reviewed variants and records source trace id, evidence mode, correction or variant status, and privacy-scan status

### Requirement: Provide correction or variant overlay example
The project SHALL include a small reviewed correction or variant overlay example for Speech-to-Task adaptation preparation.

#### Scenario: Overlay is applied
- **WHEN** the dataset or seed-set workflow uses the overlay
- **THEN** exported examples preserve original trace-derived targets, active targets, overlay reasons, and overlay status without mutating source traces

#### Scenario: Overlay is unsafe
- **WHEN** the overlay contains credentials, private URLs, raw audio paths, raw screenshot paths, local file URIs, remote host details, or browser profile data
- **THEN** the workflow fails and does not present the seed set as adaptation-ready

### Requirement: Preserve bounded dataset positioning
The seed set SHALL be documented as local Speech-to-Task adaptation preparation evidence, not as a trained model, public benchmark corpus, or model-quality result.

#### Scenario: Reviewer reads seed-set documentation
- **WHEN** a reviewer reads the README, dataset docs, or public evidence page
- **THEN** the documentation states that the seed set is small, local, privacy-gated, and does not include model fine-tuning, checkpoint publication, broad public-web automation, or ASR/TTS quality claims
