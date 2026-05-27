## Context

The current repo already covers the core MVP: one spoken command becomes a Browser Task Request or Clarification Request, deterministic checks run before browser execution, selected controlled visual tasks have live and agentic traces, and local builders create release-pack and Speech-to-Task dataset artifacts. The strongest remaining portfolio gap is evidentiary: reviewers can see that `browser-use-vision` is imported, but the checked-in evidence does not yet make one real visual-grounding path unmistakable.

This design keeps the next phase bounded. The change should improve reviewer confidence and resume value without turning the project into a training project, hosted service, or broad public-web automation system.

## Goals / Non-Goals

**Goals:**

- Produce at least one sanitized controlled trace that exercises real `browser-use-vision` visual grounding code.
- Keep deterministic preview/live/agentic evidence intact while separating real-vision evidence as its own evidence mode.
- Provide a committed public-safe evidence page that can be opened locally or hosted statically.
- Define a short demo/GIF artifact contract tied to fixture ids, trace ids, and privacy rules.
- Produce a modest 20-50 example Speech-to-Task seed set with provenance, correction or variant metadata, and privacy gates.

**Non-Goals:**

- Do not fine-tune models, publish checkpoints, or claim model-quality improvements.
- Do not collect or publish raw audio, raw screenshots, browser profiles, credentials, private URLs, remote host details, or unsanitized runtime traces.
- Do not run unrestricted public-web automation.
- Do not require remote A100/GPU infrastructure for the required path.
- Do not introduce benchmark leaderboards, SOTA framing, or production automation claims.

## Decisions

### Add a separate real-vision controlled evidence mode

Add a new evidence mode such as `real_vision_controlled` with a dedicated sanitized trace directory, for example `fixtures/traces/real-vision-sanitized/`. The required first target should be a stable local controlled page such as `icon-search` or `color-swatch`. The run should invoke `browser-use-vision` through the package boundary and record provider metadata, grounding references, and final status. If the full `VisionEnhancedAgent` path is too heavy for local deterministic validation, a narrower `browser-use-vision` module path such as SoM annotation plus visual evidence extraction is acceptable as long as tests prove the imported package produced the evidence.

Alternatives considered:

- Reuse existing deterministic controlled adapter evidence: stable, but it leaves the "only a wrapper" concern unresolved.
- Require remote Florence/OmniParser inference for the required trace: stronger when available, but too brittle for local reproducibility.
- Run a live public website through the full visual stack: flashy, but higher privacy and stability risk.

### Derive public evidence from committed sanitized sources

Create a committed static evidence page under a docs path such as `docs/public-evidence/index.html`. It should summarize the standalone project, architecture, evidence modes, trace directories, release-pack command, dataset/seed-set command, validation commands, demo media contract, and limitations. It may link to generated runtime paths as local build outputs, but the public page itself must not depend on ignored runtime artifacts.

Alternatives considered:

- Host the Operator Console: not needed for public review and raises deployment/runtime concerns.
- Commit generated `runtime/demo-evidence-release-pack/`: convenient, but mixes local generated artifacts into the public source tree.

### Treat demo media as a reproducible artifact contract

Keep the media scope small: a 60-90 second storyboard and, if a media file is committed, a small sanitized GIF/video under a documented docs path. The contract should specify which fixture or transcript to run, which trace/export to show, and what must not appear in the recording.

Alternatives considered:

- Record broad live browsing: less reproducible and weakens the bounded safety story.
- Leave only a text plan: lower effort, but less persuasive for portfolio review.

### Expand seed data through reviewed variants, not raw collection

The seed set should grow from sanitized trace-derived examples and reviewed correction or variant overlays. The manifest must distinguish original trace-derived examples from reviewed variants so the number is honest and auditable. The target size should be 20-50 examples, enough to show a data loop without pretending to train a model.

Alternatives considered:

- Collect a large raw speech dataset: too much scope and privacy surface.
- Generate synthetic examples without trace provenance: easier to inflate, weaker evidence.
- Train immediately: distracts from the end-to-end agent portfolio goal.

## Risks / Trade-offs

- Real `browser-use-vision` APIs may be heavier or less stable than deterministic adapters -> keep the required path controlled/local and fail clearly when real visual evidence is unavailable.
- The evidence page can drift -> test required references to committed trace directories, commands, and limitations.
- Demo media can leak private state -> use controlled fixtures and privacy scans or review checklist before committing/referencing media.
- Seed-set counts can look inflated -> track original examples and reviewed variants separately.
- Existing closeout work is still active -> keep this change additive and separate; archive closeout before or alongside implementation to avoid mixed handoff claims.

## Migration Plan

Add the new real-vision evidence group without changing existing preview, live-controlled, or agentic evidence semantics. Update release-pack and dataset builders to include the new group when present, and add strict completeness/privacy checks for the new public-evidence validation path. Generated runtime artifacts remain ignored; committed public artifacts remain sanitized and source-controlled.

## Open Questions

None blocking. During apply, choose the most stable controlled target after a read-only inspection of the local `browser-use-vision` APIs and controlled demo pages.
