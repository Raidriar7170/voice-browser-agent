## Why

The current GitHub-shaped command path is useful for controlled demos, but it does not prove that `github.com` was operated: it routes to a local showcase page and the Operator Console mainly shows trace cards. The next stage should make one or two bounded real GitHub public-readonly tasks visibly inspectable, so a reviewer can see the real webpage result while the system still reports honest blocks for login, captcha, rate-limit, or site-variance cases.

## What Changes

- Add explicit GitHub public-readonly task contracts for stable read-only flows such as repository search and public repository page reading.
- Route supported GitHub commands to `live_public_readonly` only when public-readonly is enabled, `github.com` is allowlisted, and a GitHub task contract matches the normalized slots.
- Extend public task completion verification for GitHub-specific proof, including searched query, search result page, repository result metadata, public repo title/owner/name, README or description marker, and block reasons.
- Add local/private visual result artifacts for live public tasks, including final screenshot preview, step screenshot timeline, page title, sanitized origin, and blocked-page screenshot when safe.
- Update the Operator Console so the user can see the real public page result or blocking state directly, instead of relying only on `Execution Evidence` cards and raw trace JSON.
- Keep GitHub execution disabled by default, isolated from user sessions, and strictly read-only: no login, captcha bypass, star, fork, issue, pull request, comment, file edit, download, upload, or account automation.
- Update demo fixtures, docs, and evidence wording to distinguish controlled GitHub showcase, real GitHub public-readonly smoke, and local/private visual artifacts.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `public-readonly-web-execution`: Add GitHub-specific public task contracts, visual result artifacts, and honest handling for captcha/login/rate-limit/site-variance states.
- `operator-task-routing`: Route supported GitHub commands to real public-readonly only when a task contract matches; otherwise keep controlled showcase, preview, clarification, or blocked behavior.
- `spoken-command-normalization`: Preserve GitHub search/read slots without broadening into account automation or unrestricted public browsing.
- `safe-browser-execution`: Capture local/private screenshots and page-state evidence for public-readonly runs while preserving isolation and read-only policy stops.
- `operator-console`: Display real public webpage visual result previews, step screenshots, and block states in the console.
- `demo-evidence-set`: Document and fixture the real GitHub public-readonly smoke path separately from controlled showcase and public release artifacts.

## Impact

- Affected backend code: public-readonly task contract parsing/matching, GitHub route selection, Playwright public-readonly executor, completion verifier, trace model/runtime metadata, trace writer/sanitizer, and readiness/preflight reporting.
- Affected UI/API: `/api/executions`, trace/export payloads, Operator Console result panels, visual preview rendering, and local/private artifact messaging.
- Affected tests: normalizer slot tests, route-selection tests, public-readonly executor tests, completion verifier tests, sanitizer/privacy tests, API/UI rendering tests, and release-pack classification tests.
- Affected docs/evidence: README, demo task suite, useful scenarios, video plan, closeout checklist, public evidence page, `CONTEXT.md` coverage matrix, and public-readonly smoke fixture manifest.
