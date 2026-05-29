## Why

The public-readonly reliability matrix proves the safety contract, but the current smoke set is still a compact outcome matrix rather than a useful task pack a reviewer can run and inspect. The next stage should broaden real public-readonly evidence to a small set of practical documentation, reference, package, and public repository read tasks without drifting into arbitrary public-web autonomy.

## What Changes

- Add a separate 8-12 task useful task pack alongside the 5-task public-readonly reliability matrix.
- Favor stable read-only public targets such as documentation pages, reference pages, package metadata, public repository search/read, public release notes, and standards/reference content.
- Add a local task-pack runner that loads explicit task contracts, runs or summarizes task attempts, and writes a local/private matrix artifact under `runtime/`.
- Require task-pack rows to keep the same outcome vocabulary: `completed`, `partial`, `stopped`, `failed`, and `blocked`.
- Keep task-specific completion criteria mandatory; a page-open-only run is still incomplete.
- Update Operator Console/API surfaces so useful task-pack status can be inspected without reading raw trace JSON first.
- Extend release-pack summaries to include local/private useful task-pack summary metadata while excluding raw public traces, screenshots, page text, cookies, browser profiles, local paths, credentials, private data, and remote host details.
- Preserve safety boundaries: no arbitrary URL execution, no login/session reuse, no account workflows, no mutation, no upload/download, no captcha or verification bypass, no private-network targets, and no long-horizon browsing.

## Capabilities

### New Capabilities

- None. This change broadens and operationalizes the existing public-readonly execution and evidence contracts.

### Modified Capabilities

- `public-readonly-web-execution`: define an 8-12 task useful public-readonly task pack, local task-pack run artifacts, task-pack summary fields, and safety-preserving completion outcomes.
- `operator-task-routing`: route expanded useful public commands only when a matching task contract exists and preserve stable rejected-route reasons.
- `safe-browser-execution`: preserve read-only, bounded, isolated execution for the broader useful task pack and report unsafe public actions as explicit outcomes.
- `operator-console`: display task-pack summary, selected task contract, outcome, proof, unmet criteria, route reason, visible-result state, and export state before raw trace JSON.
- `demo-evidence-set`: include a reviewer-readable useful task-pack summary in local release-pack output while keeping raw public runtime artifacts private by default.
- `spoken-command-normalization`: preserve safe slots for expanded documentation, package, release-note, reference, and public repository commands while rejecting unsupported broad or write-capable commands.

## Impact

- Affected backend code: public task contract loading, useful task-pack manifest/model validation, local runner/summary generation, completion verifier metadata, route matching, public-readonly safety checks, and release-pack generation.
- Affected UI/API: execution responses, readiness/task-pack status, Operator Console result panels, visible result messaging, and local export summaries.
- Affected tests: smoke/task-pack contract validation, expanded slot normalization, route selection, unsafe command rejection, runner output, release-pack privacy gates, API responses, and console rendering.
- Affected docs/evidence: README, useful scenarios, demo task suite, public evidence page, video plan, closeout checklist, interview material, `CONTEXT.md`, and OpenSpec specs.
