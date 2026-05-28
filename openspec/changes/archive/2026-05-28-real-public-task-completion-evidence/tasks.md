## 1. Public Task Contract Tests

- [x] 1.1 Add failing tests for public task contract parsing, including task id, task kind, allowlist id, target URL/template, allowed actions, slots, completion criteria, limits, and privacy policy.
- [x] 1.2 Add failing tests that an allowlisted origin without a matching task contract cannot launch live public task execution.
- [x] 1.3 Add failing tests for public task slot normalization, including target site hints, search query, read target, extraction target, read-only constraints, stop conditions, and safety flags.
- [x] 1.4 Add failing tests for route decisions that preserve public task id, task kind, requested slots, completion criteria identifier, sanitized origin, allowlist id, execution limits, and private evidence state.

## 2. Completion Verifier Contract Tests

- [x] 2.1 Add failing tests for a documentation search completion verifier that requires task-specific proof such as searched query, result heading, final title, URL path, or visible result marker.
- [x] 2.2 Add failing tests that opening a public page without satisfying the requested search/read/extraction criteria is partial, stopped, or failed instead of succeeded.
- [x] 2.3 Add failing tests for public site variance outcomes, including timeout, missing selector, redirect off allowlist, captcha/login boundary, network error, and step-budget exhaustion.
- [x] 2.4 Add failing tests that public task outcomes are classified as completed, partial, stopped, failed, or blocked with precise stop/failure reasons.

## 3. Models, Config, and Routing

- [x] 3.1 Add public task contract models and runtime/config parsing while keeping public-readonly disabled by default.
- [x] 3.2 Extend public-readonly target matching so route selection uses configured task contracts instead of domain-only matching.
- [x] 3.3 Extend normalizer and validator behavior to preserve public task slots and clarify or reject broad, mutation-oriented, or unsupported public commands.
- [x] 3.4 Extend route decision and trace/runtime metadata with public task id, task kind, requested slots, completion criteria summary, completion state, observed proof summary, and unmet criteria.

## 4. Public-Readonly Executor and Verifier

- [x] 4.1 Implement a deterministic public task completion verifier separate from URL/action policy checks.
- [x] 4.2 Extend the Playwright public-readonly executor to perform bounded task actions for the first stable smoke tasks, such as documentation search, direct reference read, safe result navigation, read-only expansion, and visible extraction.
- [x] 4.3 Enforce task-contract allowed action classes before every public action and preserve existing URL, private-network, login, mutation, upload/download, and sensitive-state stops.
- [x] 4.4 Ensure executor results fail or stop with missing-completion, site-variance, policy-stop, or budget reasons when completion proof is absent.

## 5. Evidence Privacy and Export

- [x] 5.1 Extend trace writing and sanitization for public task completion state, requested slots, observed proof summaries, unmet criteria, and local/private evidence status.
- [x] 5.2 Update release-pack behavior so local/private public task traces are excluded or represented only by sanitizer-approved summaries.
- [x] 5.3 Add sanitizer tests that raw public URLs, page text, screenshots, cookies, credentials, profile paths, local file URIs, private data, and remote host details are excluded from public artifacts.
- [x] 5.4 Generate or document private runtime smoke traces for the first public task set without committing raw public runtime traces.

## 6. Operator Console and API

- [x] 6.1 Update execution API responses so public task plan, completion state, observed proof summary, unmet criteria, and privacy state are available to the console.
- [x] 6.2 Update Operator Console route/evidence panels to show public task id, task kind, target label, completion criteria, completion state, stop/failure reason, and sanitizer/export status.
- [x] 6.3 Ensure the console does not visually present opened-but-incomplete public tasks as successful.
- [x] 6.4 Run desktop and mobile visual checks for public task route/result states, including completed, partial, stopped, failed, blocked, and local/private export states.

## 7. Documentation and Smoke Set

- [x] 7.1 Define 2-3 initial public task smoke fixtures, favoring stable reference/documentation targets such as Python docs, MDN, or Wikipedia.
- [x] 7.2 Update README, demo docs, public evidence page, video plan, closeout/interview material, and `CONTEXT.md` coverage matrix with real public task completion boundaries.
- [x] 7.3 Document why OpenAI docs and GitHub public search may remain optional or later targets if UI drift, login, captcha, or anti-bot boundaries make them less stable.
- [x] 7.4 Add wording/privacy guards so docs avoid production automation, unrestricted autonomy, account automation, captcha bypass, public benchmark, SOTA, and model-quality claims.

## 8. Verification

- [x] 8.1 Run targeted tests for normalizer slots, public task routing, completion verifier, public-readonly executor, sanitizer/export behavior, API responses, console rendering, and release-pack classification.
- [x] 8.2 Run `openspec validate real-public-task-completion-evidence --strict`.
- [x] 8.3 Run `openspec validate --all --strict`.
- [x] 8.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 8.5 Run `git diff --check`.
- [x] 8.6 Run `git status --short --ignored` and confirm raw public runtime traces, screenshots, uploads, browser profiles, caches, and generated release packs remain ignored or unstaged.
