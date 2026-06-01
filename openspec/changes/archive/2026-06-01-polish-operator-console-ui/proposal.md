## Why

The current Operator Console exposes the right execution evidence, but it still reads like a plain debug surface: dense status fields, raw JSON, task-pack details, and command controls compete for attention. This change upgrades the console into a polished local operations dashboard so reviewers can understand the voice-to-browser loop quickly without weakening the project's bounded safety and privacy claims.

## What Changes

- Refine the console information architecture around the primary operator workflow: command input, readiness, route decision, execution evidence, visible result, timeline, and inspectable trace details.
- Introduce a cohesive visual system for panels, status chips, outcome badges, privacy/export labels, spacing, focus states, and responsive breakpoints.
- Keep advanced replay, task-pack row details, and raw trace JSON available but visually secondary by default.
- Improve desktop and narrow-viewport layouts so dynamic status content does not clip, overlap, or cause avoidable layout shifts.
- Preserve the existing backend APIs, static app architecture, safety semantics, sanitizer boundaries, and public-readonly local/private evidence labels.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `operator-console`: strengthen visual-quality, workflow hierarchy, accessibility, responsive behavior, and privacy-aware evidence presentation requirements for the existing local Operator Console.

## Impact

- Affected code: `voice-browser-agent/src/voice_browser_agent/static/index.html`, `voice-browser-agent/src/voice_browser_agent/static/styles.css`, `voice-browser-agent/src/voice_browser_agent/static/app.js`, and focused UI/static tests.
- Affected specs: `operator-console`.
- No backend API, trace schema, browser execution, ASR, normalizer, sanitizer, or public-readonly policy changes are expected.
- Validation should include focused console tests, full pytest when practical, OpenSpec strict validation, `git diff --check`, and browser screenshots at desktop and mobile widths.
