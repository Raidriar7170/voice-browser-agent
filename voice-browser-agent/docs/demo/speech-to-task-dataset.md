# Speech-to-Task Adaptation Dataset

This dataset is local Speech-to-Task adaptation preparation evidence. It turns checked-in sanitized Execution Traces into reviewable examples for later adaptation experiments.

Build it from the committed trace sources:

```bash
uv run python scripts/build_speech_to_task_dataset.py
```

The command writes generated local artifacts under `runtime/speech-to-task-adaptation-dataset/`:

- `runtime/speech-to-task-adaptation-dataset/manifest.json` records example ids, source trace paths, evidence modes, final statuses, validator outcomes, safety flags, correction status, and privacy-scan status.
- `runtime/speech-to-task-adaptation-dataset/examples.jsonl` contains the adaptation-ready example stream with transcript inputs, original target outputs, active target outputs, validator decisions, language metadata, and correction metadata.

Use an optional correction overlay when a reviewed example needs a safer or clearer target:

```bash
uv run python scripts/build_speech_to_task_dataset.py --correction-overlay path/to/corrections.json
```

Build the modest 20-50 example seed set with reviewed variants:

```bash
uv run python scripts/build_speech_to_task_dataset.py --seed-set
uv run python scripts/build_speech_to_task_dataset.py --seed-set --evaluation-splits
```

The seed-set command uses `fixtures/seed-set/reviewed-variants.json` by default. With `--evaluation-splits`, every included example is assigned to exactly one stable split: `train`, `dev`, or `test`. The assignment is based on the example id, not wall-clock time or filesystem traversal order. The manifest separates original trace-derived examples from reviewed variants and records source trace id, source trace path, provenance kind, evidence mode, target output kind, correction or variant status, split, split provenance, and privacy-scan status.

The same sanitized fixture transcripts and reviewed variants can feed local normalizer comparison:

```bash
uv run python scripts/build_normalizer_comparison.py --seed-set
```

That workflow writes `runtime/normalizer-comparison/manifest.json` with source example ids, source trace ids when available, normalizer mode, schema status, validator outcome, fallback state, route readiness, and privacy-scan status. It compares structured-output normalization behavior and stays separate from model training or checkpoint work.

Run the local adaptation evaluation harness against the held-out split:

```bash
uv run python scripts/build_speech_to_task_eval.py \
  --dataset-manifest runtime/speech-to-task-adaptation-dataset/manifest.json
```

The default split is `test`; use `--split dev` for local tuning checks before touching the held-out test split. The built-in candidate modes are `rule` and deterministic `mock_llm`, both using the same structured normalizer and deterministic validator path as the app.

Candidate JSONL from a later local model or provider comparison can be supplied without adding training behavior:

```bash
uv run python scripts/build_speech_to_task_eval.py \
  --candidate-output-jsonl adapted_model=runtime/local-adapter-candidates.jsonl
```

Each candidate JSONL row must match one held-out example id exactly:

```json
{"example_id":"demo_preview:demo-icon-search","output":{"kind":"browser_task_request","task":"Click the toolbar search icon.","intent_type":"click_visual_target","constraints":["controlled demo page only"],"visual_references":[{"kind":"icon","text":"magnifying glass"}],"requires_confirmation":false,"stop_conditions":["login_required"],"safety_flags":[]}}
```

Missing, extra, or duplicate ids are rejected. Malformed `output` payloads become schema-failure evaluation rows so the manifest can count them honestly without treating them as route-ready successes.

The evaluation manifest is written under `runtime/speech-to-task-adaptation-eval/` and includes:

- `schema_valid_rate`: candidate outputs that parse as a browser-task or clarification request.
- `output_kind_accuracy`: candidate output kind versus the active target kind.
- `intent_type_accuracy`: browser-task intent type match where the target has an intent.
- `required_slot_match_rate`: required public-task slot values preserved when present.
- `safety_or_clarification_decision_accuracy`: route-ready, confirmation-required, blocked, or clarification decision category match.
- `route_ready_rate`: candidate rows that are valid browser tasks accepted by the deterministic validator without confirmation.
- `fallback_rate`: candidate rows that used a fallback path.
- `row_count` and split/candidate-mode counts for auditability.

Failure slices are grouped by candidate mode, split, evidence mode, target output kind, intent type, schema status, and safety or clarification category. These slices are meant for debugging adaptation readiness, not leaderboard comparison.

To add the sanitized high-level summary to the reviewer release pack:

```bash
uv run python scripts/build_demo_evidence_pack.py \
  --adaptation-eval-path runtime/speech-to-task-adaptation-eval/manifest.json
```

The release-pack summary includes split counts, candidate modes, high-level metrics, failure slices, source manifest path, privacy-scan status, and local/private positioning. If no eval manifest is passed, the pack says `not_provided` and does not imply the harness was run.

The overlay keeps the original trace-derived target and stores the corrected target separately:

```json
{
  "corrections": [
    {
      "example_id": "demo_preview:demo-icon-search",
      "target_output": {
        "kind": "browser_task_request",
        "task": "Click the toolbar search icon.",
        "intent_type": "click_visual_target",
        "constraints": ["controlled demo page only"],
        "visual_references": [{"kind": "icon", "text": "magnifying glass"}],
        "requires_confirmation": false,
        "stop_conditions": ["login_required"],
        "safety_flags": []
      },
      "reason": "reviewed wording",
      "note": "Keep the original trace target for audit."
    }
  ]
}
```

The generated files stay local. The committed sources remain `fixtures/traces/sanitized/`, `fixtures/traces/live-sanitized/`, `fixtures/traces/agentic-sanitized/`, `fixtures/traces/real-vision-sanitized/`, and `fixtures/seed-set/reviewed-variants.json`.

Privacy gates reject raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, local file URIs, raw prompts, raw provider responses, request headers, API keys, remote host details, checkpoint paths, and unsanitized runtime fields. The harness does not train, fine-tune, load, publish, or score checkpoints.

This is local adaptation-readiness evidence for structured Speech-to-Task behavior. It is not an ASR/TTS corpus, not a fine-tuning run, not a model checkpoint, not checkpoint publication, not public leaderboard ranking, not state-of-the-art evidence, not production readiness, and not broad web-autonomy evidence.
