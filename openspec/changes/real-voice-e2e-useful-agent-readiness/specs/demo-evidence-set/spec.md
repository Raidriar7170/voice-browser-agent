## ADDED Requirements

### Requirement: Include real-use evidence mode
The evidence pack SHALL include a distinct `real_voice_controlled` evidence mode for sanitized traces that start from real uploaded or recorded audio.

#### Scenario: Release pack includes real voice evidence
- **WHEN** the release-pack workflow finds a sanitized real voice controlled trace
- **THEN** the manifest and HTML index classify it as `real_voice_controlled` and include input source, ASR adapter metadata, transcript review status, final status, grounding references, and privacy-scan status

#### Scenario: Required real voice evidence is missing
- **WHEN** final real-use evidence validation runs without the required sanitized real voice controlled trace
- **THEN** it fails with a clear missing real voice evidence reason

### Requirement: Include useful local scenario pack
The project SHALL document and evidence a small set of local useful scenarios that are closer to real workflows than one-off visual demos while staying controlled and non-destructive.

#### Scenario: Useful scenarios are listed
- **WHEN** a reviewer opens the scenario documentation
- **THEN** it lists local CRM, settings, dashboard, or similar controlled scenarios with user intent, browser intent type, expected safety behavior, evidence mode, and privacy boundary

### Requirement: Preserve failure and usage traces
The evidence set SHALL include sanitized traces for representative real-use failures and operator decisions.

#### Scenario: Failure traces are packaged
- **WHEN** the release-pack workflow builds real-use evidence
- **THEN** it includes or references sanitized traces for ASR unavailable, clarification required, confirmation pending or cancelled, ambiguous visual target, and successful real voice controlled execution

#### Scenario: Failure evidence avoids overclaiming
- **WHEN** public evidence docs describe failure and usage traces
- **THEN** they explain that failures are reliability evidence, not benchmark scores, production automation claims, ASR/TTS quality claims, or unrestricted autonomy claims
