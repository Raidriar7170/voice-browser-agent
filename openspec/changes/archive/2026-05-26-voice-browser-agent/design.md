## Context

`voice-browser-agent` is a new application project presented publicly as Voice-to-Browser Agent. It fills the portfolio gap between agent reliability evaluation and a usable multimodal agent application by turning Chinese-first spoken commands into safe, traceable browser execution.

The project reuses `browser-use-vision` as the Visual Grounding Engine. The voice project owns ASR ingestion, spoken-command normalization, safety confirmation, operator-facing UI, trace output, and demo evidence. `browser-use-vision` remains a reusable package dependency and does not absorb voice features.

The intended runtime is hybrid: local browser execution and Operator Console on the Mac, with optional remote GPU services for heavy ASR or vision inference. Public artifacts must be sanitized; raw audio, private traces, credentials, remote host details, and live browser state must not be committed.

## Goals / Non-Goals

**Goals:**

- Build a bounded Chinese-first Voice-to-Browser Agent for single-utterance Spoken Command Execution.
- Convert ASR transcripts into structured Browser Task Requests or Clarification Requests.
- Validate normalized requests deterministically before browser execution.
- Execute bounded browser tasks through browser-use and `browser-use-vision`.
- Pause destructive, private, or irreversible actions through a Confirmation Gate.
- Produce Execution Trace artifacts that make each run auditable and reusable for future Speech-to-Task Adaptation.
- Provide an Operator Console and Demo Evidence Set suitable for README, demo video, and interview discussion.

**Non-Goals:**

- Build a general real-time voice assistant with continuous listening, interruption, or multi-speaker conversation.
- Build an ASR/TTS benchmark, TTS voice cloning system, or speech model research project.
- Build a benchmark leaderboard or claim SOTA performance.
- Support unrestricted web autonomy, login workflows, purchase completion, deletion, posting, or private-data submission without confirmation.
- Copy, fork, or merge `browser-use-vision` internals into the voice project.
- Build a multi-user production web platform, distributed workflow system, or full authentication layer.

## Decisions

### Separate application project over extending browser-use-vision

The Voice-to-Browser Agent will be a separate `voice-browser-agent` project that depends on `browser-use-vision`. This preserves the plugin boundary: `browser-use-vision` owns visual grounding, while the new project owns spoken-command execution and operator-facing evidence.

Alternatives considered:

- Add voice features directly to `browser-use-vision`: faster initially, but pollutes a visual grounding plugin with voice app concerns.
- Copy visual grounding code into the new project: simple locally, but loses reuse value and creates duplicated maintenance.

### Single-utterance command execution over real-time conversation

The MVP uses recorded or uploaded audio for one command at a time. Browser recording may be available in the Operator Console, but reproducible audio fixtures are the stable path for demo tasks.

Alternatives considered:

- Always-on real-time voice conversation: more impressive on the surface, but adds endpointing, interruption, streaming ASR/TTS, and session memory outside the MVP value.
- CLI-only audio input: simpler, but weaker for demonstrating an end-to-end multimodal agent application.

### Structured normalization over prompt rewriting

The Spoken Command Normalizer emits a Browser Task Request or Clarification Request. A Normalizer Validator checks schema, bounded intent type, safety signals, stop conditions, and missing fields before execution.

Alternatives considered:

- Pass raw transcripts directly to browser-use: too brittle for ASR noise and unsafe for ambiguous commands.
- Free-form prompt rewriting: easy to build but hard to test, audit, or use for safety gates.
- Fine-tuned normalizer from day one: premature before schema, traces, and correction examples exist.

### Bounded intents over unrestricted web autonomy

The MVP supports five Browser Intent Types: search/open, click visual target, fill form, select filter or option, and extract/compare visible information. The design explicitly rejects long-horizon autonomous browsing as an MVP goal.

Alternatives considered:

- Arbitrary browser goals: more general, but difficult to test, explain, or keep safe.
- Only controlled DOM tasks: stable, but would fail to justify visual grounding reuse.

### Direct package import plus optional remote model services

The application imports `VisionEnhancedAgent` from `browser-use-vision` directly. Heavy visual and ASR inference can be remote services, but the browser session and agent orchestration remain local for demo visibility and easier debugging.

Alternatives considered:

- Wrap `browser-use-vision` as a separate microservice: adds orchestration and trace-merging overhead without improving the MVP.
- Run the whole browser agent remotely: complicates demo visibility, browser state, and local interaction.

### Evidence-first demo over benchmark positioning

The project will provide a Demo Evidence Set: one clear demo, a quickstart, 8-12 reproducible demo tasks, sanitized traces, and a few demo ablations. These artifacts demonstrate the system without presenting it as a benchmark or leaderboard.

Alternatives considered:

- One polished recording only: too fragile and weak for a reliability-oriented portfolio.
- Full benchmark table: overlaps with existing projects and pulls the narrative away from an application.

## Risks / Trade-offs

- ASR noise causes unsafe or wrong normalization → The normalizer can return a Clarification Request, and the validator rejects missing, ambiguous, or dangerous requests.
- Browser tasks fail due to live website changes → The primary Demo Task Suite uses controlled pages, with only a few public non-destructive showcase tasks.
- The project looks like glue code → The Spoken Command Normalizer, Normalizer Validator, Confirmation Gate, and Execution Trace are first-class modules with visible artifacts.
- `browser-use-vision` API changes → Keep it as a versioned package/editable dependency and isolate integration behind a browser executor adapter.
- Public artifacts leak private data → Commit only Sanitized Demo Artifacts and ignore raw recordings, private traces, secrets, host details, and live browser state.
- Remote GPU services are unavailable → Provide fallback ASR and allow vision-heavy demos to document remote backend requirements instead of blocking all local development.
- Scope drifts toward real-time voice assistant → Keep MVP acceptance tied to single-utterance Spoken Command Execution and bounded Browser Intent Types.

## Migration Plan

This is a new project, so no production migration is required. Implementation should start from the OpenSpec tasks by scaffolding the project, wiring local dependencies, and adding tests around schemas, normalizer validation, confirmation behavior, and trace output before expanding demo tasks.

If the design proves too large, rollback is to keep `CONTEXT.md`, ADR-0001, and OpenSpec artifacts while narrowing implementation to audio upload, normalizer, confirmation gate, one browser executor path, and 3 controlled visual tasks.

## Open Questions

- Which exact SenseVoice/FunASR deployment shape will be used for the Primary ASR Adapter in the first working demo?
- Which 8-12 demo tasks should be included in the first Demo Task Suite?
- Which status TTS backend, if any, should be enabled by default for local demos?
