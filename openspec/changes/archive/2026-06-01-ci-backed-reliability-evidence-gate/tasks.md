## 1. Test and Dependency Strategy

- [x] 1.1 Add tests that describe the CI reliability workflow shape, triggers, required OpenSpec validation step, dependency setup step, and deterministic test step.
- [x] 1.2 Add or update tests that prevent public handoff docs from implying CI ran local-only evidence generation, live public browsing, recorded-audio flows, provider inference, or model training.
- [x] 1.3 Decide and document the CI dependency strategy for `browser-use-vision`: public Git source, optional extra, narrow stub, or explicit CI-safe test subset.
- [x] 1.4 Add failure coverage for stale hard-coded pass counts or unsupported reliability claims in README/public evidence/interview surfaces.

## 2. Reliability Workflow

- [x] 2.1 Add a GitHub Actions reliability workflow separate from `front-door.yml`.
- [x] 2.2 Make the workflow run `OPENSPEC_TELEMETRY=0 openspec validate --all --strict` from the repository root.
- [x] 2.3 Make the workflow install the project through the selected CI-safe dependency strategy and run deterministic tests that do not require private runtime artifacts.
- [x] 2.4 Keep heavyweight browser, real voice, real provider, and live public-readonly checks local/private unless a deterministic CI-safe path is explicitly implemented.

## 3. Reliability Snapshot

- [x] 3.1 Add a local snapshot builder under `voice-browser-agent/scripts/` that reads committed sanitized evidence and optional local runtime manifests.
- [x] 3.2 Summarize demo trace coverage, visual verification outcomes, public-readonly task-pack outcomes, normalizer comparison metrics, Speech-to-Task adaptation evaluation metrics, validation command provenance, and privacy status.
- [x] 3.3 Add privacy-scan failures for raw audio paths, raw screenshots, browser profiles, cookies, credentials, raw prompts, raw provider responses, local file URIs, private URLs, remote host details, raw public page text, unsanitized runtime fields, and checkpoint-like paths.
- [x] 3.4 Ensure snapshot output is written under ignored `runtime/` paths and does not get committed as public raw evidence.

## 4. Documentation and Handoff

- [x] 4.1 Update README and public evidence docs to separate `front-door` CI, reliability CI, local validation commands, and generated local/private evidence.
- [x] 4.2 Update closeout checklist and interview handoff surfaces with the reliability workflow and snapshot command.
- [x] 4.3 Remove or qualify stale hard-coded pass counts unless they are tied to a specific closeout record or generated evidence source.
- [x] 4.4 Keep non-goal wording explicit: no fine-tuning, checkpoint release, ASR/TTS benchmark, production readiness, broad public-web autonomy, account automation, verification-barrier bypassing, public raw evidence release, leaderboard ranking, or SOTA claim.

## 5. Verification

- [x] 5.1 Run focused tests for workflow shape, dependency strategy, snapshot content, privacy failures, and handoff wording.
- [x] 5.2 Run `OPENSPEC_TELEMETRY=0 openspec validate --all --strict` from the repository root.
- [x] 5.3 Run the selected local project test command from `voice-browser-agent/`, including full `uv run pytest` if dependencies are available.
- [x] 5.4 Run `git diff --check` and fix whitespace issues.
- [x] 5.5 Inspect `git status --short --ignored` and report generated/ignored runtime outputs separately from source changes.
