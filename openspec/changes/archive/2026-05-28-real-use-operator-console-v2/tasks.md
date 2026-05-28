## 1. Route-Selection Contract Tests

- [x] 1.1 Add tests for route decisions that map typed transcript commands to controlled live targets without manual fixture or execution-mode selection.
- [x] 1.2 Add tests that reviewed audio transcripts use the same route-selection rules while preserving audio id, ASR metadata, and transcript-review provenance.
- [x] 1.3 Add tests that public showcase commands remain preview-only or controlled-showcase unless optional public-readonly mode is explicitly enabled.
- [x] 1.4 Add tests that broad, unsafe, login, mutation, or unsupported commands return clarification, confirmation, blocked, or unsupported-route explanations instead of live execution.

## 2. Route-Selection Implementation

- [x] 2.1 Add route decision models or trace/runtime fields for route type, selected fixture, controlled target, evidence eligibility, route reason, and user-visible explanation.
- [x] 2.2 Implement a deterministic route selector after normalization and validation and before browser execution.
- [x] 2.3 Wire transcript execution and reviewed-audio execution through route selection while preserving existing fixture replay endpoints.
- [x] 2.4 Ensure route decisions are included in execution API responses and written traces without leaking raw private artifacts.

## 3. Controlled Showcase and Safe Execution

- [x] 3.1 Add a controlled local GitHub-like showcase page and metadata for a public-site-shaped command.
- [x] 3.2 Route supported GitHub-shaped commands to the controlled showcase for live controlled demonstration when selected by route rules.
- [x] 3.3 Keep real public website tasks preview-only by default and produce clear unsupported-route explanations when live execution is unavailable.
- [x] 3.4 If implementing the optional public-readonly spike, gate it behind explicit config, allowlists, isolated browser contexts, no persistent cookies, no login or mutation actions, short step budgets, and local/private trace handling.

## 4. Command-First Operator Console

- [x] 4.1 Redesign the console HTML structure around one primary command/review input, readiness status, run action, route decision, and execution evidence.
- [x] 4.2 Move fixture replay, execution-mode override, raw trace JSON, and sanitized export into advanced or inspectable controls.
- [x] 4.3 Update JavaScript to call route-aware execution paths, render route decisions, distinguish preview from live evidence, and display stop/failure reasons near the result summary.
- [x] 4.4 Update CSS for a polished, responsive operator tool layout with stable dimensions, readable status chips, clear evidence panels, and no overlapping or clipped text on desktop/mobile.
- [x] 4.5 If a local `taste` skill is available, use it for UI review; otherwise perform screenshot-based visual QA with the repo frontend guidelines.

## 5. Evidence and Documentation

- [x] 5.1 Update README Operator Console flow to describe the command-first path, automatic routing, advanced replay controls, and preview-vs-live interpretation.
- [x] 5.2 Update demo task/useful scenario docs, public evidence page, video plan, and closeout checklist for the controlled showcase and route-aware console flow.
- [x] 5.3 Update release-pack or evidence classification logic if routed traces require new route/evidence mode fields.
- [x] 5.4 Add or refresh sanitized evidence for the controlled showcase only if it can pass the existing privacy boundary.

## 6. Verification

- [x] 6.1 Run targeted route-selection, safe execution, operator console, and demo evidence tests.
- [x] 6.2 Run `openspec validate real-use-operator-console-v2 --strict`.
- [x] 6.3 Run `openspec validate --all --strict`.
- [x] 6.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 6.5 Run browser screenshot checks for desktop and mobile console layouts.
- [x] 6.6 Run `git diff --check`.
- [x] 6.7 Run `git status --short --ignored` and confirm generated runtime artifacts, raw audio, raw screenshots, private traces, browser profiles, and caches remain ignored.
