# speech-to-task-adaptation-evaluation Specification

## Purpose
Defines the local Speech-to-Task adaptation evaluation harness for deterministic seed-set splits, candidate-output comparison, structured readiness metrics, failure slicing, privacy gates, and non-benchmark positioning.
## Requirements
### Requirement: Build Speech-to-Task adaptation evaluation splits
The system SHALL build deterministic local evaluation splits from sanitized Speech-to-Task seed examples and reviewed variants.

#### Scenario: Evaluation splits are generated
- **WHEN** the adaptation evaluation split workflow is run from the project checkout
- **THEN** it produces train, dev, and test split metadata with stable example ids, source trace provenance, target kind counts, evidence mode counts, and privacy-scan status

#### Scenario: Split generation is repeated
- **WHEN** the same checked-in source examples and split configuration are used across runs
- **THEN** the generated split assignments remain stable without depending on wall-clock time or filesystem ordering

### Requirement: Evaluate candidate Speech-to-Task outputs
The system SHALL evaluate candidate transcript-to-structured-task outputs against the active target outputs from the held-out adaptation examples.

#### Scenario: Built-in normalizer candidate is evaluated
- **WHEN** the evaluation harness runs a built-in candidate mode such as rule or deterministic mock LLM over a held-out split
- **THEN** it records candidate output kind, schema status, validator outcome, route readiness, fallback state, and comparison results for each evaluated example

#### Scenario: Candidate JSONL is evaluated
- **WHEN** the evaluation harness receives a candidate-output JSONL file for a future adapted model or external provider
- **THEN** it evaluates the provided outputs against the same held-out example ids without training, loading, publishing, or claiming a model checkpoint

#### Scenario: Candidate output is malformed
- **WHEN** a candidate output cannot be parsed as a Browser Task Request or Clarification Request
- **THEN** the evaluation row records a schema failure and excludes the row from route-ready success metrics while preserving the failure reason

### Requirement: Report structured adaptation metrics
The evaluation harness SHALL report metrics that reflect structured browser-task readiness rather than text-only similarity.

#### Scenario: Evaluation manifest is written
- **WHEN** evaluation completes
- **THEN** the manifest includes split counts, candidate modes, schema-valid rate, output-kind accuracy, intent-type accuracy, required-slot match rate, safety or clarification decision accuracy, route-ready rate, fallback rate, and row counts

#### Scenario: Failure slices are reported
- **WHEN** evaluation rows contain failures or mismatches
- **THEN** the summary reports failure slices by candidate mode, split, evidence mode, target output kind, intent type when present, schema status, and safety or clarification category

### Requirement: Preserve adaptation evaluation privacy and provenance
The evaluation harness SHALL keep generated evaluation artifacts local/private and SHALL reject privacy-unsafe inputs or outputs.

#### Scenario: Private marker is detected
- **WHEN** source examples, candidate JSONL, manifests, reports, or row-level artifacts contain raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, local file URIs, raw prompts, raw provider responses, request headers, API keys, remote host details, or unsanitized runtime fields
- **THEN** the harness exits non-zero or excludes the unsafe artifact before presenting evaluation results

#### Scenario: Evaluation row is generated
- **WHEN** an evaluation row is written
- **THEN** it records source example id, source trace id when available, split name, candidate mode, target output kind, candidate output kind, metric decisions, validator metadata, route readiness, and privacy-scan status without exposing raw private provider or runtime data

### Requirement: Keep adaptation evaluation separate from model training
The project SHALL present the evaluation harness as local adaptation-readiness evidence, not as model fine-tuning, checkpoint publication, public benchmark scoring, ASR/TTS quality evaluation, or production-readiness proof.

#### Scenario: Reviewer reads evaluation documentation
- **WHEN** README, dataset docs, release-pack index, public evidence page, closeout checklist, or interview materials describe adaptation evaluation
- **THEN** they state that the harness evaluates structured Speech-to-Task outputs on a small local seed set and does not train, fine-tune, publish checkpoints, claim benchmark ranking, evaluate ASR/TTS quality, prove production readiness, or prove broad public-web autonomy

#### Scenario: Future model outputs are compared
- **WHEN** candidate JSONL from a later adapted model is evaluated
- **THEN** the harness labels the result as local/private comparison evidence and does not present it as a public leaderboard or production model-quality claim

#### Scenario: Fine-tuning is discussed
- **WHEN** final handoff materials mention future fine-tuning
- **THEN** they describe it as a separate future project or later scoped change that consumes exported seed/evaluation data rather than as completed work in the closeout MVP

### Requirement: Surface adaptation evaluation in final handoff
The project SHALL include the Speech-to-Task adaptation evaluation workflow in final reviewer instructions once the harness exists.

#### Scenario: Reviewer follows final adaptation review path
- **WHEN** a reviewer follows the final closeout checklist or public evidence command list
- **THEN** they can identify commands to build the seed set with evaluation splits, run held-out adaptation evaluation, inspect `runtime/speech-to-task-adaptation-eval/manifest.json`, and optionally include the sanitized evaluation summary in the demo evidence release pack

#### Scenario: Final surfaces describe eval metrics
- **WHEN** final handoff surfaces describe Speech-to-Task adaptation evaluation
- **THEN** they name structured readiness metrics such as schema-valid rate, output-kind accuracy, intent-type accuracy, required-slot match rate, safety or clarification decision accuracy, route-ready rate, fallback rate, row counts, and failure slices
