## Why

The project now has a broad evidence surface across controlled execution, public-readonly summaries, visual verification, normalizer comparison, and Speech-to-Task adaptation evaluation, but the final reviewer handoff materials have drifted behind the latest archived specs. This change closes the project as a coherent bounded Voice-to-Browser Agent deliverable by making the final audit path current, reproducible, and explicit about what is complete versus intentionally out of scope.

## What Changes

- Refresh the final completion narrative across `CONTEXT.md`, closeout checklist, public evidence page, interview overview, and README-adjacent handoff surfaces.
- Replace archived change-specific validation commands with current main-spec and repo validation commands that actually run after archive.
- Add the Speech-to-Task adaptation evaluation harness to final review paths, including `--evaluation-splits`, held-out evaluation, optional release-pack inclusion, and non-training/non-checkpoint framing.
- Add or update tests that guard final handoff docs against stale commands, unsupported fine-tuning claims, missing adaptation-evaluation references, and private artifact leakage.
- Regenerate or verify local runtime review artifacts only as ignored local outputs; do not commit raw runtime artifacts, screenshots, checkpoints, provider payloads, or local/private paths.
- Keep model fine-tuning out of this project completion audit; future fine-tuning belongs in a separate project or later OpenSpec change.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `demo-evidence-set`: Final reviewer handoff requirements must reference current validation commands, final completion audit surfaces, generated local artifact boundaries, and the latest adaptation evaluation path.
- `speech-to-task-adaptation-evaluation`: Final handoff documentation must surface the local adaptation evaluation harness as adaptation-readiness evidence while explicitly avoiding fine-tuning, checkpoint, ASR/TTS evaluation, production, and benchmark claims.

## Impact

- Documentation: `CONTEXT.md`, `voice-browser-agent/docs/demo/closeout-checklist.md`, `voice-browser-agent/docs/public-evidence/index.html`, `voice-browser-agent/docs/interview-project-overview.html`, and possibly `voice-browser-agent/README.md` or demo docs where final paths are summarized.
- Tests: documentation and release-pack guard tests under `voice-browser-agent/tests/`.
- OpenSpec: delta specs under `openspec/changes/final-project-completion-audit/specs/`.
- Runtime: local generated artifacts may be rebuilt under ignored `voice-browser-agent/runtime/` for verification, but no runtime outputs or checkpoints are committed.
