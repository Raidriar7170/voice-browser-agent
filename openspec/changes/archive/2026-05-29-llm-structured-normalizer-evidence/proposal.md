## Why

The project already demonstrates bounded spoken-command execution, visual grounding, public-readonly task evidence, and trace-derived adaptation data, but the main normalizer path still defaults to deterministic rules unless a test-only client is injected. This change turns the planned LLM structured-output normalizer into a configurable, safety-gated, evidence-backed capability so the next portfolio slice shows real AI intent parsing without weakening the validator, confirmation gate, or bounded execution contract.

## What Changes

- Add a configurable LLM structured-output normalizer path for transcript-to-`BrowserTaskRequest` or transcript-to-`ClarificationRequest` conversion.
- Keep the rule-based normalizer as the default offline fallback and baseline; no API key is required for tests or local deterministic demos.
- Require LLM outputs to pass schema parsing, deterministic validation, safety/confirmation checks, and route selection before any browser execution can begin.
- Record normalizer provenance, provider mode, fallback reason, schema/validation outcome, and prompt/version metadata in execution traces and reviewer evidence.
- Add an offline comparison workflow that evaluates rule, mock-LLM, and optionally real-provider normalizer outputs across committed fixture transcripts, reviewed variants, and normalizer-heavy seed examples.
- Surface normalizer source, fallback state, and validator decision in the Operator Console and generated evidence pack so reviewers can inspect why a command executed, clarified, or stopped.
- Preserve current non-goals: no model fine-tuning, no checkpoint publishing, no broad public-web autonomy, no validator bypass, no hidden account/session use, and no raw private prompts or credentials in public artifacts.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `spoken-command-normalization`: Add configurable LLM structured-output normalization, schema/fallback safety behavior, provenance recording, and comparison-oriented outputs.
- `operator-console`: Surface normalizer provider mode, fallback state, schema/validator outcome, and safe operator messaging.
- `demo-evidence-set`: Include local/private normalizer comparison evidence in the release handoff without model-quality, benchmark, or broad-autonomy claims.
- `trace-derived-training-examples`: Allow the existing sanitized seed-set workflow to feed local normalizer comparison evidence while preserving bounded adaptation positioning.

## Impact

- Affected backend code: runtime config, normalizer interfaces, provider adapters or clients, prompt assembly, schema parsing, fallback handling, trace metadata, validator integration, and tests.
- Affected API/UI: normalization and execution responses, Operator Console status panels, readiness/preflight output, and sanitized trace/export payloads.
- Affected evidence/docs: README runtime notes, demo evidence release-pack workflow, interview overview, public evidence page, and local comparison artifacts under ignored runtime paths.
- Optional provider dependencies may be added behind extras or lightweight adapters, but default test and demo paths must remain deterministic, offline, and keyless.
- Does not change browser execution semantics, route safety policy, public-readonly task contracts, ASR/TTS adapter contracts, or the `browser-use-vision` dependency boundary except for documentation references if needed.
