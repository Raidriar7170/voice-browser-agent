## Why

The project now has strong demo evidence, real `browser-use-vision` controlled evidence, and public-safe artifacts, but it still lacks a committed proof that a real recorded or uploaded audio command can drive the same end-to-end browser execution path. To make the project feel genuinely usable rather than demo- or benchmark-shaped, the next step should prove a small real-use loop: audio input, ASR, operator transcript correction, safety gating, controlled visual execution, sanitized trace, and clear failure evidence.

## What Changes

- Add a real voice end-to-end controlled smoke workflow that can start from uploaded or recorded audio, use a configured ASR adapter, run a bounded controlled visual task, and export a sanitized `real_voice_controlled` trace.
- Add local readiness/preflight checks that explain whether ASR, browser automation, real visual grounding, and runtime privacy boundaries are ready before a user tries the app.
- Add an operator transcript review/correction step so real ASR output can be inspected and edited before normalization and browser execution.
- Add a small useful-scenario task pack that is closer to practical use than one-off demo fixtures while staying controlled, local, and non-destructive.
- Add failure and usage trace artifacts that show ASR unavailable, clarification, confirmation, ambiguous visual target, and successful real voice execution paths without exposing raw audio or private runtime state.
- Update reviewer/public evidence docs so the project is positioned as locally runnable real-use evidence, not broad automation, public hosting, model training, or benchmark results.

## Capabilities

### New Capabilities

### Modified Capabilities

- `spoken-command-ingestion`: require real audio E2E smoke evidence, ASR readiness checks, and clear unavailable-ASR behavior.
- `operator-console`: require transcript review/correction before executing real audio-derived commands and clearer readiness status for real-use runs.
- `safe-browser-execution`: require real audio-derived controlled execution traces to use the same safety gates and local controlled browser execution boundaries.
- `demo-evidence-set`: require a distinct real-use evidence pack with `real_voice_controlled`, useful-scenario, and failure/usage traces while preserving public privacy boundaries.
- `spoken-command-normalization`: require edited ASR transcript provenance to remain visible when a corrected transcript is normalized.

## Impact

- Affected backend code: `voice_browser_agent.app`, ASR orchestration, execution request payloads, trace writing, and fixture/controlled task helpers.
- Affected frontend code: Operator Console upload/recording flow, transcript preview/edit controls, readiness display, and evidence summary.
- Affected scripts: new or updated preflight, real voice trace generation, and evidence pack builders.
- Affected docs/artifacts: README, public evidence page, demo docs, sanitized trace fixtures, and OpenSpec specs.
- Dependencies remain optional: local `faster-whisper` is used only when installed through the existing `asr` extra or when a remote ASR endpoint is configured.
