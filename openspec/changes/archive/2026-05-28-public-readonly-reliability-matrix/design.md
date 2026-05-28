## Context

The project already has an opt-in `live_public_readonly` lane with allowlisted public task contracts, isolated browser contexts, private-by-default traces, completion verification, and visible result panels. The remaining credibility gap is not whether one public task can run, but whether a reviewer can inspect a repeatable matrix of real public-readonly outcomes and trust that failures, stops, partial completions, and blocks are classified honestly.

The design keeps the existing bounded Voice-to-Browser Agent contract intact: local browser execution, no account/session reuse, no mutation, no arbitrary URL browsing, no captcha bypass, no raw public runtime artifacts in public evidence, and no production automation claim.

## Goals / Non-Goals

**Goals:**

- Define a 5-8 task public-readonly reliability smoke set using explicit task contracts.
- Capture matrix rows for completed, partial, stopped, failed, and blocked public task outcomes.
- Make completion proof, unmet criteria, stop/failure reason, safety policy reason, and privacy/export state inspectable in API responses, the Operator Console, and local release-pack summaries.
- Add regression tests for unsafe shortcuts and misleading success cases.
- Preserve private-by-default handling for raw public traces, screenshots, page text, browser profiles, cookies, credentials, and local paths.

**Non-Goals:**

- No arbitrary public-web browsing or transcript-emitted URL execution.
- No login, account automation, GitHub star/fork/comment/issue/pull-request, form submission, purchase, upload, download, or private-data entry.
- No captcha, verification, rate-limit, or anti-bot bypass.
- No public raw screenshots, raw page text, raw public traces, public datasets, or model-quality claims.
- No production deployment, background scheduler, multi-user auth layer, or long-horizon browser autonomy.

## Decisions

### Use Task Contracts as the Matrix Source of Truth

The reliability matrix should be generated from explicit public task contracts and their execution or fixture outcomes, not from ad hoc console runs. Each contract should identify target class, allowlist id, task kind, safe slots, URL/template, allowed action classes, completion criteria, limits, and privacy policy.

Alternative considered: infer matrix rows from arbitrary public-readonly traces. That would make review easier to drift and could accidentally treat unsupported or unsafe runs as part of the reliability surface.

### Classify Outcomes Separately from Final Status

Each public task attempt should preserve a public task outcome classification: `completed`, `partial`, `stopped`, `failed`, or `blocked`. This is related to, but more specific than, a generic execution final status. A page can open successfully and still be `partial` or `failed` if task-specific proof is absent.

Alternative considered: reuse only `final_status`. That hides the distinction between safe policy stops, site variance, incomplete proof, and pre-navigation blocks.

### Keep Raw Public Runtime Evidence Local

The matrix may include sanitizer-approved summaries and guarded local artifact references, but raw public traces, screenshots, and page text remain local/private unless an explicit public-readonly sanitizer approves them. Release-pack output should prefer summaries over raw copies.

Alternative considered: commit representative public screenshots. That creates privacy, copyright, site-variance, and accidental-account-state risk without improving the bounded reliability claim enough to justify it.

### Show Matrix Evidence in the Console Before Raw JSON

The Operator Console should display task id, target class, completion criteria, observed proof, unmet criteria, outcome, stop/failure reason, visible result state, and sanitizer/export state in a compact panel. Raw trace JSON remains available for inspection, but the reviewer path should not depend on reading raw JSON first.

Alternative considered: keep the matrix only in generated release artifacts. That would miss the live operator debugging moment where misleading success styling is most dangerous.

## Risks / Trade-offs

- Public site markup can drift -> keep tasks small, classify site variance explicitly, and treat missing proof as partial/stopped/failed rather than success.
- The smoke set can become too broad -> cap the matrix at 5-8 tasks and require allowlist plus task-contract approval for every row.
- Privacy checks can over-block useful summaries -> keep raw artifacts local and export only minimal approved metadata: target label, sanitized origin, proof summary, outcome, reason, and privacy status.
- Console UI can become noisy -> present the matrix as a compact status panel with raw trace JSON behind advanced inspection.
- Tests could become network-flaky -> rely on deterministic policy/verifier/unit tests plus optional local/private smoke generation; do not require live public network success for every CI path unless explicitly configured.
