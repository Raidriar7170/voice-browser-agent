## Why

The project now has structured LLM-style normalization and useful public-readonly task evidence, but the visual execution story still needs a clearer post-action verification layer. This change makes the agent visibly prove whether a browser action achieved its intended visual outcome, strengthening the end-to-end "perceive, act, verify, recover" narrative without expanding into broad public-web autonomy or model training claims.

## What Changes

- Add explicit visual verification results after controlled visual actions, with `passed`, `failed`, or `uncertain` outcomes, target evidence, reason text, and sanitized evidence references.
- Extend the bounded agentic visual loop so failed or uncertain verification can trigger a bounded re-observation, recovery action, or explicit stop rather than silently treating an action event as success.
- Add controlled evidence fixtures for successful verification, no-effect verification, ambiguous/uncertain verification, and recovery or stop outcomes.
- Surface visual verification summaries in release-pack evidence and the Operator Console so reviewers can inspect completion proof without raw screenshots, browser profiles, credentials, local paths, or provider-private data.
- Keep real VLM/provider verification optional and private-by-default; the committed path must work with deterministic or mock verification over controlled local pages.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `agentic-vision-execution`: add explicit post-action visual verification results, bounded recovery decisions, and sanitized verification evidence requirements.
- `demo-evidence-set`: include visual verification loop evidence in committed/generated evidence without public raw screenshots or model-quality claims.
- `operator-console`: display visual verification status, proof summary, uncertainty/failure reasons, and recovery/stop decisions in the local reviewer console.

## Impact

- Affected code is expected around `voice_browser_agent.agentic`, execution trace models, trace sanitization/export, controlled trace generation scripts, release-pack generation, and Operator Console static UI/API surfaces.
- Existing execution routes and public-readonly boundaries remain bounded; no arbitrary URL execution, account workflow, mutation workflow, captcha bypass, or production automation is introduced.
- The default implementation must remain keyless and reproducible locally, with any real VLM/provider verification kept opt-in and local/private.
