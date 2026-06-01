## Context

The Operator Console is a local FastAPI-served static web surface implemented with `index.html`, `styles.css`, and `app.js`. It already exposes command input, ASR review, readiness, route decisions, visible results, execution evidence, timelines, task-pack status, and raw trace JSON. The current weakness is not missing backend capability; it is visual hierarchy and operator comprehension. Dense evidence fields can make the console look like a debug page even when the underlying execution and privacy boundaries are correct.

This design uses `ui-ux-pro-max` as a design-system and UX review input. The relevant guidance is a professional, data-dense operations dashboard with status colors, accessible contrast, stable responsive layout, visible focus states, and reserved space for dynamic content. The skill is not a runtime dependency and should not force a framework migration.

## Goals / Non-Goals

**Goals:**

- Make the first viewport communicate what the operator can do, what the local environment can execute, and what the latest result proves.
- Preserve the command-first flow while keeping fixture replay, task-pack rows, and raw trace JSON available as secondary details.
- Apply consistent visual primitives for panels, status chips, outcome badges, privacy/export labels, timeline rows, evidence cards, and visual-result previews.
- Keep real public-readonly evidence local/private unless sanitizer status explicitly says otherwise.
- Improve desktop and narrow viewport behavior with stable grid tracks, predictable spacing, and no overlapping or clipped controls.
- Add enough tests and browser screenshot checks to catch broken DOM contracts, missing labels, layout regressions, and stale static assets.

**Non-Goals:**

- Do not replace the static HTML/CSS/JS console with React, Tailwind, shadcn, or a design-system package.
- Do not change backend route-selection, ASR, normalizer, browser execution, trace schemas, sanitizer behavior, or public-readonly policy.
- Do not make the page a marketing landing page or hide audit evidence that reviewers need.
- Do not claim public-safe evidence from local/private screenshots, task-pack rows, or raw traces unless sanitizer approval is explicit.

## Decisions

### Keep the static frontend architecture

Use the existing FastAPI static files and DOM ids. The console already has focused tests that assert element ids, strings, and JavaScript field names. Preserving this architecture keeps the UI polish low risk and avoids a frontend build pipeline.

Alternatives considered:
- React or Next.js: better component structure, but adds tooling and test churn that does not serve this scoped polish.
- Tailwind: faster token iteration, but the repo currently uses plain CSS and does not need a build step.

### Use an operations dashboard information hierarchy

Organize the first screen around:
1. Header and global execution/readiness summary.
2. Primary command and audio-review controls.
3. Route decision, execution evidence, and visible result.
4. Timeline and normalized output.
5. Advanced replay, task-pack details, and raw trace inspection.

This reflects the actual operator workflow and keeps audit-heavy details available without letting them dominate the default view.

### Use semantic CSS tokens and state classes

Define semantic tokens for surfaces, borders, text, focus rings, and statuses. Use a light professional console palette with neutral surfaces and distinct semantic state colors for ready, warning, blocked, failed, completed, partial, local/private, public-safe, and sanitizer-pending states.

Alternatives considered:
- Full dark developer-tool palette: attractive for demos, but less readable for interview review and more likely to hide privacy labels.
- One accent-heavy palette: visually louder, but weaker for repeated operations and status comparison.

### Treat evidence status as text plus color

Every important state should be readable as text. Color can reinforce state, but completion, failure, privacy, export, and sanitizer status must not rely on color alone. This is especially important for public-readonly traces where visual success styling can overstate what was proved.

### Reserve space for dynamic content

Use explicit min-height, grid constraints, aspect-ratio, and overflow rules for dynamic cards, screenshot previews, task-pack rows, and preformatted JSON. This reduces layout shift when readiness or execution results load.

### Verify visually as well as functionally

Implementation should include DOM/static tests and browser verification. At minimum, open the console locally and inspect screenshots at desktop and mobile widths. When possible, use Playwright or the in-app browser to catch overlap, clipped text, empty visual-result containers, and stale asset-cache problems.

## Risks / Trade-offs

- Status styling could accidentally imply success for partial, stopped, blocked, or local/private evidence -> keep outcome classes tied to completion state and render explicit text labels.
- UI polish could obscure auditability -> keep raw trace JSON and task-pack rows accessible behind disclosures.
- Responsive changes could break existing static tests -> preserve ids and user-facing strings that tests rely on, updating tests only for intentional UI contract changes.
- New visual tokens could become ad hoc CSS sprawl -> define reusable classes for panel, chip, badge, section header, evidence grid, and timeline patterns.
- Browser screenshot checks can be environment-sensitive -> use them as visual QA evidence, while keeping deterministic unit/static tests as the required verification floor.

## Migration Plan

1. Update the static console markup and CSS tokens in place while preserving existing element ids and API calls.
2. Refactor rendering helpers only where needed to emit consistent status chips, panel summaries, and disclosure sections.
3. Update or add focused static tests for hierarchy, labels, collapsed details, semantic status classes, and static asset versioning.
4. Run focused UI tests, full pytest when practical, OpenSpec strict validation, `git diff --check`, and browser screenshot checks at representative desktop and mobile widths.
5. Rollback is a normal git revert of the static UI commit because no backend schema or data migration is introduced.
