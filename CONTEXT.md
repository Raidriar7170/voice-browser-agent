# Voice-to-Browser Agent Context

This context defines the domain language for the standalone `voice-browser-agent` project, presented publicly as Voice-to-Browser Agent. The project exists to show an end-to-end multimodal agent application while reusing visual grounding from `browser-use-vision`.

## Language

**Voice-to-Browser Agent**:
A standalone command-based multimodal agent that converts spoken user intent into browser tasks, executes them with visual grounding, and returns traceable status feedback.
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

**Visual Verification Loop Evidence**:
Post-action controlled-task evidence that records whether the intended visual state was confirmed, failed, or remained uncertain, including expected condition, observed state summary, proof refs, and recovery or stop decision.
_Avoid_: action success only, raw screenshot proof, model-quality score, broad autonomy claim

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

**LLM Structured-Output Normalizer**:
An optional configured normalizer mode where an LLM provider proposes a `BrowserTaskRequest` or `ClarificationRequest`; schemas, deterministic validation, confirmation gates, and route policy still decide whether anything can execute.
_Avoid_: LLM executor, hidden safety bypass, broad autonomous planner

**Normalizer Provenance**:
Safe trace metadata describing provider mode, output source, prompt/schema version, output kind, schema status, validator decision, and fallback reason without recording credentials, request headers, raw prompts, or raw provider responses.
_Avoid_: raw provider log, secret-bearing prompt archive

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

**Public Task Contract**:
An explicit allowlisted public-readonly task definition containing task id, kind, target, allowed read-only actions, slots, completion criteria, limits, and private trace policy.
_Avoid_: domain-only allowlist, transcript-emitted arbitrary URL, broad public-web goal

**Public Task Completion Verifier**:
A deterministic verifier that decides whether a public-readonly task met task-specific proof before success is reported.
_Avoid_: page opened equals success, action count equals completion

**Public-Readonly Smoke Evidence**:
Local/private evidence from a small set of allowlisted documentation or reference tasks that records completed, partial, stopped, failed, or blocked outcomes without publishing raw page content.
_Avoid_: production automation, public benchmark, unrestricted browsing trace

**Public-Readonly Reliability Matrix**:
A reviewer-readable summary of the 5-task public-readonly smoke set showing task id, target class, completion criteria, observed proof summary, unmet criteria, outcome, stop/failure reason, privacy state, sanitizer status, and export state.
_Avoid_: production automation, unrestricted public-web autonomy, captcha bypass, account automation, benchmark ranking, model-quality claim, public raw-dataset evidence

**Public-Readonly Useful Task Pack**:
An 8-12 task contract set for stable read-only public documentation, reference, package metadata, release notes, and public repository search/read tasks, summarized as local/private evidence.
_Avoid_: arbitrary public-web autonomy, search-engine automation, account workflow, mutation workflow, captcha bypass, production automation, benchmark ranking, raw public artifact release

**Public-Readonly Task-Pack Runner**:
An opt-in local runner that attempts selected useful public-readonly task contracts or the full pack and writes a local/private manifest with honest completed, partial, stopped, failed, and blocked outcomes.
_Avoid_: arbitrary URL runner, crawler, public artifact publisher, production monitor, account workflow, mutation workflow

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

**Normalizer Comparison Evidence**:
A local/private report comparing rule, deterministic mock LLM, and optionally configured provider normalizer outputs over committed fixtures and reviewed seed examples.
_Avoid_: model score, training result, public leaderboard, broad autonomy evidence

## Coverage Matrix (2026-05-26)

This matrix is the current line-by-line coverage audit for the domain language above. "Covered" means the commitment is implemented, tested, documented, represented in OpenSpec specs, or evidenced by sanitized demo artifacts. "Deferred" means the current MVP intentionally stops short for a reason consistent with the bounded Voice-to-Browser Agent scope.

### Domain Terms

| Context lines | Term | Implementation | Tests | Docs / OpenSpec / Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| L7-L9 | Voice-to-Browser Agent | `voice_browser_agent.app`, `models.ExecutionTrace`, `executor.BrowserExecutorAdapter` | `test_executor_api_demo.py`, `test_core_schemas_trace.py` | README, `safe-browser-execution`, sanitized traces | Covered |
| L11-L13 | Bounded Voice-to-Browser Agent | bounded intent enum, validator long-horizon rejection, stop conditions | `test_normalizer_validator.py`, `test_confirmation_safety.py` | README, `spoken-command-normalization`, `safe-browser-execution` | Covered |
| L15-L17 | Reliable Voice-Driven Browser Execution | normalize -> validate -> confirm -> execute -> trace flow | `test_executor_api_demo.py`, `test_agentic_vision_executor.py` | demo task suite, trace fixtures | Covered |
| L19-L21 | Visual Grounding Engine | imports `browser-use-vision`, stores grounding refs, no copied internals | `test_executor_api_demo.py`, `test_agentic_vision_executor.py`, `test_real_vision_controlled_evidence.py` | README dependency note, `safe-browser-execution`, agentic traces, `real_vision_controlled` trace | Covered |
| 2026-05-29 | Visual Verification Loop Evidence | `VisualVerificationResult`, deterministic verifier, agentic recovery/stop control flow, release-pack summary | `test_agentic_vision_executor.py`, `test_demo_evidence_release_pack.py`, `test_operator_console_ui.py`, `test_demo_evidence.py` | `visual-verification-loop-evidence`, README, `fixtures/traces/agentic-sanitized/`, release-pack index | Covered as keyless controlled-task evidence; real VLM/provider verification is optional and local/private |
| L23-L25 | Remote Vision Backend | optional `VOICE_BROWSER_REMOTE_VISION_BACKEND_URL`, runtime passthrough | `test_executor_api_demo.py` | `.env.example`, `safe-browser-execution` | Covered as optional heavy inference |
| L27-L29 | Hybrid Local-GPU Runtime | local console/browser config plus optional ASR/vision URLs | `test_executor_api_demo.py`, `test_ingestion_asr.py` | README Runtime, `.env.example`, `safe-browser-execution` | Covered |
| L31-L33 | Voice Browser Stack | FastAPI, Pydantic, browser-use, `browser-use-vision`, minimal web console | `test_operator_console_ui.py`, API tests | `pyproject.toml`, README | Covered |
| L35-L37 | Spoken Command | one upload/recording/fixture input per execution | `test_ingestion_asr.py`, `test_executor_api_demo.py` | `spoken-command-ingestion`, fixture manifests | Covered |
| L39-L41 | Chinese-First Spoken Command | zh-first transcript metadata and mixed Chinese/English fixtures | `test_ingestion_asr.py`, `test_normalizer_validator.py` | audio fixtures, prompt examples | Covered |
| L43-L45 | Spoken Command Execution | one utterance creates one execution request and trace | `test_executor_api_demo.py` | README Quickstart, `spoken-command-ingestion` | Covered |
| L47-L49 | Spoken Command Normalizer | `RuleBasedNormalizer`, `StructuredOutputNormalizer` | `test_normalizer_validator.py` | `spoken-command-normalization`, prompts | Covered |
| 2026-05-29 | LLM Structured-Output Normalizer | configurable `normalizer_from_config`, mock and generic HTTP provider boundary, fallback policy | `test_normalizer_validator.py`, `test_executor_api_demo.py`, `test_real_voice_e2e_readiness.py` | `llm-structured-normalizer-evidence`, README, `.env.example` | Covered as optional intent parsing behind deterministic gates |
| 2026-05-29 | Normalizer Provenance | `NormalizerProvenance`, trace/export runtime metadata, console summary cards | `test_executor_api_demo.py`, `test_operator_console_ui.py` | release-pack summary, Operator Console, docs/public-evidence | Covered without raw provider data |
| L51-L53 | Normalizer Validator | deterministic `NormalizerValidator` | `test_normalizer_validator.py` | `spoken-command-normalization` | Covered |
| L55-L57 | Browser Task Request | Pydantic `BrowserTaskRequest` schema | `test_core_schemas_trace.py`, `test_normalizer_validator.py` | `spoken-command-normalization`, trace fixtures | Covered |
| L59-L61 | Clarification Request | Pydantic `ClarificationRequest`, no execution path | `test_normalizer_validator.py`, `test_executor_api_demo.py` | sanitized `demo-ambiguous.json` | Covered |
| L63-L65 | Browser Intent Type | enum restricts five MVP intent types | `test_core_schemas_trace.py`, `test_normalizer_validator.py` | demo task suite, `spoken-command-normalization` | Covered |
| L67-L69 | Operator Console | local FastAPI static UI/API plus public-readonly visible result panel and normalizer provenance display | `test_operator_console_ui.py`, `test_executor_api_demo.py` | `operator-console`, README | Covered |
| L71-L73 | Demo Task Suite | eight fixture-backed demo tasks | `test_demo_evidence.py` | `docs/demo/demo-task-suite.md` | Covered |
| L75-L77 | Visual-Grounding-Heavy Task | icon, color swatch, SVG, dashboard tasks | `test_demo_evidence.py`, `test_agentic_vision_executor.py` | demo pages, live/agentic traces | Covered |
| L79-L81 | Demo Ablation | module-value ablation docs without rankings | `test_demo_evidence.py` | `docs/demo/ablations.md`, `demo-evidence-set` | Covered |
| L83-L85 | Demo Evidence Set | quickstart, video plan, suite, preview/live/agentic/real-vision traces | `test_demo_evidence.py`, `test_demo_evidence_release_pack.py`, `test_real_vision_controlled_evidence.py` | README, `docs/demo/*`, `docs/public-evidence/index.html`, trace fixtures | Covered |
| L87-L89 | Sanitized Demo Artifact | sanitizer, ignored raw artifacts, public trace scans, real-vision metadata-only export | `test_demo_evidence.py`, `test_core_schemas_trace.py`, `test_real_vision_controlled_evidence.py` | `.gitignore`, sanitized trace directories, `fixtures/traces/real-vision-sanitized/` | Covered |
| 2026-05-28 | Public Task Contract | `PublicTaskContract`, GitHub search/read contracts, parser, route selection, executor contract guard | `test_public_readonly_contract.py`, `test_operator_task_routing.py`, `test_public_readonly_api_ui_evidence.py` | `public-readonly-web-execution`, `fixtures/public-readonly-smoke.json`, README | Covered |
| 2026-05-28 | Public Task Completion Verifier | `PublicTaskCompletionVerifier` records docs and GitHub-specific proof, unmet criteria, and outcome state | `test_public_readonly_contract.py` | `safe-browser-execution`, `docs/demo/demo-task-suite.md`, public evidence page | Covered |
| 2026-05-28 | Public-Readonly Smoke Evidence | smoke fixture defines OpenAI Docs, Python Docs, GitHub repository search/read, and MDN bounded tasks with private artifact status | `test_public_readonly_api_ui_evidence.py` | `fixtures/public-readonly-smoke.json`, `docs/demo/useful-scenarios.md`, `docs/demo/video-plan.md` | Covered as local/private until sanitized |
| 2026-05-28 | Public-Readonly Useful Task Pack | useful pack fixture defines documentation, reference, package metadata, release notes, and public repository search/read contracts with local/private summaries | `test_public_readonly_contract.py`, `test_public_readonly_task_pack_runner.py`, `test_demo_evidence_release_pack.py` | `fixtures/public-readonly-useful-task-pack.json`, release-pack manifest, docs/demo | Covered as local/private summary evidence |
| 2026-05-29 | Public-Readonly Task-Pack Runner | selected/full useful-pack runner writes versioned local/private manifests with deterministic and opt-in live modes | `test_public_readonly_task_pack_runner.py`, `test_public_readonly_api_ui_evidence.py`, `test_demo_evidence_release_pack.py` | `scripts/run_public_readonly_task_pack.py`, runtime manifest path, release-pack summary, Operator Console readiness | Covered as local/private until sanitized |
| 2026-05-28 | Public-Readonly Visible Result Artifact | local/private screenshot metadata and guarded artifact serving for real public runs | `test_public_readonly_contract.py`, `test_public_readonly_api_ui_evidence.py`, `test_operator_console_ui.py` | README, `operator-console`, `safe-browser-execution` | Covered |
| 2026-05-27 | Real Voice E2E Smoke | uploaded or recorded audio can be reviewed and executed against a controlled local visual task | `test_real_voice_e2e_readiness.py`, `test_operator_console_ui.py` | `fixtures/traces/real-voice-sanitized/`, `scripts/generate_real_voice_trace.py`, `spoken-command-ingestion` | Covered |
| 2026-05-27 | Local Real-Use Preflight | readiness report for primary ASR, fallback ASR, browser automation, visual grounding, visual verifier state, and privacy | `test_real_voice_e2e_readiness.py`, `test_operator_console_ui.py` | `scripts/preflight_real_use.py`, `/api/readiness`, README | Covered |
| 2026-05-27 | ASR Transcript Review | original ASR output and reviewed transcript are recorded before normalization/execution | `test_real_voice_e2e_readiness.py`, `test_operator_console_ui.py` | Operator Console, `fixtures/traces/real-voice-sanitized/`, `operator-console` | Covered |
| 2026-05-27 | Useful Local Scenario Pack | CRM/settings/dashboard pages and metadata show practical controlled local workflows | `test_demo_evidence.py` | `docs/demo/useful-scenarios.md`, `fixtures/useful-scenarios.json`, `demo/pages/*` | Covered |
| 2026-05-27 | Real-Use Failure Traces | ASR unavailable, clarification, confirmation, cancellation, and ambiguous-target traces are committed as reliability evidence | `test_demo_evidence.py`, `test_demo_evidence_release_pack.py` | `fixtures/traces/real-use-sanitized/`, `docs/public-evidence/index.html` | Covered |
| L91-L93 | Reproducible Audio Fixture | sanitized fixture manifests, no raw audio | `test_demo_evidence.py`, `test_ingestion_asr.py` | `fixtures/audio/*.fixture.json`, fixture README | Covered |
| L95-L97 | ASR Adapter | ASR protocol, remote primary, fallback, fixture adapter | `test_ingestion_asr.py`, API tests | `spoken-command-ingestion`, `.env.example` | Covered |
| L99-L101 | Primary ASR Adapter | configurable remote primary ASR adapter for zh-first commands | `test_executor_api_demo.py`, `test_ingestion_asr.py` | `.env.example`, README Runtime | Covered as optional configured service |
| L103-L105 | Fallback ASR Adapter | faster-whisper fallback adapter with `language="zh"` | `test_ingestion_asr.py` | `spoken-command-ingestion`, `pyproject.toml[asr]` | Covered |
| L107-L109 | TTS Adapter | `StatusVoiceFeedback` payload plus browser-native optional playback | `test_operator_console_ui.py` | `operator-console` closeout spec, README Runtime | Covered as optional status playback, not model TTS |
| L111-L113 | Status Voice Feedback | gated console playback when enabled, textual fallback otherwise | `test_operator_console_ui.py` | `operator-console`, `/api/status-voice` | Covered |
| L115-L117 | Speech-to-Task Adaptation | trace-derived example helper and seed-set builder support later adaptation inputs | `test_trace_derived_training_examples.py`, `test_speech_to_task_dataset_builder.py` | README Runtime, `trace-derived-training-examples`, `fixtures/seed-set/reviewed-variants.json` | Covered for seed-set preparation; model adaptation deferred |
| L119-L121 | Confirmation Gate | `ConfirmationGate` pending/confirm/cancel/block states | `test_confirmation_safety.py`, API tests | `safe-browser-execution`, `demo-checkout-stop.json` | Covered |
| L123-L125 | Execution Trace | Pydantic trace plus writer/export sanitizer | `test_core_schemas_trace.py`, API tests | sanitized preview/live/agentic trace fixtures | Covered |
| L127-L129 | Trace-Derived Training Example | `training_example_from_trace` with optional human correction and reviewed variants | `test_trace_derived_training_examples.py`, `test_speech_to_task_dataset_builder.py` | `trace-derived-training-examples`, README Runtime, seed-set docs | Covered; no public raw dataset/checkpoints |
| 2026-05-29 | Normalizer Comparison Evidence | `scripts/build_normalizer_comparison.py` creates local/private manifest from fixtures and seed examples | `test_normalizer_comparison.py`, `test_demo_evidence_release_pack.py` | `demo-evidence-set`, `trace-derived-training-examples`, release-pack index | Covered as local structured-output evidence; model training deferred |

### Example-Dialogue Commitments

| Context lines | Commitment | Implementation | Tests | Docs / OpenSpec / Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| L205-L207 | Voice layer is outside `browser-use-vision`; it consumes visual grounding as a dependency | package dependency plus real SoM invocation for controlled evidence | `test_executor_api_demo.py`, `test_real_vision_controlled_evidence.py` | README, `safe-browser-execution`, `fixtures/traces/real-vision-sanitized/` | Covered |
| L209-L211 | Do not copy or fork visual grounding internals | no copied visual code, adapter boundary only, calls `browser_use_vision.som.annotate_screenshot` | dependency/import tests, `test_real_vision_controlled_evidence.py` | README dependency note, public evidence page | Covered |
| L213-L215 | Do not wrap `browser-use-vision` as a separate service; only remote heavy inference may be service-hosted | direct import plus optional backend URL | `test_executor_api_demo.py` | `.env.example`, `safe-browser-execution` | Covered |
| L217-L219 | Browser execution and console remain local; remote GPU only for heavy inference | `local_browser=True`, file/local controlled demos | API/live tests | README Runtime, live sanitized traces | Covered |
| L221-L223 | MVP avoids large orchestration frameworks | FastAPI/Pydantic/local adapters only | project dependency checks via tests | `pyproject.toml`, design non-goals | Covered |
| L225-L227 | Main value is reliable browser execution, not ASR/TTS quality | ASR/TTS are adapters and optional feedback | ingestion/API tests | README scope, OpenSpec designs | Covered |
| L229-L231 | Public materials must not call it a general autonomous voice agent | README/test guards avoid autonomy claims | `test_demo_evidence.py` | README, demo docs | Covered |
| L233-L235 | No continuous listening; one utterance becomes one browser task attempt | upload/recording endpoint stores one clip per execution | `test_ingestion_asr.py`, API tests | `spoken-command-ingestion` | Covered |
| L237-L239 | Original contribution is the Spoken Command Normalizer | normalizer plus validator and trace evidence | `test_normalizer_validator.py` | `spoken-command-normalization` | Covered |
| L241-L243 | First normalizer is structured output plus deterministic validator, not fine-tuned model | `StructuredOutputNormalizer` with rule fallback and validator | `test_normalizer_validator.py` | prompts, OpenSpec specs | Covered; fine-tuning deferred |
| L245-L247 | Unclear speech becomes Clarification Request instead of execution | ambiguous normalizer branch and execution guard | `test_normalizer_validator.py`, API tests | `demo-ambiguous.json` | Covered |
| L249-L251 | Arbitrary browser goals are rejected; intents are bounded | enum and long-horizon validator rejection | `test_normalizer_validator.py` | `spoken-command-normalization` | Covered |
| L253-L255 | MVP is not CLI-only; reviewers use Operator Console | static web console and API | `test_operator_console_ui.py` | `operator-console`, README | Covered |
| L257-L259 | Primary demo is controlled first, with only public non-destructive showcase tasks | controlled pages plus public fixtures | `test_demo_evidence.py` | demo suite docs | Covered |
| L261-L263 | At least half of demo tasks are visual-grounding-heavy | 4 of 8 tasks marked visual-heavy | `test_demo_evidence.py` | demo suite, trace dirs | Covered |
| L265-L267 | README avoids benchmark table; ablations explain module value | README wording guard and ablation docs | `test_demo_evidence.py` | `docs/demo/ablations.md` | Covered |
| L269-L271 | One polished demo is insufficient; provide full evidence set | eight traces, quickstart, video plan | `test_demo_evidence.py` | README, docs/demo, fixtures/traces | Covered |
| L273-L275 | Raw traces and recordings must not be public artifacts | `.gitignore`, sanitized export, privacy tests | `test_demo_evidence.py`, `test_core_schemas_trace.py` | sanitized trace fixtures | Covered |
| L277-L279 | Stable demo path uses reproducible fixtures, not live microphone requirement | fixture replay endpoint and manifests | `test_executor_api_demo.py`, `test_demo_evidence.py` | fixture README | Covered |
| L281-L283 | First milestone is reliable Spoken Command Execution; ASR/TTS are replaceable adapters | ASR protocol/fallback, optional status feedback | ingestion/API/UI tests | README Runtime | Covered |
| L285-L287 | TTS is optional Status Voice Feedback, not model contribution | status payload plus gated browser playback | `test_operator_console_ui.py` | `operator-console` | Covered |
| L289-L291 | No streaming ASR; primary consumes one clip and fallback handles unavailability | upload ingestor and ASR orchestrator | `test_ingestion_asr.py` | `spoken-command-ingestion` | Covered |
| L293-L295 | Chinese-first, not universal multilingual | zh-first metadata and fixtures with English code-switching | `test_ingestion_asr.py`, normalizer tests | prompts, fixtures | Covered |
| L297-L299 | Later model fine-tuning belongs to Speech-to-Task Adaptation | trace-derived example helper creates adaptation inputs only | `test_trace_derived_training_examples.py` | README Runtime, closeout spec | Covered for later-data support; training deferred |
| L301-L303 | Checkout/deletion/private/irreversible actions pause at Confirmation Gate | safety flags, confirmation gate, browser-state stops | `test_confirmation_safety.py`, API tests | `demo-checkout-stop.json` | Covered |
| L305-L307 | Final status alone is insufficient; each execution has transcript, normalized request, safety, grounding, actions, and status trace | `ExecutionTrace`, trace writer, agentic steps | `test_core_schemas_trace.py`, API tests | trace fixtures | Covered |
| L309-L311 | Execution Traces can become Trace-Derived Training Examples with optional human correction | `training_example_from_trace` | `test_trace_derived_training_examples.py` | `trace-derived-training-examples` | Covered; no public raw dataset |

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
