## 1. Console Flow Contract

- [x] 1.1 Add OpenSpec proposal, design, specs, and tasks for the improved Operator Console demo flow.
- [x] 1.2 Add or update demo documentation explaining transcript, fixture, audio, preview, live-controlled, clarification, confirmation, and export paths.

## 2. Fixture Metadata and Backend Behavior

- [x] 2.1 Add failing API tests for fixture metadata and unsupported live-controlled fixture explanation.
- [x] 2.2 Implement a fixture metadata endpoint derived from fixture manifests and selected live-controlled tasks.
- [x] 2.3 Ensure unsupported live-controlled fixture requests return a clear user-visible reason.

## 3. Operator Console UI

- [x] 3.1 Add failing UI tests for distinct transcript, fixture, and uploaded-audio execution controls.
- [x] 3.2 Update the console HTML/JS to store uploaded or recorded `audio_id` and execute it from the UI.
- [x] 3.3 Update fixture/mode selection so preview-only fixtures cannot silently appear to run live-controlled.
- [x] 3.4 Add a compact execution summary and clearer timeline labels without hiding raw trace JSON.

## 4. Verification and Archive

- [x] 4.1 Run targeted API/UI/demo tests for the new console flow.
- [x] 4.2 Run `openspec validate improve-operator-console-demo-flow --strict`.
- [x] 4.3 Run `openspec validate --all --strict`.
- [x] 4.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 4.5 Check `git status --short --ignored` and confirm no private runtime artifacts are staged.
