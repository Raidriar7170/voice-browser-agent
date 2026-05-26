## Why

`CONTEXT.md` is the durable domain contract, but it currently defines the project language without a current coverage matrix that proves each commitment is implemented, tested, documented, specified, evidenced, or intentionally deferred. A final closeout pass is needed so the repository can show full coverage without narrowing the Voice-to-Browser Agent scope or making benchmark, SOTA, production, or unrestricted autonomy claims.

## What Changes

- Add a line-referenced coverage matrix to `CONTEXT.md` for every domain term and example-dialogue commitment.
- Replace placeholder `Purpose` text in the main OpenSpec specs with scope-specific purpose statements.
- Add a small trace-derived training example export surface so Execution Traces can support later Speech-to-Task Adaptation without committing raw private traces.
- Tighten optional Status Voice Feedback coverage in the Operator Console through explicit playback gating and tests.
- Preserve the existing boundary: `browser-use-vision` remains a dependency, browser execution remains local by default, remote GPU services remain optional for heavy inference, and public artifacts remain sanitized evidence rather than benchmark claims.

## Capabilities

### New Capabilities

- `trace-derived-training-examples`: Convert sanitized Execution Trace content plus optional human correction into a Speech-to-Task training example for later adaptation work.

### Modified Capabilities

- `operator-console`: Make optional Status Voice Feedback an explicit, gated console behavior.
- `spoken-command-ingestion`: Clarify that transcript metadata and trace-derived examples support later adaptation while raw audio remains outside public artifacts.
- `spoken-command-normalization`: Clarify trace-derived normalization evidence as the source for later Speech-to-Task examples.
- `demo-evidence-set`: Require the durable coverage matrix and explicit deferral/non-goal rows for commitments that are intentionally not implemented in the MVP.

## Impact

- Affects `CONTEXT.md`, main OpenSpec specs, a small trace-derived training example model/helper, Operator Console JavaScript, tests, and public demo documentation as needed.
- Does not add raw audio, raw screenshots, browser profiles, credentials, private URLs, remote host details, checkpoints, or unsanitized live browser state.
- Does not absorb or copy `browser-use-vision` internals, add remote browser execution, introduce a large orchestration framework, or claim benchmark/SOTA/production autonomy.
