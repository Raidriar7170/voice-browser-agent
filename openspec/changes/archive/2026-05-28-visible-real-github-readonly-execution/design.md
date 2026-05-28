## Context

`voice-browser-agent` now has a disabled-by-default `live_public_readonly` lane with task contracts, route metadata, completion verification, local/private trace policy, and console evidence cards. A real Python Docs smoke can complete with proof, but the GitHub-shaped command path still prefers a controlled local showcase. That keeps the public demo stable, but it does not satisfy the next reviewer-facing goal: typing "open GitHub and search agent projects" should visibly show a real GitHub public page result when the operator explicitly enables the public-readonly lane.

The existing boundary remains important. This repo is a bounded Voice-to-Browser Agent, not a general public-web autonomous agent or a GitHub account automation tool. GitHub is also less stable than documentation sites because unauthenticated public search can hit captcha, rate limits, changed result markup, or sign-in prompts. The design therefore treats those states as honest outcomes with visible local evidence, not errors to hide or bypass.

## Goals / Non-Goals

**Goals:**

- Add a first-class real GitHub public-readonly task set for public repository search and public repository page reading.
- Preserve deterministic routing: GitHub commands execute against `github.com` only when public-readonly is enabled and a matching GitHub task contract exists.
- Capture local/private visual artifacts for public-readonly runs so the Operator Console shows the real page result, step screenshots, or blocking page.
- Make completion proof stronger than "page opened" by verifying task-specific GitHub state such as query, result page, public repo marker, page title, README marker, or explicit block reason.
- Keep raw GitHub screenshots, URLs, page text, cookies, browser profiles, and local paths out of public exports until sanitizer approval.
- Document demo commands and a repeatable local smoke path that reviewers can run without confusing controlled showcase evidence with real GitHub evidence.

**Non-Goals:**

- No login, persistent user profile, browser cookie reuse, captcha solving, GitHub API token use, star/fork/watch, issue/PR/comment creation, file editing, uploads, downloads, or private repository access.
- No broad "browse GitHub until you find good projects" autonomy. The initial task is bounded search/read evidence, not ranking or research.
- No guarantee that GitHub will always return a clean search-result page. Captcha, login wall, rate limit, network failure, and markup drift are expected outcomes and must be surfaced.
- No public release of raw runtime screenshots or raw public page traces in this change.

## Decisions

1. **Represent GitHub as task contracts, not a special-case generic web agent.**

   GitHub support should extend the existing `PublicTaskContract` path. The initial contracts should include `github-repo-search` and `github-public-repo-read`. Search uses a URL template such as `https://github.com/search?q={search_query}&type=repositories`; repo read uses a template such as `https://github.com/{owner}/{repo}`. Allowed actions stay read-only: `navigate`, `search`, `open_result` when explicitly contracted, and `extract`. This keeps GitHub under the same allowlist, slot, timeout, and privacy machinery as Python Docs and MDN.

   Alternative considered: treat any GitHub command as a general public browser task. That would make the demo feel powerful, but it would immediately blur into account state, captcha behavior, and long-horizon browsing. The bounded contract path is less flashy and much easier to defend.

2. **Prefer real GitHub routing only when configuration makes it explicit.**

   Today GitHub-shaped commands map to `github-showcase`. After this change, route selection should first check whether public-readonly is enabled and a GitHub task contract matches. If yes, route to `public_readonly`; if not, preserve the current controlled showcase or preview fallback and clearly say why real GitHub did not run. This avoids surprising users who have not opted into real public execution.

   Alternative considered: replace the controlled showcase entirely. Keeping it is useful for stable offline demos and for cases where GitHub blocks unauthenticated access.

3. **Capture visual result artifacts as local/private runtime outputs.**

   The executor should capture screenshots after meaningful steps and at final/blocked state, store them under the runtime directory, and attach sanitized references to the trace. A small visual artifact model can record `artifact_id`, relative runtime ref, page title, sanitized origin, action type, completion state, privacy state, and sanitizer status. The API should expose artifacts only through path-guarded local endpoints tied to the execution id; public exports should include metadata summaries only unless the sanitizer explicitly approves.

   Alternative considered: embed screenshot bytes in trace JSON. That makes the API self-contained but increases leak risk and creates heavy trace payloads. Local artifact refs keep the operator UI visual without making public exports unsafe by default.

4. **Make the Operator Console visually primary for real public runs.**

   The current evidence cards remain useful, but real public runs need a visible result panel above or beside the cards. The panel should show the final screenshot, page title, target label, completion state, and a compact step strip. When the run stops on captcha/login/rate-limit, the panel should show the captured blocking state and the stop reason, not a green success card. The raw trace remains available below for audit.

   Alternative considered: rely on a headed Playwright window. A headed mode is useful as an optional local debugging switch, but the durable console experience should work from saved artifacts so it remains reviewable after the browser closes.

5. **Detect GitHub variance as first-class outcomes.**

   The public-readonly policy and completion verifier should map common GitHub variance into precise states: `public_task_captcha_or_verification`, `public_task_login_boundary`, `public_task_rate_limited`, `public_task_network_error`, `public_task_timeout`, `public_task_selector_changed`, and `public_readonly_step_budget_reached`. These states should preserve visible local evidence when safe and keep incomplete attempts out of successful evidence claims.

## Risks / Trade-offs

- **GitHub UI or bot protections may change** -> Keep the task set small, prefer URL-template navigation for search, verify using multiple resilient markers, and treat blocked pages as valid reliability evidence.
- **Screenshots can leak more than metadata** -> Store screenshots only under ignored runtime paths, expose them only to the local operator UI, and keep public export sanitizer strict by default.
- **Visual UI could imply public-safe publishing** -> Label visual artifacts `local_private` and show sanitizer status next to the preview.
- **GitHub command normalization may overmatch broad research requests** -> Preserve only bounded slots such as `search_query`, `owner`, `repo`, and `read_target`; reject or clarify "find the best", "keep searching", account actions, and mutation verbs.
- **Route ordering could regress controlled demos** -> Add tests for both enabled real GitHub routing and disabled/unmatched fallback to `github-showcase` or preview behavior.
- **Headed browser debug mode can confuse isolation** -> If added, it must still use a fresh ephemeral context and must not reuse the user's browser profile.

## Migration Plan

1. Add failing tests for GitHub normalization, routing, task contracts, completion verification, visual artifact metadata, sanitizer behavior, and console rendering.
2. Extend public-readonly models and fixtures with GitHub task contracts while keeping `VOICE_BROWSER_PUBLIC_READONLY_ENABLED=false` by default.
3. Implement GitHub route matching and bounded executor actions behind the existing public-readonly configuration gates.
4. Add local/private screenshot capture and path-guarded artifact serving for the Operator Console.
5. Update docs, demo fixtures, and evidence wording so controlled showcase and real GitHub public-readonly are visibly distinct.
6. Run a local smoke against unauthenticated GitHub when network access is available; record outcome as completed, blocked, failed, or stopped without committing raw runtime artifacts.

Rollback is straightforward: leave public-readonly disabled or remove the GitHub task contracts from the allowlist. Controlled GitHub showcase behavior remains available for demos that should not depend on github.com.

## Open Questions

- Which default demo query is most stable for the first GitHub smoke: `agent`, `browser-use-vision`, or a known public repository slug such as `Raidriar7170/gui-agent-benchmark`?
- Should `open_result` be included in the first implementation, or should the first pass only prove search-result visibility and defer clicking a result?
- Should the optional headed browser debug mode be exposed in the console, or only through an environment variable for local demos?
