# Closeout Checklist

Use this checklist before archiving or committing the final Voice-to-Browser Agent handoff.

## Generate Local Review Artifacts

```bash
uv run python scripts/preflight_real_use.py
uv run python scripts/generate_real_voice_trace.py
uv run python scripts/run_public_readonly_task_pack.py --all --mode deterministic
uv run python scripts/build_normalizer_comparison.py --seed-set
uv run python scripts/build_demo_evidence_pack.py
uv run python scripts/build_demo_evidence_pack.py --normalizer-comparison-path runtime/normalizer-comparison/manifest.json
uv run python scripts/build_speech_to_task_dataset.py
uv run python scripts/build_speech_to_task_dataset.py --seed-set
```

Inspect:

- `runtime/demo-evidence-release-pack/manifest.json`
- `runtime/demo-evidence-release-pack/index.html`
- `runtime/normalizer-comparison/manifest.json`
- `runtime/public-readonly-task-pack/runs/<run_id>/manifest.json`
- `runtime/speech-to-task-adaptation-dataset/manifest.json`
- `runtime/speech-to-task-adaptation-dataset/examples.jsonl`
- `fixtures/public-readonly-smoke.json`

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
openspec validate real-public-task-completion-evidence --strict
openspec validate --all --strict
uv run pytest
git diff --check
git status --short --ignored
```

Confirm `runtime/`, caches, local upload/recording directories, raw public-readonly traces, screenshots, browser profiles, and generated release packs remain ignored or unstaged.

For the command-first console flow, also inspect one route-aware command run and confirm the response includes `route_decision`, preview-vs-live evidence mode, and sanitized trace export. The controlled GitHub-like showcase trace is `fixtures/traces/live-sanitized/live-github-showcase.json`.

For the public-readonly flow, inspect one completed, partial, stopped, failed, and blocked state. Confirm the console shows task id, task kind, completion criteria, completion state, stop/failure reason, local/private sanitizer state, visible result artifact state when available, and never marks opened-but-incomplete public tasks as successful. For GitHub, confirm controlled showcase and real `github.com` public-readonly evidence are labeled separately.

Confirm the public-readonly reliability matrix appears in the release-pack manifest and index as a bounded local read-only summary. It must not expose raw public runtime traces, screenshots, page text, cookies, credentials, browser profiles, local paths, private data, or remote host details.

Confirm the public-readonly useful task pack appears in the release-pack manifest and index as a local/private metadata summary. It must cover package metadata and release notes without implying broad public-web autonomy, deployed web operation, leaderboard-style ranking, model score claims, captcha bypass, or account workflows.

Confirm the latest public-readonly task-pack runner manifest appears in readiness and, when present, the release-pack manifest/index as local/private evidence. Deterministic runs must be labeled non-network validation evidence; live runs must remain allowlisted, read-only, private-by-default, and honest about stopped, failed, blocked, or partial outcomes.

Confirm normalizer comparison evidence appears in the release-pack manifest and index when `runtime/normalizer-comparison/manifest.json` is supplied. It must be labeled as local structured-output comparison, not model training or a model score, and it must not expose raw prompts, raw provider responses, API keys, request headers, private URLs, local file URIs, remote host details, or unsanitized runtime fields.

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

The closeout MVP is a bounded spoken-command browser execution project. Model fine-tuning, expanded dataset collection, public hosting, verification-barrier bypassing, account workflows, production deployment, ranking tables, leaderboard claims, state-of-the-art claims, and broad public-web automation remain out of scope for this handoff.
