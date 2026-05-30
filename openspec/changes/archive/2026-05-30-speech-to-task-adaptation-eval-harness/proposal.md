## Why

The project already builds a privacy-gated Speech-to-Task seed set and compares rule versus LLM-style normalization, but it does not yet define a held-out adaptation evaluation contract. This change creates the missing bridge between local adaptation data and a later small-model fine-tuning stage without claiming model quality, ASR/TTS quality, or benchmark status.

## What Changes

- Add a local Speech-to-Task adaptation evaluation harness that builds reproducible train/dev/test splits from sanitized trace-derived examples and reviewed variants.
- Define structured metrics for transcript-to-target behavior, including schema validity, output kind accuracy, intent accuracy, required-slot match, safety/clarification accuracy, route readiness, and fallback behavior.
- Compare bounded candidate modes over the same held-out examples: rule normalizer, deterministic mock LLM normalizer, and optionally configured real provider normalizer or future model-output JSONL.
- Emit a local/private evaluation manifest and summary report with provenance, privacy-scan status, split counts, per-mode metrics, failure slices, and explicit non-benchmark positioning.
- Surface the evaluation summary in the demo evidence release pack when provided, without committing generated runtime outputs or raw provider/model data.
- Document how this harness prepares for later LoRA or small-model adaptation while keeping actual training, checkpoints, leaderboard claims, and public raw datasets out of scope.

## Capabilities

### New Capabilities
- `speech-to-task-adaptation-evaluation`: Defines the local/private evaluation harness, split contract, metric definitions, candidate-output comparison, privacy gates, and non-benchmark positioning for Speech-to-Task adaptation readiness.

### Modified Capabilities
- `trace-derived-training-examples`: Extend the dataset contract so the seed-set workflow can produce stable adaptation evaluation splits and provenance needed by the harness.
- `demo-evidence-set`: Extend reviewer handoff so the generated release pack can include a sanitized adaptation-evaluation summary when the local harness output is provided.

## Impact

- Affected scripts: `voice-browser-agent/scripts/build_speech_to_task_dataset.py`, a new evaluation script under `voice-browser-agent/scripts/`, and `voice-browser-agent/scripts/build_demo_evidence_pack.py`.
- Affected tests: focused dataset split, adaptation evaluation, privacy gate, and release-pack integration tests under `voice-browser-agent/tests/`.
- Affected docs: `voice-browser-agent/README.md`, `voice-browser-agent/docs/demo/speech-to-task-dataset.md`, and reviewer evidence documentation.
- Generated outputs remain local under `voice-browser-agent/runtime/` and are not committed.
- No runtime browser execution, ASR/TTS model changes, model fine-tuning, checkpoint publishing, or public benchmark claim is introduced by this change.
