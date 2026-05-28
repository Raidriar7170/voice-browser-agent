## Why

The current public-readonly lane can open allowlisted public pages in an isolated browser context, but it does not yet prove that a real public webpage task was completed. This change closes that credibility gap by turning public-readonly runs from "page touched" evidence into bounded task-completion evidence with explicit success, partial, stopped, and failed outcomes.

## What Changes

- Add public task definitions for allowlisted targets, including task kind, allowed actions, target URL or template, query or extraction slots, completion criteria, and privacy policy.
- Extend route selection so public commands map to a specific public task definition, not only a domain or target label.
- Extend the public-readonly executor from open-and-observe behavior to bounded read-only task execution, including documentation search, safe result navigation, read-only expansion, and visible information extraction.
- Add a deterministic completion verifier that records whether the requested public task was completed, partially completed, stopped by policy, failed due to site/network variance, or blocked before navigation.
- Preserve the existing safety boundary: no login, no persistent profile, no cookies, no upload/download, no posting, no purchase, no private-data entry, no arbitrary URL navigation, and no long-horizon browsing.
- Keep public-readonly traces local/private by default while allowing a sanitized summary or explicitly approved trace export when privacy checks pass.
- Update the Operator Console and evidence docs so reviewers can see target label, task kind, completion criteria, observed proof, stop/failure reason, and local/private sanitizer state.

## Capabilities

### New Capabilities

- None. This change strengthens the existing bounded public-readonly execution contract rather than creating a new broad public-web automation capability.

### Modified Capabilities

- `public-readonly-web-execution`: require allowlisted public task definitions, task completion criteria, completion verification, and private-by-default task evidence.
- `operator-task-routing`: route public commands to specific public task definitions and reject public commands that do not match a configured task contract.
- `safe-browser-execution`: enforce completion-aware public-readonly execution, missing-completion failure behavior, and policy stops during real public task attempts.
- `operator-console`: surface public task plan, completion state, observed proof, policy stop reasons, and local/private sanitizer status.
- `demo-evidence-set`: define private real-public task smoke evidence and public-safe summaries without overclaiming production web automation.
- `spoken-command-normalization`: preserve public task slots such as target site, search query, read target, extraction target, and read-only intent for route selection and completion verification.

## Impact

- Affected backend code: public-readonly policy and target parsing, route selection, browser executor, trace models, sanitizer/export logic, readiness checks, and task smoke generation scripts.
- Affected UI/API: execution response payloads, Operator Console route/evidence panels, readiness display, and sanitized export messaging.
- Affected tests: normalizer slot extraction, public task routing, Playwright public-readonly task execution, completion verification, safety stops, sanitizer behavior, and release-pack exclusion/summary rules.
- Affected docs/artifacts: README runtime notes, public-readonly smoke fixture, demo evidence docs, public evidence page, closeout/interview material, and OpenSpec specs.
- External behavior remains bounded and opt-in: public tasks require explicit allowlist configuration and run locally in isolated browser contexts with private traces by default.
