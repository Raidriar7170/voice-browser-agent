## ADDED Requirements

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
