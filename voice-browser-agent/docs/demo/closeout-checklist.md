# Closeout Checklist

Use this checklist before archiving or committing the final Voice-to-Browser Agent handoff. Archived change names are historical context, not validation targets; final validation uses the current main-spec suite.

## CI and Local Evidence Boundary

Confirm `.github/workflows/front-door.yml` and `.github/workflows/reliability.yml`
are described separately in handoff docs. The reliability workflow runs
OpenSpec strict validation and a CI-safe pytest subset for deterministic docs,
schemas, evidence builders, privacy guards, and release-pack contracts.

The CI-safe pytest subset is not live public browsing, not recorded-audio, not real-provider inference, and not model training. Full browser, real audio,
optional provider, live public-readonly, and full `uv run pytest` checks remain
local/private unless a future change makes them deterministic and CI-safe.

## Generate Local Review Artifacts

```bash
uv run python scripts/build_reliability_snapshot.py
uv run python scripts/preflight_real_use.py
uv run python scripts/generate_agentic_traces.py
uv run python scripts/generate_real_voice_trace.py
uv run python scripts/run_public_readonly_task_pack.py --all --mode deterministic
uv run python scripts/build_normalizer_comparison.py --seed-set
uv run python scripts/build_speech_to_task_dataset.py --seed-set --evaluation-splits
uv run python scripts/build_speech_to_task_eval.py \
  --dataset-manifest runtime/speech-to-task-adaptation-dataset/manifest.json
uv run python scripts/build_demo_evidence_pack.py
uv run python scripts/build_demo_evidence_pack.py \
  --normalizer-comparison-path runtime/normalizer-comparison/manifest.json \
  --adaptation-eval-path runtime/speech-to-task-adaptation-eval/manifest.json
```

Inspect:

- `runtime/reliability-snapshot/manifest.json`
- `runtime/demo-evidence-release-pack/manifest.json`
- `runtime/demo-evidence-release-pack/index.html`
- `runtime/normalizer-comparison/manifest.json`
- `runtime/public-readonly-task-pack/runs/<run_id>/manifest.json`
- `runtime/speech-to-task-adaptation-dataset/manifest.json`
- `runtime/speech-to-task-adaptation-dataset/examples.jsonl`
- `runtime/speech-to-task-adaptation-eval/manifest.json`
- `runtime/speech-to-task-adaptation-eval/summary.json`
- `fixtures/public-readonly-smoke.json`
- `fixtures/public-readonly-useful-task-pack.json`

Generated runtime artifacts stay local. The committed evidence sources are:

- `fixtures/traces/sanitized/`
- `fixtures/traces/live-sanitized/`
- `fixtures/traces/agentic-sanitized/`
- `fixtures/traces/real-vision-sanitized/`
- `fixtures/traces/real-voice-sanitized/`
- `fixtures/traces/real-use-sanitized/`
- `fixtures/seed-set/reviewed-variants.json`
- `fixtures/public-readonly-smoke.json`
- `fixtures/public-readonly-useful-task-pack.json`

## Validate Repo State

```bash
OPENSPEC_TELEMETRY=0 openspec validate --all --strict
CI_SAFE_PYTEST_TARGETS="tests/test_reliability_ci_gate.py tests/test_reliability_snapshot.py tests/test_demo_evidence.py tests/test_demo_evidence_release_pack.py tests/test_normalizer_comparison.py tests/test_public_readonly_task_pack_runner.py tests/test_speech_to_task_dataset_builder.py tests/test_speech_to_task_eval.py"
python -m pytest $CI_SAFE_PYTEST_TARGETS
uv run pytest
git diff --check
git status --short --ignored
```

Confirm `runtime/`, caches, local upload/recording directories, raw public-readonly traces, screenshots, browser profiles, generated release packs, generated comparison reports, generated adaptation datasets, generated adaptation evaluation reports, and checkpoint-like outputs remain ignored or unstaged.

For the command-first console flow, inspect one route-aware command run and confirm the response includes `route_decision`, preview-vs-live evidence mode, and sanitized trace export. The controlled GitHub-like showcase trace is `fixtures/traces/live-sanitized/live-github-showcase.json`.

For the public-readonly flow, inspect one completed, partial, stopped, failed, and blocked state. Confirm the console shows task id, task kind, completion criteria, completion state, stop/failure reason, local/private sanitizer state, visible result artifact state when available, and never marks opened-but-incomplete public tasks as successful. For GitHub, confirm controlled showcase and real `github.com` public-readonly evidence are labeled separately.

Confirm the public-readonly reliability matrix appears in the release-pack manifest and index as a bounded local read-only summary. It must not expose raw public runtime traces, screenshots, page text, cookies, credentials, browser profiles, local paths, private data, or remote host details.

Confirm the public-readonly useful task pack appears in the release-pack manifest and index as a local/private metadata summary. It must cover package metadata and release notes without implying broad public-web autonomy, deployed web operation, leaderboard-style ranking, model score claims, captcha bypass, or account workflows.

Confirm the latest public-readonly task-pack runner manifest appears in readiness and, when present, the release-pack manifest/index as local/private evidence. Deterministic runs must be labeled non-network validation evidence; live runs must remain allowlisted, read-only, private-by-default, and honest about stopped, failed, blocked, or partial outcomes.

Confirm normalizer comparison evidence appears in the release-pack manifest and index when `runtime/normalizer-comparison/manifest.json` is supplied. It must be labeled as local structured-output comparison, not model training or a model score, and it must not expose raw prompts, raw provider responses, API keys, request headers, private URLs, local file URIs, remote host details, or unsanitized runtime fields.

Confirm Speech-to-Task adaptation evaluation appears in the release-pack manifest and index when `runtime/speech-to-task-adaptation-eval/manifest.json` is supplied. It must be labeled as local adaptation-readiness evidence over a small seed set, not fine-tuning, not checkpoint publication, not ASR/TTS evaluation, not public leaderboard ranking, not production readiness, and not broad public-web autonomy evidence. The summary should include split counts, candidate modes, schema-valid rate, output-kind accuracy, intent-type accuracy, required-slot match rate, safety or clarification decision accuracy, route-ready rate, fallback rate, row counts, failure slices, source manifest path, and privacy-scan status.

Confirm visual verification loop evidence appears in the release-pack manifest and index. It must summarize passed, failed, and uncertain outcomes; verified fixture ids; recovery count; failed or uncertain reasons; source trace paths; and privacy-scan status. The default verifier is keyless deterministic over controlled local pages. Real VLM/provider verification is optional and local/private, and raw screenshots, raw annotated images, provider-private payloads, credentials, local paths, and remote host details must not appear in release evidence.

## Reviewer Path

1. Read `README.md`.
2. Open `docs/interview-project-overview.html` in a browser.
3. Open `docs/public-evidence/index.html`.
4. Review `docs/demo/demo-task-suite.md`, `docs/demo/useful-scenarios.md`, `docs/demo/ablations.md`, `docs/demo/video-plan.md`, and `docs/demo/speech-to-task-dataset.md`.
5. Build the release pack, normalizer comparison, task-pack runner manifest, Speech-to-Task dataset with evaluation splits, and Speech-to-Task adaptation evaluation with the commands above.
6. Inspect the generated manifests and confirm they point back to committed sanitized trace sources or explicit fixture/configuration sources.

## Boundaries

The closeout MVP is a bounded spoken-command browser execution project. Model fine-tuning, expanded dataset collection, public hosting, verification-barrier bypassing, account workflows, deployment claims, ranking tables, leaderboard claims, state-of-the-art claims, broad public-web automation, and real-provider visual verification as a default requirement remain out of scope for this handoff. Fine-tuning belongs in a separate future project or later scoped change that consumes exported seed/evaluation data.
