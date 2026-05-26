## Context

Stage 1 introduced the bounded Voice-to-Browser Agent, archived its OpenSpec change, and committed a fixture-backed demo-preview evidence set. The current executor already has two paths: dry-run mode emits a `demo_preview` action with `demo_preview_not_executed`, while non-dry-run mode instantiates `VisionEnhancedAgent` through the `browser-use-vision` package boundary and coerces the agent result into `BrowserExecutionResult`.

Phase 2 should make that non-dry-run path demonstrable on controlled visual pages. The change should keep the browser session local, preserve the existing normalizer, validator, confirmation gate, and trace model, and produce only sanitized public artifacts.

## Goals / Non-Goals

**Goals:**

- Run at least two controlled visual-grounding-heavy demo tasks through non-dry-run local browser execution.
- Keep demo-preview and live-controlled execution modes explicit in runtime metadata, API responses, Operator Console display, docs, and trace artifacts.
- Capture browser action events, screenshot or sanitized screenshot references, grounding evidence references, final status, and failure or stop reason for live-controlled runs.
- Store live public artifacts separately from demo-preview artifacts, using sanitized trace output only.
- Keep `browser-use-vision` as the Visual Grounding Engine dependency rather than copying visual grounding internals.

**Non-Goals:**

- Deploy or evaluate real ASR backends such as SenseVoice, FunASR, or faster-whisper on raw audio.
- Claim public website success rates or create a benchmark leaderboard.
- Make all eight demo tasks live-executed in this change.
- Add authentication, database persistence, multi-user sessions, distributed orchestration, or remote browser execution.
- Commit raw screenshots, browser profiles, cookies, raw audio, private traces, credentials, remote host details, or live browser state.

## Decisions

### Use explicit execution modes

Represent execution mode as a small runtime concept with values such as `demo_preview` and `live_controlled`. Dry-run behavior stays available for reproducible preview traces. Live controlled tasks use non-dry-run execution and must record mode metadata in the trace response and sanitized exports.

Alternatives considered:

- Use only the existing boolean `dry_run`: simple, but too ambiguous for docs, console display, and artifact review.
- Replace dry-run entirely: would remove a useful stable fixture path from Stage 1.

### Start with a narrow controlled task subset

The first live set should include two or three controlled visual pages, with `icon-search` and `color-swatch` as the initial targets and one dashboard or SVG task as an optional third. These pages are local, deterministic, and visual-grounding-heavy enough to show why `browser-use-vision` matters.

Alternatives considered:

- Run all eight demo tasks live: too broad for the first evidence upgrade and mixes public website volatility into the milestone.
- Start with public websites: visually impressive, but weaker as reproducible reliability evidence.

### Keep local browser execution with optional remote vision inference

The Operator Console, browser session, Playwright/Chromium execution, and trace capture remain local. Remote URLs may be passed only as model inference backends for visual grounding. The implementation must not require a remote browser session or hardcoded remote host details.

Alternatives considered:

- Run the whole browser agent remotely: complicates browser state, demo visibility, and artifact sanitization.
- Wrap `browser-use-vision` as a service: adds orchestration overhead without improving the Phase 2 proof.

### Separate live artifacts from preview artifacts

Live public traces should live under a distinct checked-in artifact path, for example `fixtures/traces/live-sanitized/`, while private runtime traces and raw screenshots stay ignored. Sanitized traces can include stable local fixture identifiers, action descriptions, sanitized screenshot references, grounding evidence references, status, and failure or stop reasons.

Alternatives considered:

- Overwrite Stage 1 sanitized traces: obscures which evidence came from preview mode.
- Commit raw live traces: conflicts with the established Sanitized Demo Artifact boundary.

### Treat failure as evidence when complete

Phase 2 does not require every selected task to succeed. A live trace may end in `failed` or `stopped` if it records enough action, grounding, and reason data to explain the failure. Empty, ungrounded, or mode-ambiguous traces do not count as live controlled evidence.

Alternatives considered:

- Require 100% live success: risks optimizing for a polished recording instead of evidence.
- Accept any non-dry-run attempt: too weak; the trace must show meaningful execution evidence.

## Risks / Trade-offs

- `browser-use-vision` API mismatch or missing model configuration -> keep the executor adapter isolated, preserve mock/lightweight integration tests, and document required live backend settings.
- Local Chromium or Playwright launch failures -> keep controlled page tests separate from live agent tests and record environment diagnostics in private runtime logs, not public artifacts.
- Live traces accidentally expose browser state -> sanitize exports and keep raw runtime traces, screenshots, browser profiles, and logs ignored by default.
- Selected visual tasks still fail -> record failure reason and grounding evidence rather than hiding the run; use the trace to decide the next implementation step.
- Execution mode leaks into unrelated APIs -> keep mode metadata small and trace-oriented rather than redesigning core schemas broadly.

## Migration Plan

This is an additive change. Existing Stage 1 preview fixtures and sanitized traces stay valid. Implementation can be rolled back by leaving `VOICE_BROWSER_DEMO_DRY_RUN=true` and not publishing live-controlled artifacts until the selected tasks produce acceptable sanitized traces.

## Open Questions

- Which dashboard-style task should be the optional third live target: `svg-dashboard` or `dashboard-compare`?
- Should live-controlled traces use checked-in sanitized screenshot references immediately, or only grounding evidence JSON references until screenshot sanitization is hardened?
- Which minimal `browser-use-vision` backend configuration is acceptable for a reproducible local run on this machine?
