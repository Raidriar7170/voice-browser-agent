## 1. Normalizer Configuration and Metadata

- [x] 1.1 Add runtime configuration for normalizer provider mode, fallback policy, prompt/schema version, and optional real-provider settings.
- [x] 1.2 Add safe normalizer provenance metadata to trace models or execution runtime payloads without exposing credentials, request headers, or raw provider responses.
- [x] 1.3 Update readiness/preflight output to report rule, deterministic mock LLM, configured real provider, fallback, or misconfigured provider states.
- [x] 1.4 Add regression tests proving default keyless behavior still uses rule-based normalization and existing execution gates.

## 2. LLM Structured-Output Normalizer

- [x] 2.1 Define a provider-neutral LLM normalizer client interface that returns candidate structured payloads.
- [x] 2.2 Implement deterministic mock LLM client behavior for tests and offline demos.
- [x] 2.3 Implement schema parsing for `BrowserTaskRequest` and `ClarificationRequest` outputs with explicit malformed-output errors.
- [x] 2.4 Implement fallback or clarification behavior when LLM output is malformed, unavailable, unsupported, or validation-unsafe.
- [x] 2.5 Add an optional real-provider adapter or generic provider boundary behind explicit configuration, keeping tests keyless.
- [x] 2.6 Add focused tests for valid LLM task output, clarification output, malformed JSON, unsafe-but-schema-valid output, provider failure, and fallback provenance.

## 3. App, API, and Operator Console Integration

- [x] 3.1 Wire `AppState` normalizer selection from runtime configuration while preserving rule-based default behavior.
- [x] 3.2 Ensure normalization, execution, fixture metadata, and reviewed-audio paths carry normalizer provenance consistently.
- [x] 3.3 Update API responses and sanitized exports so validator decisions, fallback state, and provider mode are inspectable but private provider data is excluded.
- [x] 3.4 Update the Operator Console to display normalizer source, provider mode, schema status, fallback reason, validator decision, confirmation state, and blocked/clarification reasons.
- [x] 3.5 Add UI/API tests for rule, mock LLM, fallback, confirmation, clarification, and blocked LLM-normalized command states.

## 4. Comparison Evidence and Release Handoff

- [x] 4.1 Add a local normalizer comparison workflow that runs rule and mock LLM modes over committed fixture transcripts and reviewed seed examples.
- [x] 4.2 Support optional real-provider comparison only when explicit provider configuration is present, and keep its outputs local/private by default.
- [x] 4.3 Emit a local comparison manifest or report with input ids, normalizer modes, output kinds, schema status, validator outcome, route readiness, fallback state, and privacy-scan status.
- [x] 4.4 Update demo evidence release-pack generation to include a bounded normalizer comparison summary when present and fail or warn clearly on malformed/private comparison evidence.
- [x] 4.5 Add privacy scans/tests ensuring comparison reports and release-pack summaries exclude API keys, raw prompts, raw provider responses, private URLs, local file URIs, remote host details, and unsanitized runtime fields.

## 5. Documentation and Positioning

- [x] 5.1 Update README, `.env.example`, demo docs, public evidence page, closeout checklist, and interview overview with normalizer mode setup and bounded LLM-normalizer explanation.
- [x] 5.2 Document the comparison workflow as local structured-output evidence, not model fine-tuning, benchmark ranking, SOTA, production automation, or broad autonomy.
- [x] 5.3 Update `CONTEXT.md` coverage matrix for LLM normalizer evidence, fallback behavior, comparison evidence, and remaining fine-tuning deferral.
- [x] 5.4 Add wording guards or documentation checks that prevent unsupported LLM/model-quality claims.

## 6. Verification

- [x] 6.1 Run `openspec validate llm-structured-normalizer-evidence --strict`.
- [x] 6.2 Run `openspec validate --all --strict`.
- [x] 6.3 Run targeted normalizer, API/UI, evidence-pack, and dataset/comparison tests.
- [x] 6.4 Run full `uv run pytest` from `voice-browser-agent/`.
- [x] 6.5 Run `git diff --check` and review `git status --short --ignored` for generated or private runtime artifacts.
