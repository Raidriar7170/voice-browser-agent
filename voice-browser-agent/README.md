# Voice-to-Browser Agent

Bounded Chinese-first Voice-to-Browser Agent demo. It accepts one uploaded or recorded spoken command, transcribes it, normalizes it into a structured browser task or clarification request, applies deterministic safety gates, runs bounded browser execution with visual grounding, and writes sanitized traces for review.

This is a scoped demo, not a public ranking claim, production automation platform, or unrestricted autonomous assistant.

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

## Demo Evidence

- Demo tasks: `docs/demo/demo-task-suite.md`
- Ablations: `docs/demo/ablations.md`
- Video plan: `docs/demo/video-plan.md`
- Sanitized trace artifacts: `fixtures/traces/sanitized/`
- Live controlled trace artifacts: `fixtures/traces/live-sanitized/`

The public artifacts show bounded spoken-command execution, explicit safety stops, and traceable evidence. Demo-preview traces are separate from live controlled traces. They do not claim unrestricted web autonomy.
