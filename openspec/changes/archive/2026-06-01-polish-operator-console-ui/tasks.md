## 1. Baseline And Design System

- [x] 1.1 Capture the current Operator Console desktop and narrow-viewport screenshots for visual comparison.
- [x] 1.2 Map the current static UI structure, DOM ids, render helpers, and tests that must remain stable.
- [x] 1.3 Translate the `ui-ux-pro-max` operations-dashboard guidance into local CSS tokens for surfaces, typography, spacing, focus, and semantic statuses.

## 2. Layout And Visual Polish

- [x] 2.1 Rework the shell/header/readiness area so the first viewport reads as a local operations console rather than a debug page.
- [x] 2.2 Reorganize the command-first workflow so command input and audio review remain primary while advanced replay stays secondary.
- [x] 2.3 Polish route decision, execution evidence, visible result, and timeline panels with consistent panel headers, cards, chips, and badges.
- [x] 2.4 Add responsive grid constraints, reserved visual-result space, preformatted-content overflow rules, and mobile stacking behavior that prevents clipped text or horizontal page scrolling.

## 3. Evidence Semantics And Accessibility

- [x] 3.1 Render execution outcomes, readiness states, privacy states, sanitizer states, and export states with explicit text plus semantic classes.
- [x] 3.2 Keep partial, stopped, failed, blocked, confirmation-required, clarification-required, preview-only, and local/private states visually distinct from successful live execution.
- [x] 3.3 Keep task-pack rows, normalized JSON, fixture replay, and raw trace JSON inspectable behind disclosures or lower-priority sections.
- [x] 3.4 Add or preserve accessible labels, visible focus states, stable interaction targets, and reduced-motion-safe transitions.

## 4. Tests And Verification

- [x] 4.1 Update focused static UI tests for the new hierarchy, semantic classes, disclosure behavior, and static asset cache version.
- [x] 4.2 Run focused console tests and public-readonly UI evidence tests.
- [x] 4.3 Run full `uv run pytest`, `OPENSPEC_TELEMETRY=0 openspec validate --all --strict`, and `git diff --check`.
- [x] 4.4 Verify the local console in a browser at desktop and mobile widths, saving or reporting screenshots and any remaining layout risks.
- [x] 4.5 Generate or update the Chinese Human Brief HTML for this OpenSpec phase with links to the proposal, design, spec delta, tests, and visual evidence.
