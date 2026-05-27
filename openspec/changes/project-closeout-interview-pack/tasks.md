## 1. Closeout Contract Tests

- [x] 1.1 Add tests that require a closeout checklist with release-pack build, Speech-to-Task dataset build, OpenSpec validation, full pytest, diff whitespace, and git ignored-output review commands.
- [x] 1.2 Add tests that require the closeout checklist to distinguish committed sanitized trace sources from generated local runtime artifacts.
- [x] 1.3 Add tests that require the interview briefing HTML to include problem framing, bounded scope, architecture, execution flow, evidence modes, safety/privacy gates, adaptation dataset output, validation surface, limitations, and talk track sections.

## 2. Wording and Privacy Guards

- [x] 2.1 Extend documentation wording guards to include the closeout checklist and interview briefing.
- [x] 2.2 Add tests that final handoff docs reference README, demo task suite, ablations, video plan, release-pack workflow, dataset workflow, sanitized trace directories, and OpenSpec validation.
- [x] 2.3 Add privacy/positioning scans so final handoff docs avoid raw private artifact paths, credentials, private URLs, remote host details, benchmark/SOTA framing, production automation claims, unrestricted autonomy claims, ASR/TTS quality claims, and model-checkpoint claims.

## 3. Final Handoff Artifacts

- [x] 3.1 Create `docs/demo/closeout-checklist.md` as the final archive/commit/reviewer checklist.
- [x] 3.2 Create a browser-openable `docs/interview-project-overview.html` from existing repo evidence and generated-artifact paths.
- [x] 3.3 Update README and demo docs to point reviewers to the closeout checklist and interview briefing without bloating the main entry point.
- [x] 3.4 Include explicit limitations/non-goals for model fine-tuning, expanded dataset collection, public hosting, and broad public-web automation.

## 4. Verification

- [x] 4.1 Run targeted closeout/interview artifact tests.
- [x] 4.2 Run release-pack builder and Speech-to-Task dataset builder and inspect their generated manifest paths.
- [x] 4.3 Run `openspec validate project-closeout-interview-pack --strict`.
- [x] 4.4 Run `openspec validate --all --strict`.
- [x] 4.5 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 4.6 Run `git diff --check`.
- [x] 4.7 Check `git status --short --ignored` and confirm generated runtime artifacts remain ignored.
- [x] 4.8 Confirm `speech-to-task-adaptation-dataset` is archived before archiving this closeout change.
