## Context

Stage 1 established the bounded Voice-to-Browser Agent, fixture-backed demo-preview traces, a Normalizer Validator, Confirmation Gate, Operator Console, and sanitized artifact rules. The live-controlled follow-up proved a small non-dry-run browser path for selected controlled visual tasks, but the current executor result is still action-list oriented rather than a first-class observe-act-verify loop.

This change makes the execution layer more agentic without changing the project identity. `voice-browser-agent` owns the spoken-command flow, safety boundaries, orchestration, and traces. `browser-use-vision` remains the Visual Grounding Engine dependency that supplies visual observations, OCR/SoM/region evidence, and grounding references.

## Goals / Non-Goals

**Goals:**

- Add a bounded agentic vision execution loop for validated Browser Task Requests.
- Represent each execution step as observation, target resolution, action, verification, and recovery or stop decision.
- Preserve existing confirmation gates, stop conditions, local browser execution, and sanitized artifact boundaries.
- Make the Operator Console useful for inspecting why a visually grounded action succeeded, failed, retried, clarified, or stopped.
- Publish sanitized agentic traces and small ablations for selected controlled visual tasks.

**Non-Goals:**

- Build an unrestricted open-web autonomous agent or long-horizon planning system.
- Move browser execution to the remote GPU machine or expose remote host details.
- Copy or fork `browser-use-vision` internals.
- Replace the Spoken Command Normalizer, ASR adapters, or confirmation model.
- Claim benchmark results, SOTA visual grounding, or production browser automation readiness.
- Add auth, database persistence, multi-user sessions, LangGraph, Temporal, Ray, or Celery.

## Decisions

### Add an agentic step model beside existing action events

Introduce an execution-step representation, for example `AgenticVisionStep`, that can live on `ExecutionTrace` beside the existing `browser_actions` list. Each step records the step index, observation summary, visual target candidates or references, selected action, action result, verification decision, recovery decision, and related sanitized evidence references.

Existing `BrowserActionEvent` remains valid for coarse timeline compatibility and simple consumers. Agentic steps are the richer evidence surface; action events can be derived from them or linked to them.

Alternatives considered:

- Replace `browser_actions` entirely: cleaner model, but too disruptive for existing traces, tests, and console rendering.
- Store all step details in `execution_runtime`: quick to implement, but too unstructured for tests and sanitized artifact review.

### Keep execution mode stable and add execution style metadata

Reuse the existing `demo_preview` and `live_controlled` execution modes. Mark agentic runs through structured runtime or trace metadata such as `execution_style: agentic_vision` and through the presence of agentic step records.

Alternatives considered:

- Add a third execution mode such as `agentic_live_controlled`: expressive, but it mixes environment mode with executor style and forces more API churn.
- Hide the distinction in action descriptions: avoids schema work, but makes artifacts hard to audit.

### Own orchestration locally, delegate perception to `browser-use-vision`

Add an agentic executor/controller inside `voice-browser-agent` that calls a visual observation provider backed by `browser-use-vision`, selects bounded actions based on the Browser Task Request, executes through the local browser page, and verifies progress after each action.

The controller should depend on a narrow adapter interface so unit tests can provide deterministic observations and action results. The live adapter uses local Playwright/browser-use execution and optional remote visual inference only through the existing visual grounding dependency boundary.

Alternatives considered:

- Push the entire loop into `browser-use-vision`: weakens this project’s ownership of spoken-command execution and trace semantics.
- Add a large workflow framework: too much orchestration for an MVP that needs inspectable local behavior.

### Enforce bounded recovery instead of open-ended replanning

The loop should stop or ask for clarification when visual evidence is missing, ambiguous, stale, sensitive, or outside the normalized request. Limited recovery is allowed for controlled cases, such as one re-observation after a stale page state or one alternate target selection when evidence is clearly ranked.

The loop must obey maximum steps, supported Browser Intent Types, constraints, stop conditions, and confirmation gates before acting and after observing browser state.

Alternatives considered:

- Let the agent keep trying until success: makes failures less inspectable and risks unsafe or noisy automation.
- Stop on the first mismatch: safer, but does not demonstrate useful visual recovery behavior.

### Treat sanitized step evidence as the public deliverable

Public artifacts should include agentic step traces with stable fixture IDs, sanitized evidence references, summaries, statuses, and failure reasons. Raw screenshots, browser profiles, cookies, credentials, private URLs, raw audio, remote host details, and unsanitized runtime logs remain local or ignored.

The demo evidence should include at least two visual-grounding-heavy controlled tasks and small ablations that remove re-observation or visual target resolution to show why the agentic layer matters.

Alternatives considered:

- Publish only a polished video: useful for presentation, but too weak as engineering evidence.
- Commit raw screenshots and full browser traces: easier to inspect locally, but conflicts with the Sanitized Demo Artifact boundary.

## Risks / Trade-offs

- `browser-use-vision` observation APIs may not expose exactly the needed structure -> Keep a narrow adapter with deterministic tests and normalize returned evidence into project-owned trace schemas.
- Agentic traces can become noisy -> Use compact summaries and stable evidence references rather than dumping full model prompts, raw observations, or page state.
- Recovery behavior may accidentally look like unrestricted autonomy -> Bound retries, step count, intent types, and stop conditions in both code and docs.
- Confirmation gates may only be checked before execution -> Re-check sensitive browser state before every action and after every observation.
- Live controlled tasks may still fail -> Preserve failed or stopped runs when they include meaningful step evidence and reasons; do not count empty traces as evidence.
- Sanitization may miss a nested private field -> Extend existing sanitizer tests with agentic step payloads and private-key fixtures.

## Migration Plan

This is additive. Existing demo-preview and live-controlled traces remain valid. Implementation can first add step schemas and deterministic unit tests, then wire the controlled-page agentic executor behind the existing fixture execution API. If live agentic execution is unstable, keep `VOICE_BROWSER_DEMO_DRY_RUN=true` and publish no agentic live artifacts until sanitized traces pass validation.

Rollback is straightforward: disable the agentic execution style and fall back to the current preview/live-controlled action-list path.

## Open Questions

- Should the first public agentic traces cover exactly `icon-search` and `color-swatch`, or include `svg-dashboard` as a third trace if stable?
- Should sanitized screenshot thumbnails be generated in this change, or should traces initially contain references and textual summaries only?
- Should recovery decisions use a fixed enum immediately, or begin as structured strings and tighten after the first implementation pass?
