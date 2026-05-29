## Context

Voice-to-Browser Agent already has a bounded agentic visual execution loop with observation, action, verification decision, recovery decision, and sanitized step evidence. The current evidence is strong enough to show that controlled actions happened, but the reviewer-facing proof still blends "action returned succeeded" with "the visual goal was actually achieved."

The next stage should make post-action visual verification explicit while preserving the project's constraints: controlled local tasks first, deterministic/keyless default behavior, optional provider/VLM trials only when configured, and private-by-default handling for raw screenshots or provider responses.

## Goals / Non-Goals

**Goals:**

- Represent post-action visual verification as a first-class result in traces and summaries.
- Verify controlled visual tasks against expected visual outcomes, not just action return codes.
- Support bounded recovery when verification fails or is uncertain.
- Surface verification proof in release-pack evidence and the Operator Console.
- Preserve sanitized public artifacts and avoid storing raw screenshots, provider-private payloads, credentials, local paths, or remote host details.

**Non-Goals:**

- No generic public-web VLM autonomy.
- No broad website crawler, account workflow, mutation workflow, captcha bypass, or production automation.
- No model fine-tuning or checkpoint publication.
- No requirement for real VLM credentials in the default local path.
- No publishing of raw screenshots, raw provider prompts, or raw provider responses.

## Decisions

1. **Use an explicit verifier result model instead of overloading action status.**

   Add a visual verification result concept with outcome, reason, observed state summary, expected condition, sanitized evidence refs, and optional provider mode. This keeps "the click succeeded" separate from "the intended visual state was confirmed."

   Alternative considered: keep using `AgenticVerificationDecision` only. That is simpler, but it does not give enough reviewer-facing detail to distinguish action completion, visual proof, uncertainty, and privacy boundaries.

2. **Default to deterministic controlled verification.**

   The committed path should verify local controlled pages with known expected state markers, DOM-visible state, screenshot/grounding refs, and mock/provider-neutral metadata. This keeps tests and release-pack generation reproducible without model credentials.

   Alternative considered: require a real VLM for verification. That would look more "AI-heavy" but would make the core demo brittle, credential-dependent, and harder to review safely.

3. **Make real VLM verification optional and local/private.**

   If a real verifier provider is later configured, traces may include safe provenance such as provider mode, schema/version, outcome, and privacy scan. Raw prompts, raw responses, request headers, API keys, raw screenshots, and local/private paths must remain excluded from committed or public artifacts.

   Alternative considered: commit provider outputs as evidence. That would increase apparent model evidence but conflicts with the project's existing sanitized-artifact boundary.

4. **Treat failed or uncertain verification as control flow.**

   A failed or uncertain verification can trigger one bounded re-observation/recovery attempt when budget allows. If uncertainty remains, execution stops with an explicit verification reason instead of claiming success.

   Alternative considered: record verification failures only as metadata after a successful action. That weakens the reliability story because the agent would still appear successful when the visual goal was not proven.

5. **Surface summaries before raw trace details.**

   Release-pack and console views should show compact verification status, proof summary, recovery count, and stop/failure reason before raw JSON. Reviewers should not need to parse trace internals to see whether the visual loop closed.

   Alternative considered: only update trace schema. That is technically sufficient but weaker for interview/demo use.

## Risks / Trade-offs

- Deterministic verifier may feel less "model-heavy" than a real VLM -> Mitigation: design the boundary so deterministic verification is the reproducible default and real VLM verification can be opt-in private evidence later.
- Adding trace fields can create sanitizer gaps -> Mitigation: add privacy scans and tests for forbidden markers across trace export, release pack, and console-facing payloads.
- Recovery behavior can create accidental scope expansion -> Mitigation: keep recovery budgets small, controlled-page only by default, and reuse existing validation, confirmation, and stop-condition gates.
- Console evidence can become noisy -> Mitigation: show compact summaries first and keep raw trace JSON as an advanced inspection path.
- Release-pack requirements can become brittle -> Mitigation: require a small set of controlled verification outcomes rather than broad coverage across every demo task.

## Migration Plan

1. Add visual verification fields in a backward-compatible way so existing traces without verification results still load.
2. Extend controlled agentic adapters and trace generation to emit verification results for selected tasks.
3. Update sanitization, release-pack, and console summaries to include verification fields when present.
4. Add tests for success, no-effect/failure, uncertainty, recovery, privacy scan, release-pack summary, and console rendering.
5. Refresh docs and `CONTEXT.md` coverage to position the feature as visual verification evidence, not benchmark or broad autonomy evidence.
