## Context

The repository already contains the bounded Voice-to-Browser Agent scaffold, archived OpenSpec changes, passing tests, sanitized fixture traces, and docs. The remaining gap is not a new product direction; it is contract closure. `CONTEXT.md` defines the project language, but it does not yet prove coverage for every term and example-dialogue commitment. Several main specs also still contain placeholder purpose text from earlier archives.

Two commitments deserve small implementation closure rather than prose-only coverage: Execution Traces should be usable as Trace-Derived Training Examples for later Speech-to-Task Adaptation, and optional Status Voice Feedback should be visibly gated in the Operator Console. Both must stay bounded, local-first, sanitized, and non-benchmark-oriented.

## Goals / Non-Goals

**Goals:**

- Add a durable coverage matrix to `CONTEXT.md` with line references, implementation, tests, docs, OpenSpec specs, demo evidence, and status for every domain term and example-dialogue commitment.
- Replace placeholder main spec purposes with concrete summaries.
- Add a small trace-derived training example helper/model that uses sanitized trace content and optional human correction.
- Make optional Status Voice Feedback explicit in the console and covered by tests.
- Preserve sanitized public artifacts and `browser-use-vision` as a dependency-only Visual Grounding Engine.

**Non-Goals:**

- Fine-tune a model, build an ASR/TTS benchmark, or generate a public training dataset.
- Add streaming ASR, continuous listening, voice cloning, multi-user sessions, auth, database persistence, or a large workflow framework.
- Run browsers remotely, copy `browser-use-vision` internals, or publish raw audio/screenshots/private live browser state.
- Claim benchmark, SOTA, production automation, or unrestricted autonomous-agent performance.

## Decisions

### Keep the coverage matrix in `CONTEXT.md`

The matrix belongs next to the domain language because `CONTEXT.md` is the durable contract the user asked to complete. It should be compact but line-referenced, and every deferred row must explain why the deferral is consistent with the MVP boundary.

Alternatives considered:

- Put the audit in a separate report: easier to keep short, but weakens `CONTEXT.md` as the source of truth.
- Only update README/OpenSpec: useful for users, but does not satisfy the contract-level completion definition.

### Add a trace-derived example helper, not a training pipeline

Implement a narrow model/helper that converts an `ExecutionTrace` into a sanitized Speech-to-Task example with transcript text, normalized output or clarification, validator/final status context, and optional human correction. This proves the trace contract without introducing training jobs, datasets, checkpoints, or benchmark claims.

Alternatives considered:

- Defer trace-derived examples entirely: lower implementation risk, but leaves a concrete `CONTEXT.md` term weakly covered.
- Build a dataset writer or fine-tuning pipeline: out of scope for the bounded MVP and risks pulling the project into model-training claims.

### Use browser-native optional status speech

The backend already returns a status voice feedback payload. The console should speak it only when enabled and when browser speech synthesis is available. This keeps TTS optional and demo-local while avoiding raw audio artifacts or voice-cloning scope.

Alternatives considered:

- Generate audio files server-side: more "TTS-like", but creates raw media artifacts and model/dependency overhead.
- Leave only the backend text payload: too weak for the "spoken playback" part of the optional feedback term.

### Update spec purpose text directly during archive sync

Purpose placeholders are archive drift, not a behavior change. This change still records relevant normative behavior in delta specs, then updates main spec purpose text while archiving to keep OpenSpec artifacts readable.

## Risks / Trade-offs

- Coverage matrix can become stale -> Keep it line-referenced and tied to concrete files/tests so future updates have obvious edit points.
- Trace-derived example export may expose private nested fields -> Use the existing sanitizer and test with private nested fields.
- Browser speech synthesis is unavailable in some environments -> Gate playback on `status_voice.enabled` and `window.speechSynthesis`; absence is a silent no-op.
- Spec purpose edits are easy to miss during archive -> Include them in tasks and final verification with a placeholder scan.

## Migration Plan

This is additive. Existing traces, endpoints, fixtures, and docs remain valid. If the trace-derived helper causes issues, it can be removed without changing public APIs. If status voice playback is problematic, disabling `VOICE_BROWSER_ENABLE_STATUS_VOICE_FEEDBACK` preserves current behavior.

## Open Questions

None. The goal explicitly requires end-to-end closure, and this change stays within the existing bounded MVP.
