## Context

The project already has an opt-in `live_public_readonly` lane, explicit public task contracts, completion verification, local/private visual artifacts, a 5-task reliability matrix, and a 10-task useful task pack summary. The useful task pack is currently reviewer-readable metadata rather than a reproducible local live run workflow.

This design keeps the same bounded Voice-to-Browser Agent contract: public execution is disabled by default, runs use local isolated browser contexts, task contracts remain explicit, raw public runtime artifacts remain local/private, and public docs avoid production or broad-autonomy claims.

## Goals / Non-Goals

**Goals:**

- Add an opt-in runner that can execute the useful public-readonly task pack or a selected subset from the command line.
- Produce a versioned local/private run manifest under `runtime/public-readonly-task-pack/runs/<run_id>/manifest.json`.
- Record one row per task attempt with contract metadata, requested slots, route/execution state, outcome, proof summary, unmet criteria, stop/failure reason, sanitizer state, guarded visual artifact state, and export state.
- Provide deterministic fake or dry-run execution for tests and docs without depending on public network availability.
- Surface latest run metadata through readiness/API and the Operator Console while preserving local/private labels.
- Let release-pack output reference only sanitized summaries or local/private exclusion reasons, never raw public screenshots, page text, cookies, browser profiles, or local runtime paths.

**Non-Goals:**

- No arbitrary public URL runner, crawl mode, search-engine automation, account workflow, mutation workflow, upload/download workflow, or captcha/verification bypass.
- No CI requirement that real public network tasks complete.
- No public hosting, background scheduler, multi-user run history, or production monitoring.
- No committed raw public task traces, screenshots, page text, browser profiles, cookies, recordings, or generated runtime directories.
- No leaderboard, benchmark score, model-quality claim, or broad web-autonomy claim.

## Decisions

### Reuse Task Contracts as the Runner Source

The runner loads `fixtures/public-readonly-useful-task-pack.json` and uses only validated task contracts. Task selection is by explicit task id list or a bounded `--all` pack run. Every task still goes through URL safety, allowed-actions, slot coverage, completion criteria, and privacy-policy validation before any live attempt.

Alternative considered: let the runner accept ad hoc URLs or natural-language goals. That would make the tool feel more flexible, but it breaks the evidence story and weakens the safety model.

### Make Live Network Optional and Test Mode Deterministic

The default implementation should expose a deterministic fake/dry-run adapter for tests and examples, while real public execution remains opt-in through existing runtime configuration. CI verifies schema, policy, safety, manifest writing, and outcome classification without requiring successful public network access.

Alternative considered: run the full public pack in tests. That would produce stronger live proof on a good day, but it would make correctness depend on site drift, rate limits, localization, network availability, and anti-bot systems.

### Write Versioned Manifests, Not Public Artifacts

Each run writes a local directory containing `manifest.json` and optional guarded references to traces or screenshots. The manifest is the durable contract: it records run id, started/finished timestamps, selected task ids, configuration snapshot, outcome counts, rows, privacy state, sanitizer state, and limitation notes. Raw artifacts stay in ignored runtime paths and are never copied into committed evidence by default.

Alternative considered: write one flat `summary.json` in the existing task-pack runtime directory. A flat file is simpler, but a run directory gives reviewers repeatability and lets later runs coexist without overwriting earlier evidence.

### Treat Site Variance as First-Class Evidence

The runner must preserve `completed`, `partial`, `stopped`, `failed`, and `blocked` outcomes. Captcha, verification, rate-limit, permission boundaries, redirects, selector drift, unavailable pages, and network failures become explicit outcome reasons, not hidden retries or fake success.

Alternative considered: retry or skip flaky tasks until a green summary exists. That would be misleading for a reliability project; the interesting evidence is often the boundary state.

### Publish Summaries Only After Privacy Review

Readiness, console, and release-pack surfaces can show task ids, target labels, sanitized origins, completion criteria ids, outcome summaries, proof keys, unmet criteria, sanitizer state, and local/private status. They must not expose raw URLs with private material, raw screenshots, raw page text, cookies, browser profiles, local file URIs, or remote host details.

Alternative considered: include thumbnails or page excerpts in the release pack for review convenience. That creates accidental privacy and copyright risk and moves the project away from bounded metadata evidence.

## Risks / Trade-offs

- Public pages can drift or block automation -> record precise stopped/failed/blocked outcomes and keep deterministic fake mode for verification.
- The runner can look like a general browser automation harness -> require explicit task ids/contracts, disabled-by-default live mode, and docs that state non-goals.
- Manifests can leak local paths or raw artifact details -> sanitize manifest fields and add privacy regression tests before release-pack inclusion.
- Console status can become noisy -> show the latest run summary first and keep row details compact.
- Live pack runs can be slow -> support selected task ids, step/time budgets, and early policy blocks.
