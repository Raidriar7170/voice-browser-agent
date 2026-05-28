## Context

`voice-browser-agent` already has a disabled-by-default `live_public_readonly` lane with allowlisted targets, isolated Playwright contexts, read-only policy checks, private trace boundaries, and UI/readiness reporting. A quick real public smoke showed that this path can open `docs.python.org` and record page-title evidence, but it did not complete the requested "search pathlib" task. The next stage should therefore make real public tasks completion-aware rather than merely navigation-aware.

The design keeps the bounded Voice-to-Browser Agent promise. Public execution remains local, opt-in, allowlisted, read-only, and private by default. The project should not become a generic web automation platform or a logged-in browser assistant.

## Goals / Non-Goals

**Goals:**

- Define a small public task contract for allowlisted public pages.
- Route public commands to task contracts, not arbitrary transcript-emitted URLs.
- Execute a small set of real public read-only tasks with bounded Playwright actions.
- Verify task completion using deterministic criteria before marking success.
- Preserve failed, partial, stopped, and blocked runs as evidence instead of overclaiming.
- Keep raw public traces local/private unless an explicit sanitizer approves export.
- Make route, task plan, completion criteria, observed proof, and privacy state visible in the Operator Console.

**Non-Goals:**

- No unrestricted public-web autonomy or long-horizon browsing.
- No login, account state, persistent browser profile, cookies, purchases, posting, deletion, upload, download, private-data entry, or captcha bypass.
- No production-grade public-site compatibility layer.
- No public claim that local/private public-readonly traces are publishable without sanitizer approval.
- No remote browser execution; remote services remain optional ASR or visual inference backends only.

## Decisions

1. **Introduce public task contracts on top of allowlist entries**

   Each first-stage public task should have an id, target label, allowlist id, task kind, target URL or URL template, allowed action classes, slot names, completion criteria, limits, and privacy policy. This keeps the route and executor grounded in explicit policy while still letting commands supply safe slots such as a search query.

   Alternative considered: keep using domain-level allowlists only. Rejected because domain-level allowlists prove safe navigation but not task completion.

2. **Add a completion verifier separate from the action policy**

   The action policy answers "may the agent do this next action?" The completion verifier answers "did the requested task actually complete?" Keeping them separate avoids declaring success after a safe but irrelevant action such as opening the page title.

   Alternative considered: infer success from final status and action count. Rejected because the current shallow public smoke can succeed while skipping the requested search or extraction.

3. **Start with stable read-only task kinds**

   The initial task kinds should be documentation search, direct reference read, visible heading or summary extraction, and read-only expand/filter when stable. Candidate first targets should prefer Python docs, MDN, Wikipedia, or another stable documentation/reference site. OpenAI docs and GitHub public search can remain optional or later targets because they are more likely to change UI or reach login/anti-bot boundaries.

   Alternative considered: use flashy sites first. Rejected because the next credibility gain is completed evidence, not breadth.

4. **Treat site variance as evidence, not a failure to hide**

   If a public page changes, lacks a search field, redirects off-policy, hits a login/captcha boundary, or times out, the run should stop or fail with a precise reason and preserve partial evidence. This is more honest than hardening toward site-specific brittle success.

   Alternative considered: add bypasses and many selectors until the task passes. Rejected because bypass logic would weaken the safety and portfolio story.

5. **Keep public task traces local/private by default**

   Real public pages can contain third-party text, URLs, screenshots, and changing content. Runtime traces should remain ignored/local unless a public-readonly sanitizer approves a minimized export or summary.

   Alternative considered: commit full public traces after generic sanitization. Rejected because third-party page content needs stricter review than controlled local demo pages.

## Risks / Trade-offs

- Public pages drift -> use only 2-3 stable smoke tasks, classify variance explicitly, and keep smoke evidence private unless sanitized.
- Completion criteria may be too strict -> begin with deterministic criteria such as result heading, final title, URL path, or visible text marker; expand only with tests.
- Completion criteria may be too loose -> require at least one task-specific observed proof, not just page title or action count.
- Search fields differ across sites -> use per-task selector hints and task-specific failure reasons rather than broad browser autonomy.
- Sanitized public evidence may feel less visual -> provide public-safe summaries first, and only add screenshots or page excerpts when sanitizer rules approve them.
- Scope could drift into public automation -> keep one-command execution, allowlists, short budgets, read-only actions, and no account state.

## Migration Plan

1. Add task-contract models, fixture entries, and parsing from runtime/configured public-readonly targets.
2. Add normalizer/route tests for public task slots and route decisions.
3. Add completion verifier tests before expanding the public executor.
4. Implement read-only task execution for the smallest stable smoke set.
5. Update trace/sanitizer/UI/evidence docs to show completion state and private-by-default status.
6. Run targeted public task tests, OpenSpec validation, full pytest, diff whitespace checks, and ignored-runtime review.

Rollback is simple: keep `live_public_readonly` disabled by default or route public commands back to controlled-showcase/demo-preview while preserving the task-contract code behind configuration.

## Open Questions

- Which exact first targets should be committed as the required smoke set: Python docs, MDN, Wikipedia, or a different stable public reference site?
- Should the first public summaries include only metadata and task-completion proof, or a small sanitized excerpt when sanitizer rules pass?
- Should public task definitions live in environment configuration, a checked-in fixture file, or both?
