## 1. Trace Model and Sanitization

- [x] 1.1 Add structured agentic step models for observation, target resolution, action result, verification decision, recovery decision, and sanitized evidence references.
- [x] 1.2 Extend `ExecutionTrace` to carry agentic step evidence while preserving existing `browser_actions` compatibility.
- [x] 1.3 Update trace serialization and sanitized export handling for agentic step payloads.
- [x] 1.4 Add tests proving agentic traces exclude raw screenshots, raw audio, browser profile data, cookies, credentials, private URLs, remote host details, and unsanitized live browser state.

## 2. Agentic Vision Executor

- [x] 2.1 Add a narrow visual observation/action adapter interface around the existing `browser-use-vision` dependency boundary.
- [x] 2.2 Implement the bounded observe-act-verify loop with max step budget, supported Browser Intent Type checks, and request constraint propagation.
- [x] 2.3 Implement target resolution behavior for resolved, missing, ambiguous, and stale visual targets.
- [x] 2.4 Implement post-action verification and bounded recovery for no-effect actions or stale page state.
- [x] 2.5 Reject agentic live-controlled runs that return no step evidence, action events, or grounding evidence references.
- [x] 2.6 Add unit tests for success, step-budget stop, missing target stop, ambiguous target clarification/stop, stale-state recovery, and no-evidence failure.

## 3. Safety and Execution Routing

- [x] 3.1 Route selected live-controlled fixture executions through the agentic vision executor while leaving demo-preview behavior unchanged.
- [x] 3.2 Record `execution_style` or equivalent metadata for agentic runs without changing the existing execution mode semantics.
- [x] 3.3 Re-check Confirmation Gate and browser-state safety conditions before each agentic action and after each observation.
- [x] 3.4 Preserve existing stop condition handling and record matched stop conditions in the agentic trace.
- [x] 3.5 Add tests showing sensitive browser states pause, block, or stop before the next action.

## 4. Controlled Demo Integration

- [x] 4.1 Wire controlled visual tasks such as `icon-search` and `color-swatch` into the agentic executor path.
- [x] 4.2 Add deterministic adapter fixtures for visual observations, selected targets, action results, and verification decisions.
- [x] 4.3 Run at least two controlled visual-grounding-heavy tasks through agentic live-controlled execution and capture meaningful step evidence.
- [x] 4.4 Optionally add `svg-dashboard` as a third controlled agentic trace if it is stable in the local environment.

## 5. Operator Console and Public Evidence

- [x] 5.1 Render agentic step timelines in the Operator Console with observation summaries, selected actions, evidence references, verification decisions, recovery decisions, and final status.
- [x] 5.2 Ensure sanitized trace export includes agentic step summaries and omits private runtime fields.
- [x] 5.3 Add console/API smoke tests for agentic timeline rendering and sanitized export behavior.
- [x] 5.4 Generate public sanitized agentic trace artifacts in a path that is distinct from demo-preview and existing live-controlled traces.
- [x] 5.5 Update demo task documentation to distinguish demo-preview traces, live-controlled action-list traces, and agentic live-controlled traces.
- [x] 5.6 Update demo ablations to cover re-observation and visual target resolution without benchmark, leaderboard, or SOTA wording.

## 6. Verification

- [x] 6.1 Run `openspec validate agentic-vision-execution --strict`.
- [x] 6.2 Run `openspec validate --all --strict`.
- [x] 6.3 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 6.4 Check `git status --short --ignored` and confirm no private traces, raw screenshots, browser profiles, raw audio, credentials, caches, or remote host details are staged.
