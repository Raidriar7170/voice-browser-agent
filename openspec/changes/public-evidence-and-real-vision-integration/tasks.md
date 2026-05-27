## 1. Real Vision Evidence Contract

- [x] 1.1 Add failing tests for a `real_vision_controlled` evidence mode and sanitized trace directory.
- [x] 1.2 Add tests proving the real-vision path imports and invokes `browser-use-vision` visual grounding functionality rather than the deterministic controlled adapter.
- [x] 1.3 Add tests that real-vision traces include provider metadata, adapter metadata, grounding references, final status, and privacy-scan status.
- [x] 1.4 Add tests that unavailable `browser-use-vision` entry points or empty visual evidence fail with a clear unavailable/missing-evidence reason.

## 2. Real Vision Controlled Trace

- [x] 2.1 Inspect the local `browser-use-vision` APIs and choose the most stable controlled target, such as `icon-search` or `color-swatch`.
- [x] 2.2 Implement a narrow real-vision controlled adapter or generation script that exercises `browser-use-vision` visual grounding code on the selected controlled page.
- [x] 2.3 Generate at least one sanitized real-vision controlled trace under a path distinct from preview, live-controlled, and agentic traces.
- [x] 2.4 Update trace sanitization/privacy checks so real-vision traces exclude raw screenshots, local file URIs, browser profile data, credentials, private URLs, remote host details, and unsanitized runtime state.

## 3. Public Evidence Page and Demo Media Contract

- [x] 3.1 Add tests requiring a static public evidence page to reference the standalone project scope, evidence modes, sanitized trace directories, release-pack workflow, seed-set workflow, validation commands, limitations, and demo media contract.
- [x] 3.2 Create a committed sanitized public evidence page, for example under `docs/public-evidence/`, that can be opened locally or hosted statically.
- [x] 3.3 Update release-pack manifest and HTML generation to classify real-vision controlled traces separately and expose provider metadata.
- [x] 3.4 Add a 60-90 second demo video/GIF artifact contract with exact storyboard steps, fixture ids, trace/export expectations, and privacy requirements.
- [x] 3.5 Add or update wording guards so public evidence and demo media docs avoid benchmark, SOTA, production automation, unrestricted autonomy, model-quality, and checkpoint claims.

## 4. Speech-to-Task Seed Set

- [x] 4.1 Add tests for a seed-set workflow that outputs 20-50 examples with manifest counts and per-example provenance.
- [x] 4.2 Extend the dataset workflow or add a companion seed-set builder to include original trace-derived examples plus reviewed correction or variant overlays.
- [x] 4.3 Add a small committed correction or variant overlay example that preserves original targets and records overlay reasons/status.
- [x] 4.4 Update dataset privacy/quality gates to scan overlays, generated seed manifests, and generated example streams.
- [x] 4.5 Document the seed set as local Speech-to-Task adaptation preparation evidence, not training, checkpoint publication, ASR/TTS evaluation, or broad public-web automation.

## 5. Integration and Handoff

- [x] 5.1 Update README, demo docs, interview overview, closeout checklist, and `CONTEXT.md` coverage matrix to include real-vision evidence, public evidence page, demo media contract, and seed set.
- [x] 5.2 Update OpenSpec specs and archive/readiness notes so this change remains separate from the already-complete closeout handoff.
- [x] 5.3 Rebuild release-pack and seed-set runtime artifacts locally and inspect generated manifests for expected counts, evidence modes, and privacy-scan status.
- [x] 5.4 Confirm generated runtime artifacts, media outputs, caches, raw recordings, raw screenshots, browser profiles, and private traces remain ignored unless an explicitly sanitized public artifact is intentionally committed.

## 6. Verification

- [x] 6.1 Run targeted tests for real-vision evidence, release-pack classification, public evidence page, demo media contract, and seed-set generation.
- [x] 6.2 Run `openspec validate public-evidence-and-real-vision-integration --strict`.
- [x] 6.3 Run `openspec validate --all --strict`.
- [x] 6.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 6.5 Run `git diff --check`.
- [x] 6.6 Run `git status --short --ignored` and confirm no private runtime artifacts are staged.
