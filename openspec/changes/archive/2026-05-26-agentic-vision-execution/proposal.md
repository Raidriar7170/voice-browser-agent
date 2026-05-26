## Why

The project now has fixture-backed preview traces and a narrow live-controlled path, but execution is still closer to a single normalized task handoff than an inspectable vision-guided agent loop. This change makes the browser execution layer more agentic while keeping the project bounded, local-first, and evidence-driven.

## What Changes

- Add a bounded agentic vision execution loop that repeatedly observes the browser state, resolves visual targets through `browser-use-vision`, chooses the next browser action, executes it, and verifies progress.
- Record step-level execution evidence: visual observations, chosen action, grounding references, action result, verification decision, and stop or recovery reason.
- Add recovery behavior for common visual execution failures such as missing target, ambiguous visible target, stale page state, and action with no meaningful page change.
- Keep the loop constrained by Browser Task Request fields, stop conditions, confirmation gates, maximum step budget, and supported Browser Intent Types.
- Update the Operator Console to show the agentic step timeline rather than only a coarse final execution result.
- Add sanitized agentic execution evidence for selected controlled visual tasks, plus small demo ablations that explain why re-observation and visual target resolution matter.
- Keep browser execution local by default and continue using `browser-use-vision` as the Visual Grounding Engine dependency; do not copy visual grounding internals into this repo.
- Do not add unrestricted open-web autonomy, long-horizon task planning, production browser profiles, remote browser execution, ASR/TTS model research, or benchmark/SOTA claims.

## Capabilities

### New Capabilities

- `agentic-vision-execution`: Bounded observe-act-verify browser execution loop that uses visual grounding evidence to perform and audit multi-step browser actions.

### Modified Capabilities

- `safe-browser-execution`: Route validated Browser Task Requests through the bounded agentic loop, enforce step budgets and recovery stops, and preserve confirmation gates before sensitive actions.
- `operator-console`: Display agentic execution steps, visual observations, grounding references, action results, recovery decisions, and final status.
- `demo-evidence-set`: Add sanitized agentic execution traces and demo ablations for selected visual-grounding-heavy controlled tasks.

## Impact

- Affects the browser executor, trace model, safety handling around action loops, controlled demo fixture replay, sanitized trace export, Operator Console timeline rendering, and demo documentation.
- May add small adapters around the existing `browser-use-vision` dependency so observations and grounding evidence can be represented consistently in Execution Traces.
- Requires tests for bounded step execution, recovery/stop behavior, confirmation gate preservation, sanitized exports, and console rendering.
- Does not require schema-breaking public API changes, database persistence, auth, distributed orchestration, or remote browser sessions.
