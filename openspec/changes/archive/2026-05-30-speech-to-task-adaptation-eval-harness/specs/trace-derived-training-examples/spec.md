## ADDED Requirements

### Requirement: Produce stable adaptation evaluation splits
The Speech-to-Task seed-set workflow SHALL provide deterministic split metadata suitable for local adaptation evaluation.

#### Scenario: Seed set includes evaluation split metadata
- **WHEN** the seed-set workflow is run with evaluation split output enabled
- **THEN** the generated manifest records train, dev, and test split assignments for every included trace-derived or reviewed-variant example

#### Scenario: Split provenance is recorded
- **WHEN** an example is assigned to an evaluation split
- **THEN** the manifest records the example id, source trace id when available, source trace path, provenance kind, evidence mode, target output kind, correction or variant status, and privacy-scan status

#### Scenario: Split assignment is invalid
- **WHEN** split generation would omit an included example, assign an example to multiple splits, or produce an empty held-out split
- **THEN** the workflow exits non-zero with a clear split validation reason

### Requirement: Preserve adaptation split positioning
The dataset and seed-set documentation SHALL describe generated splits as local adaptation evaluation inputs rather than a benchmark corpus or model-training result.

#### Scenario: Reviewer reads split documentation
- **WHEN** README, dataset docs, public evidence docs, or generated local manifests reference the train, dev, or test split
- **THEN** they state that the split is a small local Speech-to-Task adaptation evaluation input and does not constitute a public benchmark dataset, model checkpoint, ASR/TTS corpus, or broad public-web autonomy claim
