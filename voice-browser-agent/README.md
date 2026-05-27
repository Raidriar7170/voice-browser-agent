# Voice-to-Browser Agent

Standalone bounded Chinese-first Voice-to-Browser Agent demo. It accepts one uploaded or recorded spoken command, transcribes it, normalizes it into a structured browser task or clarification request, applies deterministic safety gates, runs bounded browser execution with visual grounding, and writes sanitized traces for review.

This is a scoped demo application project, not a `browser-use-vision` voice extension, public ranking claim, or broad autonomous assistant.

## Quickstart

```bash
uv sync --extra dev
uv run uvicorn voice_browser_agent.app:app --reload
```

Open `http://127.0.0.1:8000`, upload a supported audio file, or paste one of the fixture transcripts from `fixtures/audio/*.fixture.json`.

The local visual grounding dependency is resolved by `uv` from `../../../browser-use-vision` through `[tool.uv.sources]`. If the repo lives elsewhere, edit that path or install `browser-use-vision` into the environment before running non-demo vision checks.

## Runtime

- The Operator Console and browser execution run locally.
- `browser-use-vision` is imported as a dependency and remains the Visual Grounding Engine.
- Heavy ASR or visual inference can be configured through optional remote service URLs in `.env`.
- Raw recordings, private traces, live browser screenshots, credentials, checkpoints, and remote host details stay out of version control.
- JSON fixture manifests are replayed through `/api/fixtures/{fixture_id}/executions`; they are not raw audio uploads.
- `VOICE_BROWSER_DEMO_DRY_RUN=true` records an explicit stopped preview trace. Disable it only when a real browser-use/browser-use-vision executor backend is configured.
- Trace-derived training examples can be created from sanitized Execution Traces for later Speech-to-Task Adaptation. This is not a fine-tuning pipeline or model result claim.

## Demo Evidence

- Demo tasks: `docs/demo/demo-task-suite.md`
- Ablations: `docs/demo/ablations.md`
- Video plan: `docs/demo/video-plan.md`
- Closeout checklist: `docs/demo/closeout-checklist.md`
- Interview overview: `docs/interview-project-overview.html`
- Public evidence page: `docs/public-evidence/index.html`
- Sanitized trace artifacts: `fixtures/traces/sanitized/`
- Live controlled trace artifacts: `fixtures/traces/live-sanitized/`
- Agentic live controlled trace artifacts: `fixtures/traces/agentic-sanitized/`
- Real browser-use-vision controlled trace artifacts: `fixtures/traces/real-vision-sanitized/`

The public artifacts show bounded spoken-command execution, explicit safety stops, and traceable evidence. Demo-preview traces are separate from live controlled and agentic live controlled traces. They do not claim broad web autonomy.

Refresh the committed real-vision controlled trace when the local Playwright browser and editable `browser-use-vision` dependency are available:

```bash
uv run python scripts/generate_real_vision_trace.py
```

Build the reviewer release pack from the committed evidence sources:

```bash
uv run python scripts/build_demo_evidence_pack.py
```

The command writes a generated local artifact under `runtime/demo-evidence-release-pack/`. Open `runtime/demo-evidence-release-pack/index.html` for the browser-readable evidence index, or inspect `runtime/demo-evidence-release-pack/manifest.json` for the machine-readable manifest. The generated directory stays local; the committed evidence sources remain `fixtures/traces/sanitized/`, `fixtures/traces/live-sanitized/`, `fixtures/traces/agentic-sanitized/`, and `fixtures/traces/real-vision-sanitized/`.

Build the local Speech-to-Task adaptation preparation dataset from the same committed trace sources:

```bash
uv run python scripts/build_speech_to_task_dataset.py
```

The command writes `runtime/speech-to-task-adaptation-dataset/manifest.json` and `runtime/speech-to-task-adaptation-dataset/examples.jsonl`. Use `--correction-overlay path/to/corrections.json` for reviewed target corrections; the original trace-derived target stays in the generated example. Use `--seed-set` to produce the 20-50 example local seed set from trace-derived examples plus `fixtures/seed-set/reviewed-variants.json`. See `docs/demo/speech-to-task-dataset.md` for the overlay format and inspection path. This dataset is local Speech-to-Task adaptation preparation evidence, not a model result or broad autonomy claim.

## Operator Console Demo Flow

Use the console as three separate execution paths:

- Transcript demo: paste a fixture transcript or short spoken-command text, then run the transcript path to show normalization, validation, clarification, confirmation, or preview evidence.
- Fixture replay: select a fixture and execution mode, then run the fixture path to reproduce checked-in demo-preview traces or selected controlled local visual tasks.
- Uploaded audio: upload or record one command, verify the stored `audio_id`, then run the audio path to execute the ingested transcript through the same safety and trace pipeline.

Use `demo_preview` for public showcase tasks such as GitHub or OpenAI pages. Use `live_controlled` only for fixtures explicitly selected for local controlled pages, such as icon search, color swatch, and SVG dashboard evidence. Clarification examples should stop before browser execution, confirmation examples should show the operator prompt before continuing, and exported traces must remain sanitized.
