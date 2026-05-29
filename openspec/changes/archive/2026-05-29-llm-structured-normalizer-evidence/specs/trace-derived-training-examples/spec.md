## ADDED Requirements

### Requirement: Reuse sanitized seed examples for normalizer comparison
The Speech-to-Task seed-set workflow SHALL provide or feed bounded examples suitable for local normalizer comparison without changing their adaptation-preparation positioning.

#### Scenario: Seed examples are used for comparison
- **WHEN** the normalizer comparison workflow consumes trace-derived examples or reviewed variants
- **THEN** it uses only sanitized transcript inputs, original targets, corrected or active targets, provenance ids, safety flags, and validator metadata needed to compare normalizer behavior

#### Scenario: Seed examples remain adaptation evidence
- **WHEN** docs or generated reports reference seed examples used for normalizer comparison
- **THEN** they still describe the seed set as local Speech-to-Task adaptation preparation evidence rather than a public benchmark corpus, trained model, or model-quality result

### Requirement: Preserve comparison privacy and provenance
The comparison workflow SHALL preserve source provenance and privacy boundaries when using trace-derived examples.

#### Scenario: Comparison row is generated from a trace-derived example
- **WHEN** a comparison row is produced from a sanitized trace-derived example or reviewed variant
- **THEN** it records source example id, source trace id when available, variant or correction status, normalizer mode, schema status, validator outcome, and privacy-scan status

#### Scenario: Unsafe comparison input is detected
- **WHEN** a trace-derived example, reviewed variant, or comparison artifact contains raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, local file URIs, private data, remote host details, or unsanitized runtime fields
- **THEN** the workflow exits non-zero or excludes the row with a clear privacy reason before presenting comparison evidence

### Requirement: Keep comparison separate from model training
The project SHALL keep normalizer comparison artifacts separate from any model fine-tuning or checkpoint workflow.

#### Scenario: Reviewer inspects comparison docs
- **WHEN** README, dataset docs, public evidence page, release-pack index, or interview overview describe normalizer comparison
- **THEN** they state that the workflow compares structured-output normalization behavior and does not train, fine-tune, publish, or evaluate a model checkpoint
