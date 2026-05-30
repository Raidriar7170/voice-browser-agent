## 1. Documentation Guardrails

- [x] 1.1 Add or update documentation tests that reject archived change-specific validation commands in final closeout surfaces after archive.
- [x] 1.2 Add or update documentation tests requiring final handoff surfaces to mention Speech-to-Task dataset evaluation splits, held-out adaptation evaluation, adaptation eval manifest paths, and optional release-pack inclusion.
- [x] 1.3 Add or update wording/privacy guards for final surfaces covering fine-tuning, checkpoint, benchmark, production, ASR/TTS, broad-autonomy, raw provider data, local file URI, and remote host overclaims.

## 2. Final Handoff Surfaces

- [x] 2.1 Refresh `CONTEXT.md` coverage matrix so the latest archived capabilities are represented: visual verification, LLM structured-output normalization, public-readonly task-pack runner, normalizer comparison, Speech-to-Task seed-set splits, and adaptation evaluation.
- [x] 2.2 Update `docs/demo/closeout-checklist.md` with current final commands: main-spec OpenSpec validation, full tests, whitespace checks, ignored-output review, public-readonly task-pack deterministic run, normalizer comparison, Speech-to-Task dataset with `--evaluation-splits`, adaptation evaluation, and release-pack inclusion of optional adaptation eval summary.
- [x] 2.3 Update `docs/public-evidence/index.html` so local review commands and evidence descriptions include adaptation evaluation without implying fine-tuning or model-quality claims.
- [x] 2.4 Update `docs/interview-project-overview.html` so the interview story covers adaptation evaluation output, current validation commands, evidence sources, and the decision to keep fine-tuning outside this project.
- [x] 2.5 Update README or demo docs only where needed to keep final reviewer paths consistent with the closeout checklist and public evidence page.

## 3. Local Evidence Chain

- [x] 3.1 Run or inspect the deterministic local evidence generation chain: public-readonly task-pack runner, normalizer comparison, Speech-to-Task dataset with evaluation splits, and Speech-to-Task adaptation evaluation.
- [x] 3.2 Build the demo evidence release pack with normalizer comparison and adaptation evaluation manifests when those local artifacts exist.
- [x] 3.3 Confirm generated runtime outputs remain local/ignored and no raw screenshots, provider payloads, checkpoints, local paths, remote host details, or raw public runtime artifacts are committed.

## 4. Verification

- [x] 4.1 Run `OPENSPEC_TELEMETRY=0 openspec validate --all --strict` from the repository root.
- [x] 4.2 Run focused documentation/release-pack tests affected by this change.
- [x] 4.3 Run the full project test suite with `uv run pytest` from `voice-browser-agent/`.
- [x] 4.4 Run `git diff --check` and fix any whitespace issues.
- [x] 4.5 Run `git status --short --ignored` and report ignored/generated outputs separately from committed source changes.
