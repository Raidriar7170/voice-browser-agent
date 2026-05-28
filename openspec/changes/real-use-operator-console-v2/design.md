## Context

The repo already has a bounded Voice-to-Browser Agent with transcript, fixture, uploaded-audio, ASR review, confirmation, trace, live-controlled, real-vision, and real-voice evidence paths. The current Operator Console exposes those internals directly: users must understand fixture IDs and execution modes before getting useful feedback, and transcript-based execution does not automatically reuse the live-controlled route even when the selected command is compatible with a controlled target.

The next improvement is a real-use console layer, not a new broad autonomous browser product. It should keep the existing safety model: controlled local targets first, public tasks as preview by default, optional public-readonly only if explicitly gated, and sanitized evidence only.

## Goals / Non-Goals

**Goals:**

- Make the default UI command-first: input or review one command, run it, then see the route, readiness, execution evidence, and final state.
- Introduce deterministic task routing between normalized commands, controlled local targets, preview-only tasks, clarification states, and optional public-readonly candidates.
- Improve visual design into a polished operator tool: compact, readable, responsive, with primary workflow controls separated from advanced replay/debug controls.
- Preserve inspectability: raw trace JSON, fixture replay, execution mode override, and export remain available but not required for the normal path.
- Add a controlled GitHub-like local showcase target so GitHub-shaped commands can show visible browser action without relying on github.com.
- Define `live_public_readonly` as an optional spike guarded by allowlists and safety stops, not a default execution mode.

**Non-Goals:**

- Unrestricted public web browsing, login completion, account mutation, purchases, posting, private data entry, or long-horizon planning.
- Claiming production automation, benchmark performance, ASR/TTS quality, or model fine-tuning results.
- Publishing raw audio, raw screenshots, live website traces, cookies, credentials, private URLs, browser profiles, or remote host details.
- Replacing `browser-use-vision`; the project continues to consume it as the Visual Grounding Engine dependency.

## Decisions

1. **Add a route-selection layer before execution**

   Introduce a small deterministic route selector after normalization and validation. It should return a structured route decision such as `controlled_live`, `demo_preview`, `clarification`, `blocked`, or optional `public_readonly_candidate`, with the reason, selected target, supported modes, and user-facing explanation.

   Alternative considered: infer execution mode directly in frontend JavaScript. That keeps the UI quick to change but duplicates backend safety decisions and makes API tests weaker. The route selector belongs near normalization/execution so fixture, transcript, and reviewed-audio paths share the same decision.

2. **Use controlled local showcase pages for visible real effects**

   Add a controlled GitHub-like page and route GitHub-shaped commands to it when the operator asks for a live controlled demo. This gives visible browser action, page title/state evidence, and safe repeatability while preserving the project's "controlled first" evidence boundary.

   Alternative considered: immediately open github.com for every GitHub command. That is more visually satisfying but introduces network variance, logged-in browser/profile risk, cookie leakage, and public trace ambiguity before the project has a public-readonly safety contract.

3. **Keep public-readonly as opt-in spike**

   If implemented in this change, `live_public_readonly` must be disabled by default and require explicit config plus an allowlist. It must use an isolated browser context, avoid persistent profile/cookies, reject forms/submits/logins, enforce short step budgets, and mark traces as local/private unless sanitized by a specific public-readonly sanitizer.

   Alternative considered: remove public-readonly from this change. Keeping it as a spike in the design helps future implementation make a conscious decision rather than smuggling public browsing into `live_controlled`.

4. **Separate primary workflow from advanced controls**

   The first viewport should show readiness, one command input/review path, run action, route decision, and live evidence. Fixture selection, execution mode override, raw JSON, and export controls move into advanced panels or tabs.

   Alternative considered: only restyle the existing form. That would make the page prettier but would not solve the user's actual workflow friction: manual dropdown selection and unclear preview/live outcomes.

5. **Use evidence-oriented UI polish**

   The console should look like an operational reliability tool rather than a landing page: dense layout, restrained color, clear status chips, route/evidence cards, accessible labels, stable dimensions, and responsive behavior. If the `taste` skill is available locally during implementation, use it for an additional UI review; otherwise follow the project frontend guidance and verify with screenshots.

## Risks / Trade-offs

- **Route selector picks the wrong controlled target** -> Keep matching deterministic, expose the route explanation, and require route-selection tests for common Chinese-first commands.
- **The UI hides important debug controls** -> Preserve advanced fixture replay, execution mode override, trace JSON, and export as explicit secondary panels.
- **Controlled GitHub-like page feels less real than github.com** -> Label it as controlled live evidence, make the visible action clear, and keep optional public-readonly as a separately gated spike.
- **Public-readonly mode expands scope too far** -> Keep it disabled by default, allowlisted, isolated, read-only, short-budget, and private/local unless sanitized explicitly.
- **Visual redesign breaks trace/audit workflows** -> Add tests for DOM controls, route summaries, evidence panel fields, and raw trace access; verify manually with browser screenshots during apply.

## Migration Plan

1. Add route decision models and route-selection tests without changing execution behavior.
2. Add controlled local GitHub-like page and metadata.
3. Wire transcript/reviewed-audio runs through route selection while preserving fixture replay endpoints.
4. Redesign the console around the primary command flow and advanced panels.
5. Add optional public-readonly spike only after controlled live routing is green.
6. Update docs/evidence artifacts and validate OpenSpec, tests, and screenshot-based UI checks.

Rollback is straightforward because the change can preserve existing API endpoints and advanced fixture replay. If route selection fails, the UI can fall back to explicit fixture replay and demo-preview behavior.

## Open Questions

- Should `live_public_readonly` be implemented in this change or left as a documented spike task only?
- Should the controlled GitHub-like page mimic GitHub search closely, or remain visibly branded as a local controlled public-code-search fixture?
- Should route decisions be stored as first-class trace fields or inside `execution_runtime` for this iteration?
