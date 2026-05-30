## Context

`voice-browser-agent` has reached a mature bounded-MVP shape: the repo contains OpenSpec main specs, checked-in sanitized traces, an Operator Console, public-readonly safety boundaries, visual verification evidence, normalizer comparison, a Speech-to-Task seed-set builder, and a held-out adaptation evaluation harness. The remaining risk is not missing runtime capability; it is final handoff drift. Some reviewer-facing docs still reference archived change validation commands, some final surfaces describe the adaptation seed set without the newer evaluation harness, and `CONTEXT.md` needs to reflect the latest archived capabilities.

The final completion audit should make the repository easy to review from a fresh checkout without widening scope into real model fine-tuning, checkpoint publication, public hosting, production web automation, or raw runtime artifact release.

## Goals / Non-Goals

**Goals:**

- Make final reviewer paths current after all relevant OpenSpec changes have been archived.
- Align `CONTEXT.md`, closeout checklist, public evidence page, interview overview, README/demo docs, tests, and OpenSpec specs around the same completion story.
- Ensure the final validation bundle uses commands that are valid after archive: main spec validation, full tests, whitespace checks, and ignored/generated-output audit.
- Include the Speech-to-Task adaptation evaluation harness in final review and release-pack instructions when its local manifest exists.
- Preserve evidence-first wording and privacy boundaries across public/reviewer surfaces.

**Non-Goals:**

- Do not add model fine-tuning, LoRA/SFT training scripts, training dependencies, checkpoints, or A100 training workflows to this project.
- Do not publish generated runtime artifacts or public-readonly raw traces.
- Do not expand public-web autonomy, account workflows, mutation workflows, captcha/verification bypass, production monitoring, or benchmark/leaderboard claims.
- Do not redesign the Operator Console or runtime execution stack.

## Decisions

1. Treat this as a handoff consistency audit, not a feature expansion.
   - Rationale: the project already has enough runtime/evidence features; completion quality now depends on reproducibility and claim hygiene.
   - Alternative considered: add a small fine-tuning pilot here. Rejected because the seed set is intentionally small and a training pilot would blur the app-project boundary.

2. Use main-spec validation as the durable OpenSpec gate.
   - Rationale: archived change names are no longer valid targets for `openspec validate <change> --strict`; final docs should use `OPENSPEC_TELEMETRY=0 openspec validate --all --strict` and any still-active change-specific validation only during apply.
   - Alternative considered: keep historical archived change commands as documentation. Rejected because they fail in the current repo state and confuse reviewers.

3. Keep generated review artifacts local and inspectable.
   - Rationale: release packs, normalizer comparisons, task-pack runs, Speech-to-Task datasets, and adaptation eval manifests are useful review surfaces, but they include local runtime context and should stay ignored unless intentionally sanitized and committed.
   - Alternative considered: commit final generated release pack. Rejected to keep privacy and artifact boundaries consistent with the repo's existing contract.

4. Make adaptation evaluation visible without implying model training.
   - Rationale: the eval harness is now part of the strongest final evidence chain, but it evaluates structured outputs from a small local seed set; it should be framed as adaptation-readiness evidence.
   - Alternative considered: omit adaptation evaluation from public/briefing surfaces. Rejected because the harness is already implemented and should be discoverable in the final handoff.

## Risks / Trade-offs

- Stale documentation commands remain after the audit -> add tests that execute or assert current validation command wording and reject archived change validation references in final handoff docs.
- Final surfaces overclaim adaptation evidence -> add wording guards for fine-tuning, checkpoint, benchmark, production, ASR/TTS, and broad-autonomy claims.
- Generated runtime artifacts leak into git -> include `git status --short --ignored` in the final validation bundle and keep runtime outputs ignored.
- The audit becomes a broad polish pass -> keep task scope tied to final handoff surfaces, spec deltas, tests, and verification only.
