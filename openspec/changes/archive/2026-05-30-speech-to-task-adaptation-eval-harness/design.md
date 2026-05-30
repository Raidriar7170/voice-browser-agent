## Context

The repository already has the data side of Speech-to-Task Adaptation: sanitized execution traces, trace-derived training examples, a 20-50 example seed-set workflow, reviewed variants, and a local normalizer comparison report. The recent LLM structured normalizer and visual verification work also give the project a credible end-to-end agent story.

The remaining gap is measurement. Before introducing LoRA, checkpoints, or A100 training, the project needs a local evaluation harness that answers: "Can a candidate transcript-to-structured-task mapper match the reviewed target contract on held-out examples?" The harness should be small, deterministic, privacy-gated, and reviewer-readable.

## Goals / Non-Goals

**Goals:**

- Produce deterministic train/dev/test splits from the existing sanitized Speech-to-Task seed examples.
- Evaluate candidate outputs against active targets with structured metrics that reflect the actual browser-task contract.
- Compare rule, deterministic mock LLM, optionally configured real provider, and future model-output JSONL candidates over the same held-out examples.
- Emit local/private evaluation artifacts suitable for the demo evidence pack and interview explanation.
- Preserve current project positioning: adaptation readiness evidence, not a benchmark, not model-quality proof, and not ASR/TTS evaluation.

**Non-Goals:**

- Do not train, fine-tune, publish, or load a model checkpoint in this change.
- Do not add GPU/A100 execution, remote training orchestration, or dataset collection.
- Do not commit generated runtime artifacts, raw provider responses, raw prompts, private transcripts, audio, screenshots, or local runtime paths.
- Do not change browser execution behavior, visual verification behavior, or public-readonly task execution.

## Decisions

### Decision: Keep splits in the dataset workflow

The existing dataset builder already owns trace-derived examples, reviewed variants, provenance, and privacy scanning. It should also produce stable split metadata when the operator asks for an evaluation-ready seed set.

Alternatives considered:
- A separate split builder. Rejected because it would duplicate provenance and privacy logic.
- Random split at evaluation time. Rejected because reviewers need stable, auditable splits.

### Decision: Use target-contract metrics instead of text-only accuracy

The harness should compare candidate output to the active target as structured data. Metrics should include schema validity, output kind accuracy, intent type accuracy, required-slot match, safety or clarification decision accuracy, route-ready rate, fallback rate, and failure slices by evidence mode and target kind.

Alternatives considered:
- Exact JSON match only. Rejected because it hides useful partial structure and over-penalizes harmless ordering differences.
- Natural-language similarity. Rejected because the project value is structured browser-task reliability, not text generation.

### Decision: Support candidate JSONL as a future model boundary

The harness should accept optional candidate-output JSONL for later small-model or LoRA outputs. This keeps the current change training-free while making the next phase straightforward.

Alternatives considered:
- Build training and evaluation together. Rejected because it would make the stage too large and risk overclaiming.
- Only evaluate in-process normalizers. Rejected because it would not prepare the project for a later adapted-model comparison.

### Decision: Keep generated evaluation artifacts local/private

Evaluation outputs should live under `runtime/speech-to-task-adaptation-eval/` and can be summarized by the release-pack builder when explicitly passed in. Committed specs, docs, and tests define the contract; generated reports stay local.

Alternatives considered:
- Commit the generated evaluation manifest. Rejected because it could drift and may later contain provider or model-output metadata.
- Publish scores as a benchmark table. Rejected because the dataset is small and portfolio-oriented, not a public benchmark.

## Risks / Trade-offs

- Small dataset risk -> Keep metrics framed as adaptation readiness evidence and include split counts plus failure slices instead of broad claims.
- Metric brittleness -> Normalize target fields and report both strict and field-level matches where useful.
- Provider privacy risk -> Reuse existing forbidden-marker scans and reject raw prompts, raw provider responses, credentials, request headers, local paths, remote host details, and private artifacts.
- Future model drift -> Candidate JSONL provides a stable interface so later LoRA outputs can be evaluated without changing the harness contract.
- Scope creep into training -> Specs and docs explicitly state that training, checkpoints, and model-quality claims are out of scope.
