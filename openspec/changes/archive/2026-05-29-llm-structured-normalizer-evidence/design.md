## Context

The current normalizer layer already exposes `StructuredOutputNormalizer`, but application state constructs it without an LLM client, so production and demo flows fall back to `RuleBasedNormalizer`. Existing specs and `CONTEXT.md` describe the normalizer as the original contribution, with deterministic validation, confirmation gates, route selection, sanitized traces, and Speech-to-Task adaptation data already in place.

This change should make the LLM path real and reviewable without making execution authority probabilistic. The LLM is an intent parser that proposes a structured output; Pydantic schemas, `NormalizerValidator`, `ConfirmationGate`, route selection, and execution policies remain the hard gates.

## Goals / Non-Goals

**Goals:**

- Add a provider-neutral LLM normalizer interface that can be configured at runtime and tested offline with a deterministic mock client.
- Parse LLM output into the existing `BrowserTaskRequest` or `ClarificationRequest` schemas, with explicit malformed-output and unsafe-output handling.
- Preserve rule-based normalization as the default keyless path, fallback path, and comparison baseline.
- Record normalizer provenance in traces and evidence: selected provider mode, prompt/schema version, output kind, fallback reason, validation outcome, and whether execution used rule, mock LLM, real provider, or fallback.
- Build local/private normalizer comparison evidence from committed fixture transcripts and reviewed Speech-to-Task variants.
- Surface normalizer source and validation/fallback state in the Operator Console and release-pack handoff.

**Non-Goals:**

- No model fine-tuning, checkpoint export, or remote GPU training job.
- No replacement of `NormalizerValidator`, `ConfirmationGate`, route policy, or public-readonly task contracts.
- No broad public-web autonomy, arbitrary URL execution, login/session reuse, account mutation, or captcha/barrier bypass.
- No public release of raw prompts that contain secrets, raw API responses, private transcripts, or provider credentials.
- No requirement that a real provider API key exists for tests, demos, or CI.

## Decisions

### Decision: Treat the LLM as a candidate generator, not an executor

The LLM normalizer returns a candidate JSON payload that must validate as `BrowserTaskRequest` or `ClarificationRequest`. If parsing fails, the system either falls back to rules or emits a clarification according to configuration. If parsing succeeds but deterministic validation rejects the request, execution remains blocked or clarified exactly as with rule-based output.

Alternatives considered:
- Let the LLM directly choose route/execution behavior. Rejected because it would bypass the existing reliability and safety contract.
- Replace rules entirely. Rejected because rule output is valuable as an offline baseline and robust fallback.

### Decision: Add provider-neutral client boundaries with deterministic offline modes

The implementation should separate the normalizer from concrete provider SDKs. Runtime config should select a provider mode such as `rule`, `mock_llm`, or a real provider adapter. The deterministic mock client should exercise the same schema/fallback path as a real provider and keep tests keyless.

Alternatives considered:
- Hardwire one provider into `StructuredOutputNormalizer`. Rejected because it makes local tests and future provider swaps brittle.
- Only document LLM usage without code. Rejected because the next portfolio slice needs inspectable evidence, not a claim.

### Decision: Version prompt/schema contracts and avoid secret-bearing artifacts

The prompt contract should live in source-controlled prompt templates or metadata that do not include secrets. Traces should record stable prompt/schema version ids, provider mode, and fallback outcome, but not raw provider credentials, private request headers, or unsanitized raw provider responses.

Alternatives considered:
- Store full raw prompt and response in public traces. Rejected because provider output can contain sensitive text and bloats public evidence.
- Store no provenance. Rejected because reviewers need to inspect whether a result came from rules, mock LLM, real provider, or fallback.

### Decision: Use local comparison evidence before fine-tuning

The comparison workflow should run rule and LLM-style normalizers over fixture transcripts and reviewed seed examples, then write a local/private report with agreement, schema validity, validator outcome, unsupported-command behavior, and route-readiness fields. This report is evidence of system behavior, not a benchmark leaderboard or model-quality claim.

Alternatives considered:
- Start with fine-tuning. Rejected because the project needs a clear LLM baseline and task contract before training can be meaningful.
- Compare only on successful demo tasks. Rejected because ambiguous, unsafe, malformed, and unsupported commands are the reliability signal.

## Risks / Trade-offs

- Provider drift or flaky live API output -> Keep real-provider evidence optional; use deterministic mock tests for required validation; record provider/model metadata when live evidence is generated.
- LLM emits unsafe but well-formed requests -> Keep deterministic validator, confirmation gate, route selection, and public-readonly contract checks as hard blockers.
- Fallback hides LLM failures -> Record fallback reason and selected output source in trace/evidence so failures remain visible.
- Evidence sounds like a benchmark claim -> Keep docs phrased as local/private comparison evidence, avoid scores or SOTA claims, and report safety/clarification behavior alongside successes.
- Added provider dependencies complicate setup -> Gate real providers behind config and optional extras where practical; default install remains keyless and deterministic.

## Migration Plan

1. Introduce config fields and normalizer metadata without changing default behavior; default provider remains rule-based.
2. Add deterministic mock LLM path and regression tests for schema parsing, fallback, validator integration, and trace provenance.
3. Add optional real-provider adapter and readiness reporting behind explicit environment configuration.
4. Add comparison workflow and local/private evidence outputs under ignored runtime paths.
5. Update console, release-pack, docs, and public evidence summaries to display normalizer provenance without exposing raw private provider data.

Rollback is straightforward: set provider mode to `rule` or remove provider credentials; existing rule-based normalization and all execution gates remain intact.

## Open Questions

- Which real provider adapter should be implemented first: OpenAI-compatible, Anthropic, or a generic HTTP structured-output endpoint?
- Should live-provider evidence be generated and committed only as sanitized summary metadata, or left entirely local/private until a later closeout pass?
- Should the comparison set use only committed fixtures/reviewed variants, or include a small checked-in normalizer challenge fixture with unsafe and ambiguous examples?
