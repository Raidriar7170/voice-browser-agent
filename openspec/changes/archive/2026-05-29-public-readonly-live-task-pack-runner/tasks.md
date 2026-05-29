## 1. Runner Contract and Manifest Tests

- [x] 1.1 Add failing tests for deterministic task-pack runner mode that validates selected task ids, rejects unknown ids, preserves pack validation, and writes a local/private manifest without opening public network pages.
- [x] 1.2 Add failing tests for full-pack runner output with run id, manifest version, timestamps, selected task ids, runner mode, configuration summary, outcome counts, privacy state, sanitizer state, limitations, and per-task rows.
- [x] 1.3 Add failing tests that runner rows preserve task id, category, kind, target class, target label, sanitized origin, completion criteria id, outcome, proof summary, unmet criteria, stop/failure reason, visible result state, sanitizer status, privacy state, and export state.
- [x] 1.4 Add failing tests that unsafe target URLs/templates, requested slots outside safe slots, unsupported actions, disabled public-readonly config, and page-open-only completion are blocked or marked incomplete.

## 2. Runner Implementation

- [x] 2.1 Implement `run_public_readonly_task_pack.py` or equivalent runner entry point with `--task-id`, `--all`, `--mode deterministic`, `--output-dir`, and project-root options.
- [x] 2.2 Reuse useful task-pack loading and validation as the runner source of truth instead of accepting ad hoc URLs or broad goals.
- [x] 2.3 Implement deterministic fake/dry-run execution that produces completed, partial, stopped, failed, and blocked rows using the same manifest schema as live mode.
- [x] 2.4 Implement live-mode orchestration through the existing public-readonly route/executor boundary, preserving task contracts, URL safety, action policy, completion verification, and step/time budgets.
- [x] 2.5 Write versioned run manifests under `runtime/public-readonly-task-pack/runs/<run_id>/manifest.json` while keeping raw traces and screenshots in ignored local/private runtime paths.

## 3. Safety, Privacy, and Evidence Integration

- [x] 3.1 Add regression coverage that live runner attempts use isolated local browser contexts with no persistent profile, cookie reuse, credential reuse, account session, or private-network target.
- [x] 3.2 Add regression coverage that captcha, verification, rate-limit, unavailable page, access denied, selector drift, timeout, network failure, login boundary, and off-contract action states are recorded as honest non-success outcomes.
- [x] 3.3 Extend sanitizer/privacy checks so runner manifests and release-pack summaries exclude raw screenshots, raw page text, cookies, credentials, browser profiles, local file URIs, private URLs, private data, remote host details, and unsanitized runtime fields.
- [x] 3.4 Extend demo evidence release-pack generation to include local/private live task-pack runner summaries when available and to report clear completeness/privacy errors for malformed manifests.

## 4. Readiness, Console, and Docs

- [x] 4.1 Extend readiness/preflight output with latest task-pack runner status, runner mode, selected task count, outcome counts, privacy state, sanitizer state, finished timestamp, and local/private artifact policy.
- [x] 4.2 Update the Operator Console to show latest runner status and row-level task outcomes before raw trace JSON, including deterministic-vs-live labels and local/private artifact labels.
- [x] 4.3 Update README, demo task suite, useful scenarios, public evidence page, video plan, closeout checklist, interview overview, and `CONTEXT.md` with runner commands, scope, limitations, and private-by-default evidence boundaries.

## 5. Verification

- [x] 5.1 Run targeted tests for runner contract validation, deterministic manifest output, live-mode safety policy, sanitizer/privacy gates, release-pack integration, readiness payloads, and console rendering.
- [x] 5.2 Run `openspec validate public-readonly-live-task-pack-runner --strict`.
- [x] 5.3 Run `openspec validate --all --strict`.
- [x] 5.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 5.5 Run `git diff --check`.
- [x] 5.6 Run `git status --short --ignored` and confirm raw public runtime traces, screenshots, browser profiles, generated run manifests, caches, and release packs remain ignored or unstaged unless explicitly intended.
