## Why

The public-readonly useful task pack now defines stable read-only contracts, but reviewers still cannot reproduce a bounded live attempt across the pack from one local workflow. This change turns the pack from local/private metadata into an opt-in live run surface that records honest completion, partial, stopped, failed, and blocked outcomes without publishing raw public-web artifacts.

## What Changes

- Add an opt-in local task-pack runner for the existing public-readonly useful task pack.
- Run one or more explicit task contracts through the existing public-readonly route/executor boundary with the same allowlist, URL safety, read-only action, no-login, no-download, no-upload, private-network, and step/time-budget protections.
- Write a local/private run directory under `runtime/` with a machine-readable manifest, per-task outcome rows, selected contract metadata, completion proof summaries, stop/failure reasons, sanitizer state, and guarded visual artifact references when available.
- Support deterministic dry-run or fake-executor mode for tests and documentation without touching the network.
- Preserve honest live outcomes for public-site variance such as captcha, verification, rate-limit, unavailable pages, selector drift, network failure, or permission boundaries.
- Surface latest run availability and local/private status in readiness and the Operator Console without implying public-safe evidence.
- Include only sanitized run summaries or local/private exclusion reasons in release-pack output; raw public screenshots, page text, cookies, browser profiles, local file URIs, private URLs, and remote host details stay out of committed public evidence.

## Capabilities

### New Capabilities
- None. This change operationalizes the existing bounded public-readonly task-pack contract rather than introducing broad public-web automation.

### Modified Capabilities
- `public-readonly-web-execution`: define the live task-pack runner, run manifest, task selection, local/private run summary, deterministic test mode, and honest outcome classification for useful task attempts.
- `safe-browser-execution`: require every live task-pack attempt to preserve the existing public-readonly isolation, safety policy, completion verification, and guarded visual artifact boundaries.
- `operator-console`: display latest task-pack run state, row outcomes, completion proof summaries, sanitizer state, and local/private artifact labels.
- `demo-evidence-set`: include live task-pack run summaries as local/private evidence while excluding raw public runtime artifacts from public release output.

## Impact

- Affected backend code: public-readonly useful task-pack loading, runner script, route/executor invocation, run manifest writing, outcome summarization, readiness reporting, and release-pack generation.
- Affected UI/API: readiness payloads and Operator Console panels for latest public-readonly task-pack run state.
- Affected tests: deterministic runner tests, safety-policy regressions, manifest schema checks, release-pack exclusion checks, and UI/static rendering checks.
- Affected docs/artifacts: README runtime notes, demo evidence docs, closeout checklist, video plan, public evidence page, and generated local runtime manifests.
- Network behavior remains opt-in and local: no new default public-web execution, no account workflows, no mutation actions, no raw public artifact publication, and no production-use claim.
