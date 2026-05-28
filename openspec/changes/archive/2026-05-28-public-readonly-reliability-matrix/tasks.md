## 1. Reliability Matrix Contract Tests

- [x] 1.1 Add failing tests for loading a 5-8 task public-readonly reliability smoke set with task id, target label, target class, allowlist id, task kind, safe slots, URL/template, allowed read-only actions, completion criteria, limits, privacy policy, and expected matrix coverage.
- [x] 1.2 Add failing tests that smoke tasks without task-specific completion criteria are rejected for reliability-matrix use.
- [x] 1.3 Add failing tests for matrix rows representing `completed`, `partial`, `stopped`, `failed`, and `blocked` outcomes.
- [x] 1.4 Add failing tests that a page-open-only public task cannot be marked completed without observed task-specific proof.

## 2. Normalization and Routing

- [x] 2.1 Extend public-readonly slot normalization tests for expanded documentation, reference, and public repository search/read commands.
- [x] 2.2 Add tests that broad browsing, open-ended comparison, account-oriented, mutation-oriented, arbitrary URL, unsafe protocol, private-network, and credential-bearing commands become clarification, rejection, confirmation, or blocked states.
- [x] 2.3 Extend route-selection tests so expanded reliability tasks route only when public-readonly is enabled and a matching task contract exists.
- [x] 2.4 Extend route decisions with matrix eligibility, target class, completion criteria id, evidence privacy state, sanitizer status, and stable rejected-route reasons.

## 3. Executor, Verifier, and Policy Outcomes

- [x] 3.1 Extend public task contract parsing and runtime config support for the reliability matrix fields while preserving disabled-by-default public-readonly behavior.
- [x] 3.2 Extend or add matrix-generation models that record task id, target class, observed proof, unmet criteria, outcome, stop/failure reason, privacy state, sanitizer status, and regression coverage.
- [x] 3.3 Extend completion verification so every reliability task requires configured proof and returns completed, partial, stopped, failed, or blocked outcome explicitly.
- [x] 3.4 Enforce safety policy outcomes for login, captcha/verification, rate-limit, account actions, mutation, upload/download, private data, off-allowlist navigation, private-network targets, and manual override attempts.
- [x] 3.5 Preserve guarded local/private visual artifact references for matrix inspection without embedding raw screenshots or raw page text in public export payloads.

## 4. Operator Console and API

- [x] 4.1 Extend execution API responses with reliability matrix fields, including outcome classification, observed proof, unmet criteria, visible result state, and export state.
- [x] 4.2 Update the Operator Console result panel to show task id, task kind, target class, completion criteria summary, route reason, execution limits, outcome, stop/failure reason, privacy state, and sanitizer status before raw trace JSON.
- [x] 4.3 Ensure the console styles completed, partial, stopped, failed, and blocked public-readonly outcomes distinctly and never styles opened-but-incomplete tasks as successful.
- [x] 4.4 Run desktop and mobile UI checks for reliability matrix states, long reason text, local/private visual artifact labels, and sanitizer-pending or sanitizer-failed export states.

## 5. Evidence, Release Pack, and Documentation

- [x] 5.1 Update public-readonly smoke fixtures or docs to define 5-8 bounded reliability tasks and keep the stable controlled showcase separate from real public-readonly tasks.
- [x] 5.2 Extend the release-pack or evidence builder to emit a reviewer-readable reliability matrix summary while excluding raw public runtime traces, screenshots, page text, cookies, credentials, browser profiles, local paths, private data, and remote host details.
- [x] 5.3 Add completeness and privacy gates for missing outcome classes, ambiguous rows, malformed matrix rows, and unsafe exported content.
- [x] 5.4 Update README, useful scenarios, demo task suite, public evidence page, video plan, closeout checklist, interview material, and `CONTEXT.md` with reliability matrix scope, commands, limitations, and private-by-default boundaries.
- [x] 5.5 Add wording guards so the matrix is not described as production automation, unrestricted public-web autonomy, captcha bypass, account automation, public benchmark, SOTA, model-quality, or public raw-dataset evidence.

## 6. Verification

- [x] 6.1 Run targeted tests for normalization slots, routing, public task contracts, completion verifier, policy outcomes, matrix generation, sanitizer/export behavior, API responses, and console rendering.
- [x] 6.2 Run `openspec validate public-readonly-reliability-matrix --strict`.
- [x] 6.3 Run `openspec validate --all --strict`.
- [x] 6.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 6.5 Run `git diff --check`.
- [x] 6.6 Run `git status --short --ignored` and confirm raw public runtime traces, screenshots, uploads, browser profiles, caches, and generated release packs remain ignored or unstaged.
