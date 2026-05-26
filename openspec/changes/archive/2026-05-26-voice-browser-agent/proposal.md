## Why

The current portfolio already demonstrates agent evaluation, GUI execution evidence chains, and visual grounding as separate reliability projects. The missing piece is an end-to-end multimodal agent application that turns Chinese spoken intent into safe, traceable browser execution while reusing the existing `browser-use-vision` plugin.

This change proposes a bounded Voice-to-Browser Agent rather than another benchmark or a general real-time voice assistant. It should show that speech input, command normalization, visual grounding, browser execution, safety gates, and execution traces can work together in a reproducible demo system.

## What Changes

- Introduce a new `voice-browser-agent` application project with a minimal Operator Console.
- Add ASR adapters for single-utterance Spoken Command Execution, with a SenseVoice-first default and a faster-whisper fallback.
- Add a Spoken Command Normalizer that converts noisy Chinese-first ASR transcripts into either a structured Browser Task Request or a Clarification Request.
- Add deterministic validation for normalized requests, including bounded Browser Intent Types, required fields, stop conditions, and safety flags.
- Add a Confirmation Gate that pauses or blocks destructive, private, or irreversible actions.
- Integrate `browser-use-vision` as a package dependency and Visual Grounding Engine rather than copying or merging its code.
- Add browser execution through browser-use and local Playwright/Chromium, with optional remote GPU services for visual or ASR inference.
- Add Execution Trace artifacts for each command, including transcript, normalized request, validation result, confirmation decision, browser actions, grounding evidence, final status, and failure reason.
- Add a Demo Task Suite of 8-12 controlled and public non-destructive tasks, with at least half being visual-grounding-heavy.
- Add sanitized demo artifacts, reproducible audio fixtures, quickstart documentation, and 2-3 demo ablations that show why the normalizer, visual grounding, and confirmation gate matter.

## Capabilities

### New Capabilities

- `spoken-command-ingestion`: Accept one recorded or uploaded Chinese-first spoken command, transcribe it through an ASR adapter, and expose transcript metadata for downstream normalization.
- `spoken-command-normalization`: Convert noisy ASR transcripts into structured Browser Task Requests or Clarification Requests using LLM structured output plus deterministic validation.
- `safe-browser-execution`: Execute bounded browser tasks through browser-use with `browser-use-vision` visual grounding, confirmation gating, stop conditions, and local/remote runtime separation.
- `operator-console`: Provide a minimal web console that shows audio input, transcript, normalized request, execution timeline, screenshots, trace status, and optional status voice feedback.
- `demo-evidence-set`: Provide reproducible demo tasks, audio fixtures, sanitized traces, and demo ablations without positioning the project as a benchmark or leaderboard.

### Modified Capabilities

- None.

## Impact

- New project files for a Python/FastAPI backend, Pydantic schemas, ASR/TTS adapter interfaces, normalizer, validator, confirmation gate, browser executor integration, trace writer, and minimal web UI.
- New dependency on `browser-use-vision` as a reusable Visual Grounding Engine.
- New dependency on browser-use/Playwright for browser execution.
- Optional dependencies for SenseVoice, faster-whisper, status TTS, and remote GPU model services.
- New sanitized demo fixtures and trace artifacts suitable for public GitHub documentation.
- No changes to `browser-use-vision` internals are required by this change.
