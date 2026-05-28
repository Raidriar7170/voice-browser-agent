# Closeout Checklist

Use this checklist before archiving or committing the final Voice-to-Browser Agent handoff.

## Generate Local Review Artifacts

```bash
uv run python scripts/preflight_real_use.py
uv run python scripts/generate_real_voice_trace.py
uv run python scripts/build_demo_evidence_pack.py
uv run python scripts/build_speech_to_task_dataset.py
uv run python scripts/build_speech_to_task_dataset.py --seed-set
```

Inspect:

- `runtime/demo-evidence-release-pack/manifest.json`
- `runtime/demo-evidence-release-pack/index.html`
- `runtime/speech-to-task-adaptation-dataset/manifest.json`
- `runtime/speech-to-task-adaptation-dataset/examples.jsonl`

Generated runtime artifacts stay local. The committed evidence sources are:

- `fixtures/traces/sanitized/`
- `fixtures/traces/live-sanitized/`
- `fixtures/traces/agentic-sanitized/`
- `fixtures/traces/real-vision-sanitized/`
- `fixtures/traces/real-voice-sanitized/`
- `fixtures/traces/real-use-sanitized/`
- `fixtures/seed-set/reviewed-variants.json`

## Validate Repo State

```bash
openspec validate project-closeout-interview-pack --strict
openspec validate public-evidence-and-real-vision-integration --strict
openspec validate real-voice-e2e-useful-agent-readiness --strict
openspec validate --all --strict
uv run pytest
git diff --check
git status --short --ignored
```

Confirm `runtime/`, caches, and local upload/recording directories remain ignored.

For the command-first console flow, also inspect one route-aware command run and confirm the response includes `route_decision`, preview-vs-live evidence mode, and sanitized trace export. The controlled GitHub-like showcase trace is `fixtures/traces/live-sanitized/live-github-showcase.json`.

## Archive Order

Confirm `speech-to-task-adaptation-dataset` has already been archived before archiving `project-closeout-interview-pack`.

Recommended final sequence:

```text
/opsx:archive project-closeout-interview-pack
```

## Reviewer Path

1. Read `README.md`.
2. Open `docs/interview-project-overview.html` in a browser.
3. Open `docs/public-evidence/index.html`.
4. Review `docs/demo/demo-task-suite.md`, `docs/demo/useful-scenarios.md`, `docs/demo/ablations.md`, and `docs/demo/video-plan.md`.
5. Build the release pack and dataset with the commands above.
6. Inspect the generated manifests and confirm they point back to committed sanitized trace sources.

## Boundaries

The closeout MVP is a bounded spoken-command browser execution project. Model fine-tuning, expanded dataset collection, public hosting, and broad public-web automation remain out of scope for this handoff.
