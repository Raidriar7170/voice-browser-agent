## 1. Real Voice Contract Tests

- [x] 1.1 Add failing tests for a `real_voice_controlled` evidence mode and sanitized trace directory.
- [x] 1.2 Add tests that real voice traces prove audio-based input source, ASR adapter metadata, transcript provenance, reviewed transcript status, browser action evidence, and privacy-scan status.
- [x] 1.3 Add tests that fixture-only or transcript-only inputs cannot be mislabeled as real voice evidence.
- [x] 1.4 Add tests that unavailable ASR produces a clear failure or unavailable evidence trace instead of successful real voice evidence.

## 2. Real Voice E2E Smoke Workflow

- [x] 2.1 Implement a local real voice smoke generator with injectable ASR output for deterministic tests and real ASR adapter use when configured.
- [x] 2.2 Generate at least one committed sanitized `real_voice_controlled` trace for `icon-search` under a distinct real voice trace directory.
- [x] 2.3 Record original ASR transcript, reviewed transcript, adapter metadata, edit status, and audio input source without raw audio paths.
- [x] 2.4 Update trace privacy scans to cover real voice traces and reject raw audio paths, local file URIs, remote host details, credentials, cookies, browser profiles, and raw screenshots.

## 3. Local Readiness / Preflight

- [x] 3.1 Add tests for preflight reporting ASR readiness, fallback ASR availability, browser automation readiness, real visual grounding readiness, runtime privacy status, and recommended setup actions.
- [x] 3.2 Implement a preflight module and CLI script for real-use readiness.
- [x] 3.3 Add a readiness API endpoint that returns the same sanitized readiness categories to the Operator Console.
- [x] 3.4 Ensure preflight output avoids raw file names, local file URIs, credentials, private URLs, and remote host details.

## 4. ASR Review and Correction UX

- [x] 4.1 Add API tests for transcribing uploaded/recorded audio without immediate execution.
- [x] 4.2 Add API support for executing an audio command with reviewed transcript text and transcript provenance.
- [x] 4.3 Add Operator Console controls for ASR transcript review, editable transcript text, normalize-preview, and execute-reviewed-audio.
- [x] 4.4 Add UI tests that audio execution remains distinct from transcript and fixture execution and displays ASR unavailable failures clearly.

## 5. Useful Local Scenario Pack

- [x] 5.1 Add tests requiring useful local scenario documentation and controlled scenario metadata.
- [x] 5.2 Add or extend local controlled pages for CRM/settings/dashboard-style useful scenarios without credentials or external network dependencies.
- [x] 5.3 Add scenario fixtures or metadata for at least three useful local tasks with intent type, safety behavior, and privacy boundary.
- [x] 5.4 Document why useful scenarios remain controlled local workflows instead of broad public-web automation.

## 6. Failure and Usage Evidence

- [x] 6.1 Add tests requiring sanitized failure/usage traces for ASR unavailable, clarification required, confirmation pending/cancelled, ambiguous visual target, and successful real voice controlled execution.
- [x] 6.2 Generate committed sanitized failure/usage traces under a distinct directory or evidence mode classification.
- [x] 6.3 Update release-pack manifest and HTML generation to classify real voice, useful scenario, and failure/usage traces with privacy-scan status.
- [x] 6.4 Update public evidence docs to frame failures as reliability evidence, not benchmark scores or production automation claims.

## 7. Documentation and OpenSpec Integration

- [x] 7.1 Update README quickstart with real-use setup, preflight, real audio flow, and ASR configuration expectations.
- [x] 7.2 Update public evidence page, demo media plan, interview overview, and closeout checklist with real voice E2E and preflight usage.
- [x] 7.3 Update `CONTEXT.md` coverage matrix for real voice evidence, preflight, transcript review, useful scenarios, and failure/usage traces.
- [x] 7.4 Update main OpenSpec specs so archived requirements stay aligned with the new real-use behavior.

## 8. Verification

- [x] 8.1 Run targeted tests for real voice smoke, preflight, ASR review UX, useful scenarios, release-pack classification, and failure/usage traces.
- [x] 8.2 Run `uv run python scripts/preflight_real_use.py`.
- [x] 8.3 Run `uv run python scripts/generate_real_voice_trace.py`.
- [x] 8.4 Run `uv run python scripts/build_demo_evidence_pack.py`.
- [x] 8.5 Run `openspec validate real-voice-e2e-useful-agent-readiness --strict`.
- [x] 8.6 Run `openspec validate --all --strict`.
- [x] 8.7 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 8.8 Run `git diff --check`.
- [x] 8.9 Run `git status --short --ignored` and confirm raw runtime artifacts remain ignored.
