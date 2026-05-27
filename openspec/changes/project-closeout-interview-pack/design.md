## Context

The repo now has the functional MVP surface and several evidence-producing workflows: Operator Console execution, sanitized preview/live/agentic traces, demo evidence release pack, and Speech-to-Task adaptation dataset. The remaining closeout risk is presentation drift: a reviewer can still miss the strongest evidence, confuse generated local artifacts with committed sources, or hear a story that overstates autonomy, benchmark status, ASR/TTS quality, or model training.

This phase creates a final handoff layer from existing repo evidence. It should make the project easy to review and explain without changing core runtime behavior.

## Goals / Non-Goals

**Goals:**

- Produce a browser-openable interview/project briefing that is self-contained and evidence-backed.
- Provide a closeout checklist that records the exact local commands and artifact paths needed before archive/commit.
- Tie the final story to committed sources: OpenSpec specs, README/docs, sanitized traces, release-pack manifest, adaptation dataset manifest, and test output.
- Keep final handoff language bounded, privacy-safe, and honest about limitations.
- Make the final handoff mechanically testable through structural, wording, and privacy checks.

**Non-Goals:**

- Do not add new execution capability, ASR/TTS model capability, model fine-tuning, remote GPU workflow, or public raw dataset.
- Do not publish generated runtime artifacts into version control.
- Do not create a leaderboard, benchmark result page, production automation claim, or unrestricted public-web autonomy demo.
- Do not rewrite the existing product scope or merge `browser-use-vision` into this repo.

## Decisions

### Use a static browser-openable HTML briefing

Create a checked-in static HTML briefing, for example `docs/interview-project-overview.html`, that can be opened directly in a browser. It should be based on repo evidence and validation artifacts rather than memory, and it should include a concise talk track plus reviewer navigation.

Alternatives considered:

- Markdown only: easier to maintain, but weaker for interview practice and less polished for a reviewer walkthrough.
- Hosted page: unnecessary for local closeout and adds deployment work outside the MVP.

### Pair the briefing with a closeout checklist

Add a short closeout checklist document, for example `docs/demo/closeout-checklist.md`, that enumerates the pre-archive and pre-commit checks: release pack build, dataset build, OpenSpec validation, pytest, diff whitespace, privacy-sensitive ignored outputs, and git status review.

Alternatives considered:

- Put everything in README: bloats the public entry point and makes the reviewer story less scannable.
- Rely on OpenSpec tasks only: good for implementation, but not as friendly for final project handoff.

### Test the artifact structure and wording

Add tests that ensure the briefing and checklist reference required evidence paths, validation commands, limitations, and generated local artifacts. Reuse existing wording guard patterns to prevent unsupported claims.

Alternatives considered:

- Manual review only: too easy to drift when README or docs change.
- Screenshot-driven browser QA only: useful later if styling is complex, but structural checks are enough for a static closeout artifact.

## Risks / Trade-offs

- Final artifact can become stale -> include validation commands and generated timestamp guidance instead of hardcoding unverifiable current outputs.
- Briefing can overclaim -> enforce wording guards and include explicit limitations/non-goals.
- HTML can become too long to maintain -> keep it as a concise project overview, not a full slide deck.
- Generated runtime artifacts can leak into git -> closeout checklist and status checks must keep `runtime/` ignored.

## Migration Plan

This is additive. Existing README, demo docs, trace artifacts, release-pack builder, dataset builder, and OpenSpec specs remain valid. The new docs reference them as the final review path. If the briefing/checklist checks fail, core runtime behavior is unaffected.

## Open Questions

None for this phase. Any later public hosting, model training, or expanded evaluation should be planned as a separate OpenSpec change.
