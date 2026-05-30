## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Surface adaptation evaluation in final handoff
The project SHALL include the Speech-to-Task adaptation evaluation workflow in final reviewer instructions once the harness exists.

#### Scenario: Reviewer follows final adaptation review path
- **WHEN** a reviewer follows the final closeout checklist or public evidence command list
- **THEN** they can identify commands to build the seed set with evaluation splits, run held-out adaptation evaluation, inspect `runtime/speech-to-task-adaptation-eval/manifest.json`, and optionally include the sanitized evaluation summary in the demo evidence release pack

#### Scenario: Final surfaces describe eval metrics
- **WHEN** final handoff surfaces describe Speech-to-Task adaptation evaluation
- **THEN** they name structured readiness metrics such as schema-valid rate, output-kind accuracy, intent-type accuracy, required-slot match rate, safety or clarification decision accuracy, route-ready rate, fallback rate, row counts, and failure slices
