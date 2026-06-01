## Why

The project has strong local evidence for controlled execution, public-readonly task
contracts, visual verification, normalizer comparison, and Speech-to-Task adaptation
readiness, but the GitHub-facing validation still only runs a lightweight front-door
check. This change makes the evidence chain continuously reproducible and reviewer
trustworthy without widening the agent's autonomy, training, or deployment claims.

## What Changes

- Add a CI-backed reliability gate that runs OpenSpec validation and a CI-safe
  project test strategy on GitHub Actions.
- Add a generated reliability snapshot that summarizes existing evidence sources:
  demo trace coverage, visual verification outcomes, public-readonly task-pack
  outcomes, normalizer comparison metrics, Speech-to-Task adaptation evaluation
  metrics, and privacy/sanitizer status.
- Split final handoff wording into local validation, CI validation, and generated
  local/private runtime artifacts so public docs do not overstate what CI has
  reproduced.
- Keep heavy or local-only execution private by default: raw recordings,
  screenshots, public-readonly runtime traces, provider payloads, local paths,
  browser profiles, and checkpoint-like outputs remain ignored and unstaged.
- Preserve the existing bounded MVP claim: no model fine-tuning, checkpoint
  release, ASR/TTS benchmark, production deployment, broad public-web autonomy,
  account automation, or public leaderboard claim is introduced.

## Capabilities

### New Capabilities

- `ci-backed-reliability-evidence-gate`: Defines the CI workflow contract,
  dependency strategy, reliability snapshot manifest, privacy gates, and status
  reporting that make the existing evidence chain reproducible on GitHub and
  locally reviewable.

### Modified Capabilities

- `demo-evidence-set`: Final handoff and release-pack documentation must
  distinguish CI-verified checks from local-only generated evidence, and must
  reference the new reliability snapshot without treating private runtime outputs
  as committed public evidence.

## Impact

- GitHub Actions: add or extend workflows under `.github/workflows/` beyond the
  current lightweight `front-door` job.
- Packaging/dependencies: define a CI-safe install path for `voice-browser-agent`,
  including how `browser-use-vision` is resolved when the local editable sibling
  path is unavailable.
- Scripts: likely add a reliability snapshot builder under
  `voice-browser-agent/scripts/` that consumes existing committed sanitized
  artifacts and optional local manifests.
- Tests: add focused tests for workflow shape, reliability snapshot content,
  privacy scanning, and documentation wording; keep full runtime/browser/provider
  checks out of CI unless they are explicitly made deterministic and safe.
- Documentation: update README, public evidence, closeout checklist, and related
  handoff surfaces to show CI status and local/private evidence boundaries.
- Runtime artifacts: generated outputs remain under ignored
  `voice-browser-agent/runtime/` and are not committed.
