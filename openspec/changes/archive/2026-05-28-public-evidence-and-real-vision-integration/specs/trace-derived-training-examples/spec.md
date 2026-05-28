## ADDED Requirements

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
