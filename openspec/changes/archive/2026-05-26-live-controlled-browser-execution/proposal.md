## Why

Stage 1 proves the Voice-to-Browser Agent architecture, safety gates, fixtures, and trace format, but the checked-in traces are explicit demo-preview artifacts. The next reliability step is to prove a small number of controlled visual tasks through non-dry-run local browser execution while preserving the same bounded, sanitized evidence discipline.

## What Changes

- Add an explicit live controlled execution mode for selected visual-grounding-heavy demo tasks.
- Run at least two controlled visual tasks through local browser execution with `browser-use-vision` instead of the dry-run preview path.
- Record live browser actions, grounding evidence references, final status, and failure or stop reasons in sanitized trace artifacts.
- Distinguish demo-preview traces from live-controlled traces in the Operator Console and demo documentation.
- Keep public artifacts sanitized and avoid committing raw screenshots, live browser state, credentials, remote host details, or raw audio.
- Keep ASR model deployment, public website success claims, benchmark tables, and platform orchestration out of this change.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `safe-browser-execution`: Add requirements for non-dry-run controlled visual task execution, mode separation, live action capture, and local browser/runtime boundaries.
- `demo-evidence-set`: Add requirements for live controlled sanitized traces that complement the existing fixture-backed demo-preview evidence.
- `operator-console`: Add requirements for clearly showing live-controlled execution mode, timeline events, grounding evidence references, and sanitized export state.

## Impact

- Affects `voice-browser-agent` executor configuration, controlled fixture replay, trace writing/export, demo documentation, and Operator Console display.
- May add test-only or lightweight adapters to make live controlled runs reproducible without depending on public website changes.
- Continues to depend on `browser-use-vision` through the existing package boundary; no visual grounding code is copied into this repo.
- Does not require schema-breaking API changes, authentication, database work, or remote browser execution.
