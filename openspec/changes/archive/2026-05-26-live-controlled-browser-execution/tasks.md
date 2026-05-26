## 1. Execution Mode and Trace Model

- [x] 1.1 Add an explicit execution mode field or runtime metadata value that distinguishes `demo_preview` from `live_controlled`.
- [x] 1.2 Update `BrowserExecutorConfig` and executor results so dry-run preview and live controlled execution are visible in trace responses.
- [x] 1.3 Ensure live controlled runs that return no action or grounding evidence are marked failed or stopped with an explicit reason.
- [x] 1.4 Add unit tests for execution mode metadata and empty live evidence rejection.

## 2. Controlled Live Fixture Routing

- [x] 2.1 Define the selected live controlled task set with `icon-search` and `color-swatch` as required targets and one dashboard or SVG task as optional.
- [x] 2.2 Wire controlled page targets into fixture replay so selected fixtures can launch local `file://` or local-server demo pages.
- [x] 2.3 Add configuration or API handling for running selected fixture executions with `VOICE_BROWSER_DEMO_DRY_RUN=false`.
- [x] 2.4 Add tests that preview mode still produces `demo_preview_not_executed` while live controlled mode calls the non-dry-run executor path.

## 3. Browser-Use-Vision Live Path

- [x] 3.1 Verify the `VisionEnhancedAgent` import and constructor path used by the executor against the current local `browser-use-vision` dependency.
- [x] 3.2 Pass normalized task text, constraints, visual references, stop conditions, controlled target URL, and optional remote vision backend URL into the live executor.
- [x] 3.3 Run the `icon-search` controlled page through a non-dry-run live controlled execution path and capture trace evidence.
- [x] 3.4 Run the `color-swatch` controlled page through a non-dry-run live controlled execution path and capture trace evidence.
- [x] 3.5 Optionally run one dashboard or SVG controlled task if the first two live runs expose enough stable executor behavior.

## 4. Sanitized Live Evidence Artifacts

- [x] 4.1 Add a distinct public artifact path for live controlled sanitized traces, such as `fixtures/traces/live-sanitized/`.
- [x] 4.2 Generate sanitized live controlled traces for at least two selected visual-grounding-heavy tasks.
- [x] 4.3 Verify live sanitized traces exclude raw audio, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, and unsanitized live browser state.
- [x] 4.4 Update demo documentation to distinguish demo-preview artifacts from live-controlled artifacts without benchmark or SOTA wording.

## 5. Operator Console Visibility

- [x] 5.1 Display execution mode in the Operator Console for preview and live controlled traces.
- [x] 5.2 Display live controlled action descriptions, screenshot references when sanitized, grounding evidence references, final status, and failure or stop reason in the timeline.
- [x] 5.3 Ensure the trace export control returns sanitized live controlled traces and does not expose raw runtime fields.
- [x] 5.4 Add frontend or API smoke tests for live controlled mode labeling and timeline rendering.

## 6. Verification

- [x] 6.1 Run `openspec validate live-controlled-browser-execution --strict`.
- [x] 6.2 Run `openspec validate --all --strict`.
- [x] 6.3 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 6.4 Check `git status --short --ignored` and verify runtime traces, browser profiles, caches, raw screenshots, raw audio, secrets, and remote host details are not staged.
