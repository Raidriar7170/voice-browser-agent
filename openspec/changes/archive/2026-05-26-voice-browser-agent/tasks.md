## 1. Project Scaffold

- [x] 1.1 Create the `voice-browser-agent` project directory with Python 3.11 package metadata, source layout, tests, and README skeleton
- [x] 1.2 Add FastAPI, Pydantic, browser-use, Playwright, and local/editable `browser-use-vision` dependencies
- [x] 1.3 Add configuration loading for local runtime, optional remote vision backend, optional ASR backend, and ignored secret files
- [x] 1.4 Add `.gitignore` rules for raw audio, private traces, screenshots with live browser state, secrets, checkpoints, and remote host details

## 2. Core Schemas and Trace Model

- [x] 2.1 Define Pydantic models for Spoken Command input, ASR transcript metadata, Browser Task Request, Clarification Request, validation result, confirmation decision, and Execution Trace
- [x] 2.2 Define the bounded Browser Intent Type enum for search/open, click visual target, fill form, select filter or option, and extract/compare visible information
- [x] 2.3 Implement a trace writer that stores transcript, normalized output, validator decision, confirmation decision, browser actions, grounding evidence references, final status, and failure or stop reason
- [x] 2.4 Add unit tests for schema validation and trace serialization

## 3. Spoken Command Ingestion

- [x] 3.1 Implement audio upload ingestion for one audio clip per Spoken Command Execution
- [x] 3.2 Add optional browser recording endpoint or frontend hook while keeping uploaded fixtures as the stable path
- [x] 3.3 Implement the ASR Adapter interface with transcript metadata output
- [x] 3.4 Implement the Primary ASR Adapter wrapper for SenseVoice or a compatible local/remote service
- [x] 3.5 Implement a faster-whisper Fallback ASR Adapter
- [x] 3.6 Add tests for unsupported audio, primary ASR success, fallback ASR usage, and transcript metadata preservation

## 4. Spoken Command Normalization

- [x] 4.1 Implement the LLM structured-output normalizer that returns either Browser Task Request or Clarification Request
- [x] 4.2 Add prompt/context examples for Chinese-first commands with English code-switching and visual UI references
- [x] 4.3 Implement Normalizer Validator checks for required fields, supported intent type, stop conditions, visual references, and unsupported long-horizon goals
- [x] 4.4 Add safety-sensitive command detection for checkout, payment, deletion, posting, login, private-data entry, file transfer, and irreversible submit actions
- [x] 4.5 Add tests for clear commands, ambiguous commands, ASR-noisy commands, unsupported intents, safety-sensitive commands, and validator rejection paths

## 5. Confirmation Gate and Safety Stops

- [x] 5.1 Implement Confirmation Gate state transitions for pending, confirmed, cancelled, and blocked execution
- [x] 5.2 Pause before execution when a Browser Task Request requires confirmation
- [x] 5.3 Add browser-state stop checks for login required, checkout/payment, deletion, posting, private-data entry, and irreversible submit states
- [x] 5.4 Record confirmation and stop decisions in the Execution Trace
- [x] 5.5 Add tests for confirmation-required requests, cancellation, confirmed continuation, and browser-state safety stop detection

## 6. Browser Execution Integration

- [x] 6.1 Implement browser executor adapter that imports `VisionEnhancedAgent` from `browser-use-vision` directly
- [x] 6.2 Configure browser-use local Playwright/Chromium execution for bounded tasks
- [x] 6.3 Pass normalized task text, constraints, visual references, and stop conditions into the browser execution layer
- [x] 6.4 Support optional Remote Vision Backend configuration without wrapping `browser-use-vision` as a separate service
- [x] 6.5 Capture browser action events, screenshot references, visual grounding evidence references, final status, and failure reason into the Execution Trace
- [x] 6.6 Add integration smoke tests with controlled demo pages and a mocked or lightweight vision backend

## 7. Operator Console and API

- [x] 7.1 Implement FastAPI endpoints for audio ingestion, normalization preview, execution start, confirmation decision, trace retrieval, and sanitized trace export
- [x] 7.2 Build a minimal web Operator Console with audio upload, optional recording, transcript panel, normalized request panel, execution timeline, screenshot/trace panel, and final status
- [x] 7.3 Add UI handling for Clarification Requests without starting browser execution
- [x] 7.4 Add UI handling for Confirmation Gate prompts with confirm and cancel actions
- [x] 7.5 Add optional Status Voice Feedback for confirmation prompts, final success, stopped states, and failure explanations
- [x] 7.6 Add frontend/API smoke tests for the main happy path, clarification path, confirmation path, and trace viewing

## 8. Demo Task Suite and Fixtures

- [x] 8.1 Define 8-12 Demo Task Suite entries with expected audio fixture, browser intent type, visual grounding requirement, stop condition, and expected final status
- [x] 8.2 Ensure at least half of the Demo Task Suite is visual-grounding-heavy
- [x] 8.3 Reuse or adapt controlled pages from `browser-use-vision/demo` for icon-only, color swatch, canvas/SVG, dynamic SPA, dashboard, and ecommerce scenarios
- [x] 8.4 Add 2-3 public non-destructive showcase tasks that do not require login or private data
- [x] 8.5 Create Reproducible Audio Fixtures for the stable demo path
- [x] 8.6 Generate sanitized example traces for each demo task

## 9. Demo Ablations and Public Documentation

- [x] 9.1 Add a demo ablation showing a visual-grounding-heavy task without visual grounding
- [x] 9.2 Add a demo ablation showing noisy ASR transcript behavior without the Spoken Command Normalizer or validator
- [x] 9.3 Add a demo ablation showing a safety-sensitive action stopped by the Confirmation Gate
- [x] 9.4 Write README quickstart with bounded project positioning, setup, dependency notes, demo task instructions, and artifact privacy rules
- [x] 9.5 Add public wording that avoids benchmark, SOTA, production-ready, and general autonomous assistant claims
- [x] 9.6 Prepare a short demo video or GIF plan showing audio input, normalized request, browser action, confirmation/trace, and final status

## 10. Verification and Apply Readiness

- [x] 10.1 Run unit tests for schemas, normalizer validator, confirmation gate, ingestion, and trace writing
- [x] 10.2 Run integration smoke tests for controlled visual tasks with local browser execution
- [x] 10.3 Run the Demo Task Suite from reproducible audio fixtures and collect sanitized trace artifacts
- [x] 10.4 Verify no raw audio, private traces, secrets, remote host details, credentials, or live browser state are tracked in git
- [x] 10.5 Verify README and demo artifacts present the project as a bounded Voice-to-Browser Agent rather than a benchmark
