## Why

The current public-readonly lane can execute a few bounded public tasks, but its evidence is still task-by-task rather than a repeatable reliability story. This change upgrades it into a small public-readonly reliability matrix that proves completed, partial, stopped, failed, and blocked outcomes under explicit safety boundaries.

## What Changes

- Expand the allowlisted public-readonly smoke set to 5-8 stable read-only task contracts, favoring documentation, reference, and public repository search/read tasks.
- Require every public task contract to define task kind, safe input slots, allowed read-only actions, completion criteria, execution limits, privacy policy, and expected outcome classification.
- Add a public-readonly reliability matrix that records task id, target class, expected proof, observed proof, outcome state, failure or stop reason, privacy/export status, and regression coverage.
- Extend completion verification so each task is judged against task-specific criteria and never succeeds merely because a page opened or actions occurred.
- Preserve strict safety boundaries: no arbitrary URLs, no login/session reuse, no account actions, no mutation, no upload/download, no captcha bypass, no private-network targets, and no long-horizon browsing.
- Update the Operator Console to surface reliability-matrix evidence, including task class, completion proof, outcome classification, policy reason, visible result availability, and sanitizer/export state.
- Update evidence docs and release-pack summaries so sanitizer-approved public-readonly summaries can be reviewed without publishing raw public traces, screenshots, page text, cookies, browser profiles, credentials, local paths, or private data.
- Add regression coverage for broad browsing, login, mutation, download/upload, captcha or verification boundaries, private URL injection, missing task contracts, manual override attempts, and opened-but-incomplete public tasks.

## Capabilities

### New Capabilities

- None. This change strengthens the existing bounded public-readonly execution and evidence contracts rather than introducing broad public-web automation.

### Modified Capabilities

- `public-readonly-web-execution`: require a 5-8 task public-readonly smoke set, reliability-matrix outcome classification, completion proof, and safety-boundary regressions.
- `operator-task-routing`: route expanded public commands only when a matching task contract exists, and preserve auditable route reasons for matrix outcomes.
- `safe-browser-execution`: enforce read-only policy, task budget, missing-completion, captcha/login/mutation, private-network, and manual-override stops as explicit reliability outcomes.
- `operator-console`: display reliability-matrix status, task proof, outcome reason, visible result state, and sanitizer/export status without misleading success styling.
- `demo-evidence-set`: publish a reviewer-readable reliability matrix and release-pack summaries while keeping raw public-readonly artifacts local/private by default.
- `spoken-command-normalization`: preserve safe public task slots for the expanded task set and clarify or reject unsupported broad, account-oriented, or mutation-oriented commands.

## Impact

- Affected backend code: public task contract parsing, route selection, public-readonly executor, completion verifier, policy checks, trace models, sanitizer/export logic, and smoke/matrix generation scripts.
- Affected UI/API: execution responses, Operator Console route/result panels, reliability matrix rendering, visible result messaging, and export state.
- Affected tests: public task contracts, route selection, slot preservation, executor outcomes, completion verifier, safety regressions, sanitizer/privacy gates, API responses, and console rendering.
- Affected docs/evidence: README, public-readonly smoke fixtures, useful scenarios, demo task suite, public evidence page, closeout checklist, interview material, and release-pack summaries.
- External behavior remains bounded and opt-in: public-readonly tasks require explicit enablement, allowlisted task contracts, isolated local browser contexts, short budgets, and private-by-default evidence.
