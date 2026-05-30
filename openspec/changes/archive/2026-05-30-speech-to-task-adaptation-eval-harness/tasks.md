## 1. Dataset Split Contract

- [x] 1.1 Add tests for deterministic train/dev/test split metadata in the Speech-to-Task seed-set manifest.
- [x] 1.2 Extend `scripts/build_speech_to_task_dataset.py` with an opt-in evaluation split mode that assigns every included example to exactly one split.
- [x] 1.3 Record split provenance fields for trace-derived and reviewed-variant examples, including source trace id, source trace path, evidence mode, target output kind, correction or variant status, and privacy-scan status.
- [x] 1.4 Add failure coverage for missing held-out splits, duplicate split assignments, omitted examples, and privacy-unsafe split metadata.

## 2. Adaptation Evaluation Harness

- [x] 2.1 Add tests for a new local evaluation script that consumes the seed-set manifest/examples and evaluates rule plus deterministic mock LLM candidates over a held-out split.
- [x] 2.2 Implement `scripts/build_speech_to_task_eval.py` with built-in candidate modes, target parsing, deterministic validation, row-level comparison, and local/private output under `runtime/speech-to-task-adaptation-eval/`.
- [x] 2.3 Implement structured metric calculation for schema-valid rate, output-kind accuracy, intent-type accuracy, required-slot match rate, safety or clarification decision accuracy, route-ready rate, fallback rate, and row counts.
- [x] 2.4 Add failure-slice summaries by candidate mode, split, evidence mode, target output kind, intent type when present, schema status, and safety or clarification category.
- [x] 2.5 Add optional candidate-output JSONL evaluation with strict example-id matching, malformed-output reporting, and no training/checkpoint behavior.
- [x] 2.6 Reuse or extend privacy scans so source examples, candidate JSONL, reports, and manifests reject raw audio paths, raw screenshots, credentials, raw prompts, raw provider responses, request headers, API keys, local file URIs, remote host details, checkpoint paths, and unsanitized runtime fields.

## 3. Release-Pack Integration

- [x] 3.1 Add tests for passing an adaptation-evaluation manifest into `scripts/build_demo_evidence_pack.py`.
- [x] 3.2 Extend the release-pack manifest with split counts, candidate modes, high-level metrics, failure-slice summaries, source manifest path, privacy-scan status, and local/private positioning when the evaluation manifest is provided.
- [x] 3.3 Render a concise adaptation-evaluation section in the release-pack HTML index without implying evaluation ran when no manifest is supplied.
- [x] 3.4 Add release-pack rejection coverage for unsafe adaptation-evaluation evidence fields, including raw provider data, credentials, local paths, remote host details, and checkpoint paths.

## 4. Documentation and Reviewer Framing

- [x] 4.1 Update `README.md` with commands for building the seed set with splits, running local adaptation evaluation, and including the result in the demo evidence pack.
- [x] 4.2 Update `docs/demo/speech-to-task-dataset.md` with split semantics, candidate JSONL format, metric definitions, privacy boundaries, and inspection paths.
- [x] 4.3 Ensure public/reviewer wording states that this is local adaptation-readiness evidence, not model fine-tuning, checkpoint publication, ASR/TTS evaluation, public benchmark ranking, SOTA, production readiness, or broad public-web autonomy.

## 5. Validation

- [x] 5.1 Run focused tests for dataset splits, adaptation evaluation, release-pack integration, and privacy failures.
- [x] 5.2 Run the full project test suite with `uv run pytest` from `voice-browser-agent/`.
- [x] 5.3 Run `OPENSPEC_TELEMETRY=0 openspec validate --all --strict` from the repository root.
- [x] 5.4 Run `git diff --check` and fix any whitespace issues before marking the change ready to apply/archive.
