## 1. Trace Schema And Verifier Contract

- [x] 1.1 Add a backward-compatible visual verification result model or trace field with outcome, expected condition, observed state summary, reason, verifier/provider mode, and sanitized evidence references.
- [x] 1.2 Add sanitizer coverage for visual verification fields so raw screenshots, raw annotated images, provider-private payloads, credentials, local paths, and remote host details are rejected or excluded.
- [x] 1.3 Add focused model/trace tests proving existing traces still load and new visual verification fields serialize safely.

## 2. Controlled Visual Verification Loop

- [x] 2.1 Implement a deterministic controlled visual verifier for local controlled tasks without requiring real VLM credentials or network access.
- [x] 2.2 Integrate visual verification into the agentic loop so action success is separate from visual outcome verification.
- [x] 2.3 Treat failed or uncertain verification as bounded control flow: re-observe or recover when budget allows, otherwise stop with an explicit verification reason.
- [x] 2.4 Preserve optional real-provider/VLM verifier configuration as private-by-default provenance without requiring it for default tests or release-pack generation.

## 3. Evidence Fixtures And Release Pack

- [x] 3.1 Extend controlled agentic trace generation to include at least one passed visual verification trace and one failed or uncertain verification trace.
- [x] 3.2 Update release-pack manifest generation to summarize verification outcome counts, verified fixtures, recovery count, failed or uncertain reasons, source paths, and privacy-scan status.
- [x] 3.3 Update release-pack HTML to show visual verification summaries without requiring raw trace JSON inspection.
- [x] 3.4 Add regression tests for missing verification evidence and privacy-unsafe verification artifacts.

## 4. Operator Console And Readiness

- [x] 4.1 Surface visual verifier readiness, mode, controlled verifier availability, optional provider state, and missing setup action in readiness data.
- [x] 4.2 Render visual verification outcome, expected condition, observed state summary, proof references, recovery decisions, and stop reasons in the Operator Console.
- [x] 4.3 Ensure failed or uncertain verification is not styled or summarized as a successful verified run.
- [x] 4.4 Add UI/API tests for passed verification, failed or uncertain verification, recovery flow, and privacy-safe rendering.

## 5. Documentation And Validation

- [x] 5.1 Update README, demo evidence docs, public evidence page, video plan, closeout checklist, and interview overview to describe visual verification loop evidence and its non-goals.
- [x] 5.2 Update `CONTEXT.md` coverage for visual verification terminology and implementation status.
- [x] 5.3 Run targeted tests for agentic execution, release-pack generation, Operator Console, and sanitizer behavior.
- [x] 5.4 Run full repository verification: `openspec validate visual-verification-loop-evidence --strict`, `openspec validate --all --strict`, `uv run pytest`, `git diff --check`, and generated/ignored output review.
