# Voice-to-Browser Agent Context

This context defines the domain language for the `voice-browser-agent` project, presented publicly as Voice-to-Browser Agent. The project exists to show an end-to-end multimodal agent application while reusing visual grounding from `browser-use-vision`.

## Language

**Voice-to-Browser Agent**:
A command-based multimodal agent that converts spoken user intent into browser tasks, executes them with visual grounding, and returns traceable status feedback.
_Avoid_: real-time voice assistant, general voice agent, ASR/TTS benchmark, browser-use-vision voice extension

**Bounded Voice-to-Browser Agent**:
A voice-driven browser agent with explicit task categories, safety stops, and traceable execution rather than unrestricted web autonomy.
_Avoid_: general autonomous voice agent, production web automation, real-time multimodal assistant

**Reliable Voice-Driven Browser Execution**:
The core project promise: spoken intent is converted into a browser task and executed with visible grounding, recoverable failures, safety confirmations, and traceable status feedback.
_Avoid_: voice interaction demo, speech model benchmark, generic assistant

**Visual Grounding Engine**:
The reusable browser UI perception component that turns screenshots, OCR, regions, and Set-of-Mark annotations into page context for the browser executor.
_Avoid_: voice agent core, benchmark harness

**Remote Vision Backend**:
The GPU-backed visual model service used by the Visual Grounding Engine for OCR, region captioning, detection, or description.
_Avoid_: voice backend, browser executor service

**Hybrid Local-GPU Runtime**:
A runtime split where the Operator Console and browser execution run locally, while heavy ASR or vision inference can run on a remote GPU service.
_Avoid_: remote-only browser agent, local-only heavy inference

**Voice Browser Stack**:
The MVP technology family: Python/FastAPI backend, Pydantic schemas, browser-use execution, browser-use-vision visual grounding, and a minimal web Operator Console.
_Avoid_: distributed workflow platform, full multi-user web app, unrelated agent framework

**Spoken Command**:
A short user utterance that expresses a browser task in natural language, possibly with speech noise, omissions, or references to visible UI elements.
_Avoid_: benchmark task, transcript only

**Chinese-First Spoken Command**:
A spoken browser command expressed primarily in Chinese, with expected English code-switching for product names, URLs, UI labels, and technical terms.
_Avoid_: universal multilingual command, English-only command

**Spoken Command Execution**:
The MVP interaction model where one recorded or uploaded utterance is interpreted as one browser task execution request.
_Avoid_: real-time voice conversation, always-on listening, multi-speaker voice session

**Spoken Command Normalizer**:
The intent adaptation layer that converts noisy ASR text into a structured, safety-aware browser task request.
_Avoid_: prompt rewrite, transcript cleanup, chat assistant

**Normalizer Validator**:
A deterministic check that accepts, rejects, or flags a normalized command before browser execution.
_Avoid_: second LLM judge, hidden prompt rule

**Browser Task Request**:
A structured request for browser execution containing the intended task, intent type, execution constraints, visible UI references, confirmation requirements, and stop conditions.
_Avoid_: raw transcript, benchmark prompt, free-form chat message

**Clarification Request**:
A pause state produced when a Spoken Command cannot be safely normalized into one Browser Task Request.
_Avoid_: execution failure, generic error

**Browser Intent Type**:
One of the bounded task categories supported by the MVP: search and open, click visual target, fill form, select filter or option, or extract/compare visible information.
_Avoid_: unrestricted web autonomy, long-horizon browsing goal

**Operator Console**:
A minimal web interface that exposes the spoken command, ASR transcript, normalized Browser Task Request, execution trace, screenshots, and final browser state for demonstration and debugging.
_Avoid_: consumer voice assistant app, chat UI, CLI-only demo

**Demo Task Suite**:
A small set of controlled demo tasks plus a few public non-destructive website tasks used to demonstrate the Voice-to-Browser Agent.
_Avoid_: benchmark, leaderboard, standard evaluation suite

**Visual-Grounding-Heavy Task**:
A demo task whose correct execution depends on visual UI evidence such as icon-only controls, color swatches, canvas/SVG content, image-like cards, or spatial references.
_Avoid_: text-only search task, normal DOM button task

**Demo Ablation**:
A small demonstration that removes one module to show why the MVP needs it.
_Avoid_: benchmark result, leaderboard comparison, SOTA claim

**Demo Evidence Set**:
The MVP completion evidence: one clear demo video, a quickstart, a small reproducible Demo Task Suite, and trace artifacts for each task.
_Avoid_: one-off successful recording, benchmark leaderboard

**Sanitized Demo Artifact**:
A public artifact stripped of credentials, private URLs, personal data, and live browser state.
_Avoid_: raw user recording, real website trace dump, secret-bearing screenshot

**Reproducible Audio Fixture**:
A saved audio sample paired with an expected spoken command and demo task.
_Avoid_: live-only microphone input, non-repeatable demo speech

**ASR Adapter**:
The replaceable component that converts one Spoken Command into a transcript.
_Avoid_: ASR benchmark module, speech model research core

**Primary ASR Adapter**:
The default ASR Adapter for the MVP, expected to favor Chinese spoken browser commands.
_Avoid_: streaming ASR core, ASR research target

**Fallback ASR Adapter**:
A secondary ASR Adapter used when the primary ASR implementation is unavailable or too heavy for the local environment.
_Avoid_: second benchmark baseline

**TTS Adapter**:
The replaceable component that turns execution feedback into optional spoken output.
_Avoid_: voice cloning core, TTS benchmark module

**Status Voice Feedback**:
Optional spoken playback of execution status, confirmation prompts, and final results.
_Avoid_: TTS model project, voice cloning feature

**Speech-to-Task Adaptation**:
The model adaptation layer that maps noisy spoken browser commands into structured Browser Task Requests.
_Avoid_: ASR fine-tuning, TTS fine-tuning, transcript polishing

**Confirmation Gate**:
A safety boundary that pauses or blocks execution when a Browser Task Request or browser state indicates a destructive, private, or irreversible action.
_Avoid_: optional warning, post-hoc safety note

**Execution Trace**:
The ordered evidence record of how one Spoken Command Execution was interpreted, checked, grounded, executed, and completed or stopped.
_Avoid_: final status only, benchmark report

**Trace-Derived Training Example**:
A Speech-to-Task training example created from an Execution Trace and optional human correction.
_Avoid_: raw private trace dump, ASR benchmark sample

## Example Dialogue

Developer: "Should the voice layer live inside browser-use-vision?"

Domain expert: "No. browser-use-vision remains the Visual Grounding Engine. The new Voice-to-Browser Agent consumes it as a dependency and owns the spoken command flow."

Developer: "Should the Voice-to-Browser Agent copy the visual grounding code?"

Domain expert: "No. It depends on the Visual Grounding Engine as a reusable component and does not own or fork visual grounding internals."

Developer: "Should browser-use-vision be wrapped as a separate service?"

Domain expert: "No. The Voice-to-Browser Agent imports the Visual Grounding Engine directly. Only the Remote Vision Backend is service-hosted when GPU inference is needed."

Developer: "Should the whole browser agent run on the GPU machine?"

Domain expert: "No. The project uses a Hybrid Local-GPU Runtime: local browser execution and console, with remote GPU services only for heavy inference."

Developer: "Should the MVP introduce a large orchestration framework?"

Domain expert: "No. The MVP uses the Voice Browser Stack: Python/FastAPI, Pydantic, browser-use, browser-use-vision, and a minimal Operator Console."

Developer: "Is the main value ASR/TTS quality?"

Domain expert: "No. ASR and TTS are the input and feedback surfaces. The main value is Reliable Voice-Driven Browser Execution."

Developer: "Can public materials call this a general autonomous voice agent?"

Domain expert: "No. It is a Bounded Voice-to-Browser Agent with explicit intent types, safety stops, and traceable execution."

Developer: "Should the MVP support continuous listening and interruption?"

Domain expert: "No. The MVP is Spoken Command Execution: one utterance produces one browser task attempt with traceable feedback."

Developer: "What is the original contribution beyond wiring ASR to browser-use?"

Domain expert: "The Spoken Command Normalizer. It turns noisy spoken intent into a Browser Task Request that the visual browser agent can execute and audit."

Developer: "Should the first normalizer be a fine-tuned model?"

Domain expert: "No. The first normalizer uses structured output plus a Normalizer Validator. Fine-tuning belongs to later Speech-to-Task Adaptation."

Developer: "Should unclear speech always become a browser task?"

Domain expert: "No. Unclear, ambiguous, or unsafe speech becomes a Clarification Request instead of being executed."

Developer: "Can the MVP accept arbitrary browser goals?"

Domain expert: "No. Each Browser Task Request belongs to a bounded Browser Intent Type so the agent remains demonstrable and auditable."

Developer: "Should the MVP be a CLI?"

Domain expert: "No. The MVP uses an Operator Console so reviewers can see the transcript, normalized request, trace, and browser state in one place."

Developer: "Should the primary demo depend on live websites?"

Domain expert: "No. The Demo Task Suite is controlled first, with only a few public non-destructive website tasks for showcase."

Developer: "Can most demo tasks be text-only browser actions?"

Domain expert: "No. At least half of the Demo Task Suite should be Visual-Grounding-Heavy Tasks so reuse of the Visual Grounding Engine is meaningful."

Developer: "Should README include a full benchmark table?"

Domain expert: "No. It may include a few Demo Ablations that explain why the normalizer, visual grounding, and confirmation gate matter."

Developer: "Is one polished demo enough?"

Domain expert: "No. The MVP needs a Demo Evidence Set: a clear demo, quickstart, reproducible demo tasks, and trace artifacts."

Developer: "Can raw traces and recordings be committed publicly?"

Domain expert: "No. Public materials must be Sanitized Demo Artifacts; raw audio, real website traces, credentials, and live browser state stay local or ignored."

Developer: "Does every demo task need live microphone input?"

Domain expert: "No. Each reproducible task can use a Reproducible Audio Fixture. Browser recording is a presentation enhancement, not the stable test path."

Developer: "Is ASR/TTS model quality the first milestone?"

Domain expert: "No. ASR and TTS are replaceable adapters in the MVP. The first milestone is reliable Spoken Command Execution."

Developer: "Should TTS be a core model contribution?"

Domain expert: "No. TTS is Status Voice Feedback: optional spoken playback for status, confirmations, and final results."

Developer: "Does the MVP need streaming ASR?"

Domain expert: "No. The Primary ASR Adapter consumes one audio clip per Spoken Command. A Fallback ASR Adapter can be used when the primary implementation is unavailable."

Developer: "Does the MVP promise universal multilingual support?"

Domain expert: "No. It is Chinese-first, with English code-switching for product names, URLs, UI labels, and technical terms."

Developer: "Where should model fine-tuning live later?"

Domain expert: "In Speech-to-Task Adaptation: adapting noisy spoken browser commands into structured Browser Task Requests."

Developer: "Can the agent execute checkout or deletion directly if the spoken command asks for it?"

Domain expert: "No. A Confirmation Gate pauses destructive, private, or irreversible actions before execution continues."

Developer: "Is a final success message enough?"

Domain expert: "No. Each Spoken Command Execution produces an Execution Trace showing transcript, normalized request, safety decision, grounding, browser actions, and final status."

Developer: "Can traces support the later fine-tuning phase?"

Domain expert: "Yes. Execution Traces can become Trace-Derived Training Examples when paired with optional human correction."
