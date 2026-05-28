## Why

The current Operator Console still feels like an internal debugging harness: the operator must choose fixture and execution-mode dropdowns before seeing a useful live result, and transcript runs silently fall back to `demo_preview`. This change makes the console match the real-use story the project now needs to demonstrate: one command in, automatic routing, clear safety/readiness feedback, and visible evidence when a controlled live browser task actually ran.

## What Changes

- Redesign the Operator Console around a primary command-first workflow instead of fixture-first controls.
- Add automatic task routing that maps entered or reviewed commands to supported controlled live targets when safe, and clearly explains preview-only or unsupported requests.
- Move fixture selection, execution mode, raw trace JSON, and export controls into advanced/inspectable surfaces so the default flow is usable without dropdown choreography.
- Add a live result/evidence panel that surfaces browser state, page title, action result, screenshot/evidence references, stop/failure reasons, and whether the run was preview, controlled live, or optional public-readonly.
- Add a controlled GitHub-like local showcase path so commands such as "打开 GitHub" can show a visible browser effect without depending on external websites or leaking live website state.
- Add an explicit optional spike for `live_public_readonly` execution against allowlisted public pages. This mode must stay off by default unless the implementation proves no login, form submission, cookie/profile reuse, destructive action, or public artifact leakage.
- Add UI quality requirements for a polished, dense operator tool surface. If a `taste` skill is installed locally, use it during implementation review; otherwise apply the repo's frontend guidance and verify with browser screenshots.

## Capabilities

### New Capabilities
- `operator-task-routing`: Maps free-form transcript/reviewed-audio commands to supported execution routes, controlled targets, preview explanations, clarification states, or optional public-readonly candidates.

### Modified Capabilities
- `operator-console`: Changes the console from a fixture-first debug UI to a command-first real-use workflow with advanced controls, readiness-aware actions, and visible live evidence.
- `safe-browser-execution`: Adds controlled local showcase routing for GitHub-like tasks and defines the optional `live_public_readonly` safety boundary without making unrestricted public-web automation a default capability.
- `demo-evidence-set`: Adds evidence expectations for the improved console flow, controlled showcase task, and clear preview-vs-live result presentation.

## Impact

- Affected frontend files: `voice-browser-agent/src/voice_browser_agent/static/index.html`, `app.js`, and `styles.css`.
- Affected backend/API areas: route selection in `voice_browser_agent.app`, controlled task metadata in `demo_tasks.py`, execution mode handling in `models.py` and `executor.py`, and trace metadata for routed runs.
- Affected tests: operator console UI/API tests, safe execution tests, demo evidence tests, and likely new route-selection tests.
- Affected docs/artifacts: README Operator Console flow, demo task suite/useful scenarios, public evidence page, video plan, and closeout checklist.
- No public raw audio, raw screenshots, cookies, credentials, live website traces, private URLs, browser profile data, or remote host details may be introduced.
