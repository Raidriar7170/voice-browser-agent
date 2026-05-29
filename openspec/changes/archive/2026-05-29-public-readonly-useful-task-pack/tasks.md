## 1. Useful Task-Pack Contract Tests

- [x] 1.1 Add failing tests for loading an 8-12 task useful public-readonly task pack with category coverage, task categories, target classes, task ids, safe slots, completion criteria, limits, privacy policy, and expected task-pack coverage.
- [x] 1.2 Add failing tests that task packs with fewer than 8 tasks, more than 12 tasks, missing categories, missing completion criteria, or non-read-only actions are rejected.
- [x] 1.3 Add failing tests that useful task-pack rows preserve completed, partial, stopped, failed, and blocked outcomes without allowing page-open-only success.

## 2. Normalization and Routing

- [x] 2.1 Add failing tests for normalizing useful public-readonly commands for documentation, reference, package metadata, release notes, and public repository search/read slots.
- [x] 2.2 Add failing tests that broad browsing, arbitrary URLs, account actions, mutation actions, upload/download, private-network targets, captcha bypass, and manual override attempts do not route to `live_public_readonly`.
- [x] 2.3 Extend route decisions for useful task-pack matches with task id, task category, completion criteria id, evidence privacy state, sanitizer status, and stable rejected-route reasons.

## 3. Runner, Summary, and Release Pack

- [x] 3.1 Implement useful task-pack manifest/model loading and validation while preserving disabled-by-default public-readonly behavior.
- [x] 3.2 Implement local/private useful task-pack summary generation under `runtime/` with task count, category coverage, outcome counts, proof, unmet criteria, stop/failure reason, privacy state, sanitizer status, visible result state, and export state.
- [x] 3.3 Extend the evidence release-pack builder to include local/private useful task-pack summary metadata and exclude raw public runtime traces, screenshots, page text, cookies, credentials, browser profiles, local paths, private data, and remote host details.

## 4. Operator Console, API, and Docs

- [x] 4.1 Extend API/readiness or execution payloads with useful task-pack status and summary fields required by the console.
- [x] 4.2 Update the Operator Console to show useful task-pack availability, category coverage, task rows, outcome, proof, unmet criteria, route reason, visible-result state, privacy state, sanitizer status, and export state before raw trace JSON.
- [x] 4.3 Update README, useful scenarios, demo task suite, public evidence page, video plan, closeout checklist, interview material, and `CONTEXT.md` with useful task-pack scope, limitations, commands, and private-by-default boundaries.

## 5. Verification

- [x] 5.1 Run targeted tests for task-pack loading, summary generation, normalization, routing, release-pack privacy gates, API payloads, and console rendering.
- [x] 5.2 Run `openspec validate public-readonly-useful-task-pack --strict`.
- [x] 5.3 Run `openspec validate --all --strict`.
- [x] 5.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 5.5 Run `git diff --check`.
- [x] 5.6 Run `git status --short --ignored` and confirm raw public runtime traces, screenshots, uploads, browser profiles, caches, and generated release packs remain ignored or unstaged.
