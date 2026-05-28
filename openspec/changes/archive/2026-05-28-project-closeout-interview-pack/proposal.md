## Why

The bounded Voice-to-Browser Agent now has the core execution loop, sanitized demo evidence, release-pack workflow, and Speech-to-Task adaptation dataset, but the final reviewer path is still spread across README sections, demo docs, generated local artifacts, OpenSpec changes, and test commands. The next phase should convert the completed MVP into a coherent closeout and interview handoff pack so the project can be archived, committed, reviewed, and explained without relying on memory or unsupported claims.

## What Changes

- Add a browser-openable interview/project briefing that explains the project from repo evidence: problem, bounded scope, architecture, execution flow, evidence modes, safety/privacy gates, dataset output, validation results, limitations, and talk track.
- Add a closeout checklist that ties together OpenSpec archive state, generated release pack, generated adaptation dataset, test commands, privacy scans, and git hygiene.
- Add documentation tests or structural checks that ensure the briefing and closeout docs reference the committed evidence sources and generated local artifact paths.
- Add wording guards so final handoff material stays aligned with the bounded Voice-to-Browser Agent scope and avoids benchmark, SOTA, production automation, unrestricted autonomy, or model-quality claims.
- Do not add new runtime behavior, model training, ASR/TTS evaluation, remote GPU jobs, public raw artifacts, or broad public-web automation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `demo-evidence-set`: Extend the public/reviewer evidence contract with a final closeout handoff pack, interview briefing, validation snapshot, and privacy-safe reviewer checklist.

## Impact

- Affects docs, generated/static interview artifact, README/demo references, tests, OpenSpec artifacts, and final verification workflow.
- Does not change the Operator Console runtime, browser executor, visual grounding dependency boundary, ASR adapters, normalizer/validator behavior, trace schema, or Speech-to-Task dataset builder except for documentation references if needed.
