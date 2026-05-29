## Context

The project already has a disabled-by-default `live_public_readonly` lane with allowlisted task contracts, isolated local browser contexts, completion verification, local/private visual artifacts, and a 5-task reliability matrix. That matrix is good safety evidence, but it is still too small and outcome-oriented to feel like a useful real-world task pack.

This design keeps the bounded Voice-to-Browser Agent contract intact: local browser execution, no account/session reuse, no mutation, no arbitrary URL browsing, no captcha bypass, no public raw runtime artifacts, and no production automation claim.

## Goals / Non-Goals

**Goals:**

- Define an 8-12 task useful public-readonly pack across stable documentation, reference, package metadata, release-note, and public repository read/search targets.
- Add a local runner or summary builder that produces inspectable task-pack matrix output under `runtime/`.
- Surface task-pack catalog, row outcome, proof, unmet criteria, and export state in API/Operator Console/release-pack summaries.
- Preserve the existing outcome vocabulary: `completed`, `partial`, `stopped`, `failed`, and `blocked`.
- Add regression tests for task-pack size, category coverage, completion proof, route matching, unsafe command rejection, summary output, and privacy gates.

**Non-Goals:**

- No arbitrary public-web browsing or transcript-emitted URL execution.
- No login, account automation, write-capable GitHub actions, form submission, purchase, upload, download, or private-data entry.
- No captcha, verification, anti-bot, rate-limit, or permission-boundary bypass.
- No public raw screenshots, raw page text, raw public traces, public datasets, or model-quality claims.
- No cloud deployment, multi-user auth, background scheduler, or long-horizon browser autonomy.

## Decisions

### Keep the Task Pack Contract-First

The useful pack is a manifest of explicit task contracts and expected evidence fields, not a free-form list of websites. Contracts remain the source of truth for target, allowed slots, target URL/template, completion criteria, execution limits, privacy policy, and category.

Alternative considered: allow the operator to type any public URL and rely on safety stops. That would make the project look more capable in a demo, but it weakens the bounded reliability story and makes privacy/export guarantees much harder to review.

### Treat Runtime Evidence as Local and Summaries as Reviewable

The local runner writes task-pack run summaries under `runtime/` and may reference local/private traces or screenshots. Release-pack output only includes local/private summary metadata: task id, category, target label, sanitized origin, outcome, observed proof summary, unmet criteria, stop/failure reason, sanitizer state, privacy state, and export state.

Alternative considered: commit representative public screenshots or page text. That creates privacy, copyright, site drift, and accidental account-state risk without adding enough credibility to justify it.

### Prefer Stable Read-Only Targets

The pack favors documentation/reference/package/repository pages with direct URLs or deterministic templates. Search-engine tasks are avoided because they often produce captcha, anti-bot, localization, or result-order instability.

Alternative considered: use broad web search tasks to appear more realistic. That would shift the evidence from agent reliability to site variance and anti-bot behavior.

### Reuse the Reliability Matrix Data Model

The useful pack should extend existing public-readonly matrix rows and summaries instead of adding a parallel result schema. A useful row can add category/source-pack metadata, but the outcome and privacy semantics stay the same.

Alternative considered: create a separate "benchmark result" schema. That risks overclaiming and conflicts with the project's non-benchmark positioning.

## Risks / Trade-offs

- Public site markup can drift -> keep completion criteria explicit and record missing proof as partial/stopped/failed rather than success.
- Pack can become too broad -> cap the first useful pack at 8-12 tasks and require task-contract approval for every row.
- Live network tests can be flaky -> use deterministic contract/unit tests plus optional local/private live runs; CI should not require public network success unless explicitly configured.
- Console can become noisy -> show compact task-pack status first and leave raw JSON behind advanced inspection.
- Privacy checks can over-block useful summaries -> keep raw artifacts local and export minimal approved metadata only.
