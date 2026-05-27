## Context

The current MVP already has the pieces a reviewer needs: eight demo-preview traces, live-controlled traces for selected local visual tasks, agentic traces, demo docs, ablations, a bounded README, and an Operator Console that makes evidence paths clearer. The remaining friction is packaging. A reviewer still has to know which folders matter, which traces are preview versus live, which artifacts are sanitized, and which command proves the evidence set is complete.

This design adds a local release-pack workflow that packages existing sanitized evidence into a stable artifact without adding new browser autonomy or changing the execution loop.

## Goals / Non-Goals

**Goals:**

- Build one reproducible local evidence bundle from checked-in sanitized trace artifacts.
- Produce both a JSON manifest for automated checks and a browser-openable HTML index for interview walkthroughs.
- Preserve the distinction between demo-preview, live-controlled, and agentic evidence.
- Fail fast when required evidence is missing, malformed, ambiguous, or privacy-unsafe.
- Keep the pack useful offline after generation.

**Non-Goals:**

- Do not generate new raw recordings, raw screenshots, credentials, browser profiles, or private traces.
- Do not run unrestricted public-web live automation.
- Do not add benchmark scores, leaderboards, SOTA claims, or model-quality metrics.
- Do not fine-tune Speech-to-Task models or add new ASR/TTS model capability.
- Do not introduce a large dashboard framework or hosted publishing flow.

## Decisions

### Use a local script instead of a web app feature

Add a small repository script, for example `scripts/build_demo_evidence_pack.py`, that reads the existing sanitized trace directories and writes a pack under a generated artifacts directory. This keeps the packaging workflow reproducible from the command line and independent of the Operator Console runtime.

Alternatives considered:

- Add an Operator Console export-all button: convenient, but ties release packaging to a live browser session and makes reproducibility weaker.
- Add CI publishing: useful later, but premature for a local portfolio artifact and risks mixing public release concerns with local demo evidence.

### Emit manifest plus HTML index

The manifest should be the source of truth for tests: fixture id, evidence mode, source path, final status, stop/failure reason, grounding refs, agentic step count, and privacy-scan outcome. The HTML index should render the same manifest in a readable way for interview walkthroughs.

Alternatives considered:

- HTML only: good for humans, weak for automated verification.
- JSON only: good for tests, awkward for interviews.

### Treat privacy scan as a release gate

The builder should scan every copied trace and generated index for forbidden keys or strings such as raw audio paths, raw screenshots, cookies, credentials, private URLs, browser profile paths, remote host details, and local file URIs. The script should exit non-zero when the pack is unsafe or incomplete.

Alternatives considered:

- Rely on existing trace tests only: they are necessary but do not prove the assembled release pack is clean.
- Warn instead of fail: too easy to miss in a public handoff flow.

### Keep evidence modes explicit

The manifest should classify evidence into `demo_preview`, `live_controlled`, and `agentic_live_controlled` groups. Agentic traces are still live-controlled traces, but the release pack should name the agentic evidence mode separately so reviewers do not confuse action-list live traces with observe-act-verify traces.

Alternatives considered:

- Use only `execution_mode` from the trace: insufficient because both action-list and agentic traces use `live_controlled`.

## Risks / Trade-offs

- Evidence pack can drift from checked-in traces -> derive all rows from trace JSON and fail on missing required fixture coverage.
- HTML can become a second documentation source -> render directly from the manifest and keep prose minimal.
- Privacy scan can false-positive on benign words -> keep the forbidden list focused on known private fields and sensitive runtime markers.
- Live evidence may be stale -> record source trace paths and generated timestamp so reviewers can reproduce or regenerate.

## Migration Plan

This is additive. Existing trace generation scripts and docs stay in place. The release-pack builder consumes current sanitized traces and writes generated artifacts under an ignored or explicitly documented output directory. If the pack builder fails, existing demo evidence remains unaffected.

## Open Questions

None for this phase. Keep the scope to packaging existing sanitized evidence and proving completeness/privacy, not adding new execution behavior.
