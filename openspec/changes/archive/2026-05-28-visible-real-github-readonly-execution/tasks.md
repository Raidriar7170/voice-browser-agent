## 1. Contract, Normalization, and Routing Tests

- [x] 1.1 Add failing tests for GitHub public task contract parsing, including `github-repo-search`, `github-public-repo-read`, URL templates, allowed read-only actions, required slots, completion criteria, limits, and local/private visual artifact policy.
- [x] 1.2 Add failing tests that GitHub public-readonly remains disabled by default and falls back to controlled showcase, preview, clarification, or blocked behavior without claiming real `github.com` execution.
- [x] 1.3 Add failing normalizer tests for GitHub repository search commands that preserve target site hint, search query, repository intent, read-only constraints, stop conditions, and safety flags.
- [x] 1.4 Add failing normalizer tests for GitHub public repository read commands that preserve owner/repo or repo slug slots, read target, read-only constraints, stop conditions, and safety flags.
- [x] 1.5 Add failing normalizer/validator tests for unsupported GitHub commands, including login, star, fork, issue, pull request, comment, edit, upload, download, private repository access, and broad ranking/research requests.
- [x] 1.6 Add failing route-selection tests that prefer real GitHub public-readonly when enabled with a matching task contract and preserve the current controlled showcase fallback when disabled or unmatched.
- [x] 1.7 Add failing route-bypass tests for manual `live_public_readonly` overrides, mixed unsafe URLs, private-network URLs, credential-bearing URLs, and non-allowlisted origins.

## 2. Completion and Site-Variance Tests

- [x] 2.1 Add failing completion verifier tests for successful GitHub repository search proof, including searched query, search URL or page state, repository result marker, page title, and completed state.
- [x] 2.2 Add failing completion verifier tests for successful GitHub public repository read proof, including owner/repo slug, public repo page title, README or description marker, and completed state.
- [x] 2.3 Add failing tests that opening GitHub without search or repository proof is partial, stopped, or failed rather than succeeded.
- [x] 2.4 Add failing tests for GitHub captcha, abuse detection, verification, login boundary, private repository, permission, rate-limit, timeout, network error, selector drift, and step-budget outcomes.
- [x] 2.5 Add failing tests that GitHub site-variance outcomes preserve collected evidence and precise stop/failure reasons without bypassing safety policy.

## 3. Visual Artifact and Privacy Tests

- [x] 3.1 Add failing model/schema tests for public-readonly visual artifact metadata, including artifact id, local runtime ref, action label, page title, sanitized origin, completion state, privacy state, sanitizer status, and execution id binding.
- [x] 3.2 Add failing executor tests that step and final screenshots are captured for GitHub public-readonly runs when visual result capture is enabled.
- [x] 3.3 Add failing executor tests that blocked GitHub states capture local/private visual evidence when safe.
- [x] 3.4 Add failing API tests for path-guarded local visual artifact retrieval that prevents path traversal and access to artifacts outside the execution runtime.
- [x] 3.5 Add failing sanitizer/export tests that raw GitHub screenshots, raw page text, cookies, credentials, browser profile paths, private URLs, local file URIs, and remote host details are excluded from public exports.
- [x] 3.6 Add failing tests for optional headed public browser mode preserving fresh ephemeral context, no persistent profile, and no reused cookies.

## 4. GitHub Public-Readonly Implementation

- [x] 4.1 Extend public-readonly contract models/config parsing to support GitHub task examples without enabling them by default.
- [x] 4.2 Extend normalizer behavior to extract bounded GitHub search queries, public repo slugs, and read targets without hardcoding unrelated queries.
- [x] 4.3 Extend validation and safety gates for GitHub account actions, mutation verbs, broad research requests, and private repository access.
- [x] 4.4 Update route selection so configured GitHub public-readonly task contracts take precedence over controlled showcase only when enabled and matched.
- [x] 4.5 Preserve controlled GitHub showcase behavior when public-readonly is disabled, missing allowlist, missing task contract, or blocked by safety policy.
- [x] 4.6 Implement GitHub repository search execution with URL-template navigation or read-only search-field fallback under the public-readonly policy.
- [x] 4.7 Implement GitHub public repository read execution for explicit owner/repo or repo slug tasks under the public-readonly policy.
- [x] 4.8 Extend public task completion verification for GitHub search and repo-read proof fields and unmet-criteria reporting.
- [x] 4.9 Map GitHub captcha, verification, login, private repo, rate-limit, timeout, network error, selector drift, and budget states to precise public task outcome reasons.

## 5. Visual Result Implementation

- [x] 5.1 Add local/private visual artifact metadata to execution runtime and trace responses without embedding raw screenshot bytes.
- [x] 5.2 Capture step and final screenshots for public-readonly tasks into ignored runtime paths with execution-scoped filenames.
- [x] 5.3 Add a path-guarded local artifact endpoint for the Operator Console to display visual artifacts tied to the current execution id.
- [x] 5.4 Ensure trace writing and sanitized responses omit raw screenshot bytes, browser profile data, cookies, credentials, local absolute paths, raw public page text, and private URLs.
- [x] 5.5 Add optional configuration for headed public browser debug mode while preserving isolated browser contexts and read-only policy checks.

## 6. Operator Console Implementation

- [x] 6.1 Update the execution API response shape consumed by the console to include visual artifact summaries, final visual result ref, and step timeline refs for public-readonly runs.
- [x] 6.2 Add a visible result panel to the Operator Console that shows final screenshot preview, page title, target label, sanitized origin, completion state, privacy state, and sanitizer status.
- [x] 6.3 Add compact step screenshot timeline rendering for public-readonly navigation, search, read, and stop states.
- [x] 6.4 Ensure GitHub captcha, verification, login, rate-limit, and missing-proof states are styled as blocked, stopped, failed, or incomplete rather than completed.
- [x] 6.5 Ensure the console falls back to proof metadata with a clear "no visual result captured" message when visual artifacts are unavailable.
- [x] 6.6 Run desktop and mobile visual checks for completed, blocked, stopped, failed, local/private, and no-visual-artifact states.

## 7. Docs, Fixtures, and Evidence

- [x] 7.1 Add GitHub public-readonly smoke fixture entries for repository search and public repository read with task id, kind, slots, completion criteria, limits, safety boundaries, visual artifact policy, and local/private status.
- [x] 7.2 Update README with copy-paste local commands for enabling the GitHub public-readonly allowlist/task contract and running a visible GitHub smoke through the console or API.
- [x] 7.3 Update demo task suite, useful scenarios, video plan, closeout checklist, public evidence page, and interview overview to distinguish controlled GitHub showcase from real GitHub public-readonly evidence.
- [x] 7.4 Update release-pack behavior or docs so local/private GitHub screenshots and raw runtime traces remain excluded unless sanitizer approval is explicit.
- [x] 7.5 Update `CONTEXT.md` coverage matrix with GitHub public-readonly task contracts, visible result artifacts, console visual result panel, and privacy boundaries.

## 8. Validation and Smoke

- [x] 8.1 Run targeted tests for GitHub normalization, route selection, task contracts, completion verifier, executor policy, visual artifacts, sanitizer/export behavior, API responses, and console rendering.
- [x] 8.2 Run a local real GitHub public-readonly smoke with public-readonly enabled and record whether it completed, blocked, stopped, failed, or hit site variance without committing raw runtime artifacts.
- [x] 8.3 Run `openspec validate visible-real-github-readonly-execution --strict`.
- [x] 8.4 Run `openspec validate --all --strict`.
- [x] 8.5 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 8.6 Run `git diff --check`.
- [x] 8.7 Run `git status --short --ignored` and confirm raw GitHub screenshots, runtime traces, browser profiles, uploads, caches, and generated release packs remain ignored or unstaged.
