## Why

The project now proves reliable spoken-command execution on controlled local pages, but it still cannot operate real public webpages under an auditable safety contract. The next step is to add a narrow public-readonly execution path so the agent becomes a usable browser operator without drifting into unrestricted web autonomy.

## What Changes

- Add an opt-in `live_public_readonly` execution path for allowlisted public pages.
- Add a public-readonly safety policy that requires isolated browser contexts, no persistent cookies or browser profiles, no login/session reuse, short step budgets, and read-only or non-destructive actions only.
- Extend route selection so public commands can become controlled live, public-readonly, preview-only, clarification, confirmation, or blocked routes with clear explanations.
- Extend the browser executor with a bounded public-readonly observe-act-verify loop that records page-state and grounding evidence but stops before mutation, login, private data entry, upload, download, checkout, posting, or irreversible submission.
- Keep public-readonly traces local/private by default and add an explicit sanitizer/evidence contract before any public artifact is created.
- Update the Operator Console to show public-readonly readiness, allowlist status, private trace status, route decisions, stop reasons, and sanitized export eligibility.
- Add a small public-readonly smoke set for stable public pages such as documentation/search/read-only information pages; do not add logged-in sites or account mutation workflows.

## Capabilities

### New Capabilities

- `public-readonly-web-execution`: Defines the safety contract, configuration, execution behavior, private trace boundary, and evidence requirements for real public webpage operation.

### Modified Capabilities

- `operator-task-routing`: Route allowlisted public commands into public-readonly execution or explicit unsupported states without manual override bypass.
- `safe-browser-execution`: Integrate public-readonly execution with existing validation, confirmation, stop-condition, local browser, and missing-evidence safeguards.
- `operator-console`: Surface public-readonly route/readiness/private-trace state and preserve safe operator controls.
- `demo-evidence-set`: Document public-readonly smoke evidence as private-by-default and only publish sanitized artifacts after explicit privacy checks.

## Impact

- Affected models: `ExecutionMode`, `RouteType`, `RouteDecision`, execution runtime metadata, and sanitized trace fields.
- Affected execution path: route selection, browser executor config, Playwright context setup, agentic observe-act-verify loop, safety stop checks, trace writing, and export sanitization.
- Affected UI/API: command execution response, readiness/preflight output, Operator Console route/evidence panels, and sanitized export controls.
- Affected docs/evidence: README runtime notes, demo evidence docs, public evidence page, release-pack classification, and OpenSpec specs.
- Dependencies stay local-first: browser execution remains on the local machine; remote ASR or vision services remain optional inference backends only.
