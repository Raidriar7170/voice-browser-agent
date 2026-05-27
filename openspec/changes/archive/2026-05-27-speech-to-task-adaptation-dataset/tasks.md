## 1. Dataset Contract Tests

- [x] 1.1 Add tests that build a dataset from sanitized preview, live-controlled, and agentic trace directories.
- [x] 1.2 Add tests for stable example ids, source execution ids, source trace paths, evidence modes, final statuses, validator outcomes, safety flags, and privacy-scan status in the manifest.
- [x] 1.3 Add tests that the JSONL export includes transcript inputs, normalized targets, validator decisions, final statuses, language metadata, and correction status.

## 2. Privacy and Quality Gates

- [x] 2.1 Add tests for traces missing transcript or normalized output and assert the dataset workflow fails with the source trace named.
- [x] 2.2 Add tests for duplicate stable example ids and malformed or unknown correction overlay entries.
- [x] 2.3 Add tests that private markers in source traces, correction overlays, generated manifests, or JSONL examples fail the workflow.

## 3. Dataset Builder

- [x] 3.1 Implement a local dataset builder script that reads checked-in sanitized trace directories and writes generated artifacts under a local runtime directory.
- [x] 3.2 Generate a dataset manifest with generated timestamp, source directories or optional release-pack manifest path, example count, evidence-mode counts, correction count, privacy-scan status, and per-example provenance.
- [x] 3.3 Generate adaptation-ready JSONL examples with stable ids, input payloads, original target outputs, active target outputs, validator decisions, final statuses, safety flags, and correction metadata.
- [x] 3.4 Support an optional human correction overlay without mutating source traces or silently replacing original trace-derived targets.
- [x] 3.5 Reuse existing trace sanitization/privacy scanning patterns where possible and keep all generated dataset files local.

## 4. Documentation and Positioning

- [x] 4.1 Document the dataset build command, generated output paths, optional correction overlay format, and reviewer inspection path.
- [x] 4.2 Document that the dataset is local Speech-to-Task adaptation preparation evidence, not an ASR/TTS corpus, benchmark leaderboard, model checkpoint, production automation dataset, or unrestricted public-web autonomy claim.
- [x] 4.3 Add or update wording guards so README/demo docs avoid benchmark, SOTA, production automation, and unrestricted autonomy framing for the dataset.

## 5. Verification

- [x] 5.1 Run targeted trace-derived training example and dataset-builder tests.
- [x] 5.2 Run the dataset builder and inspect the generated manifest and JSONL output.
- [x] 5.3 Run `openspec validate speech-to-task-adaptation-dataset --strict`.
- [x] 5.4 Run `openspec validate --all --strict`.
- [x] 5.5 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 5.6 Check `git status --short --ignored` and confirm no private runtime artifacts are staged.
