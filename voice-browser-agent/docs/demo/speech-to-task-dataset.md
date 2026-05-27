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
```

The seed-set command uses `fixtures/seed-set/reviewed-variants.json` by default. The manifest separates original trace-derived examples from reviewed variants and records source trace id, evidence mode, correction or variant status, and privacy-scan status.

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

This is not an ASR/TTS corpus, not a model checkpoint, and not broad web-autonomy evidence. It is a small local data contract for the bounded Voice-to-Browser Agent.
