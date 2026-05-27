## 1. Release Pack Contract

- [x] 1.1 Add tests for release-pack manifest generation from sanitized preview, live-controlled, and agentic trace directories.
- [x] 1.2 Add tests for evidence mode classification: `demo_preview`, `live_controlled`, and `agentic_live_controlled`.
- [x] 1.3 Add tests for missing required fixture coverage and malformed trace failures.

## 2. Privacy and Completeness Gates

- [x] 2.1 Add tests that inject private markers into candidate traces and assert the release-pack workflow fails.
- [x] 2.2 Implement reusable privacy scanning for trace payloads and generated release-pack files.
- [x] 2.3 Implement completeness checks for all demo-preview fixtures and required selected live/agentic controlled visual fixtures.

## 3. Evidence Pack Builder

- [x] 3.1 Implement `scripts/build_demo_evidence_pack.py` to build a local release directory from existing sanitized trace artifacts.
- [x] 3.2 Generate `manifest.json` with fixture id, evidence mode, source path, final status, stop/failure reason, grounding refs, agentic step count, and privacy-scan status.
- [x] 3.3 Generate a browser-openable `index.html` from the manifest without benchmark, SOTA, production automation, or unrestricted autonomy wording.
- [x] 3.4 Ensure the builder exits non-zero with clear errors when evidence is missing, ambiguous, malformed, or privacy-unsafe.

## 4. Documentation and Handoff

- [x] 4.1 Update README and demo docs with the evidence-pack build command and reviewer walkthrough path.
- [x] 4.2 Document which generated output directories are local artifacts and which sanitized trace sources remain committed evidence.
- [x] 4.3 Add or update tests that guard the release-pack docs against benchmark/SOTA/unrestricted-autonomy positioning.

## 5. Verification

- [x] 5.1 Run targeted release-pack tests.
- [x] 5.2 Run the release-pack builder and inspect the generated manifest and HTML index.
- [x] 5.3 Run `openspec validate demo-evidence-release-pack --strict`.
- [x] 5.4 Run `openspec validate --all --strict`.
- [x] 5.5 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 5.6 Check `git status --short --ignored` and confirm no private runtime artifacts are staged.
