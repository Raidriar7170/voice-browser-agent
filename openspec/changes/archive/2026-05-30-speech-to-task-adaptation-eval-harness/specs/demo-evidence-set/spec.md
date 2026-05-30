## ADDED Requirements

### Requirement: Include adaptation evaluation summary in reviewer handoff
The demo evidence release-pack workflow SHALL include a sanitized Speech-to-Task adaptation evaluation summary when a local evaluation manifest is provided.

#### Scenario: Evaluation manifest is provided
- **WHEN** the release-pack workflow is run with a Speech-to-Task adaptation evaluation manifest path
- **THEN** the generated release-pack manifest and HTML index include split counts, candidate modes, high-level metric summaries, failure-slice summaries, source manifest path, privacy-scan status, and local/private positioning

#### Scenario: Evaluation manifest is absent
- **WHEN** the release-pack workflow runs without an adaptation evaluation manifest
- **THEN** the release pack remains valid and does not imply that adaptation evaluation has been run

### Requirement: Reject unsafe adaptation evaluation evidence
The evidence workflow SHALL reject adaptation evaluation artifacts that expose private data, raw provider data, or model-training artifacts.

#### Scenario: Unsafe evaluation evidence is detected
- **WHEN** an evaluation manifest, generated release-pack manifest, or generated evidence page contains raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, local file URIs, raw prompts, raw provider responses, request headers, API keys, remote host details, checkpoint paths, or unsanitized runtime fields
- **THEN** the release-pack workflow exits non-zero or excludes the unsafe adaptation evaluation summary before presenting the pack as privacy-scan passed

### Requirement: Preserve adaptation evaluation non-benchmark framing
The reviewer handoff SHALL describe adaptation evaluation as bounded local evidence rather than a benchmark leaderboard, model-quality result, ASR/TTS evaluation, or production automation claim.

#### Scenario: Reviewer inspects release-pack adaptation evaluation section
- **WHEN** the generated release-pack index describes Speech-to-Task adaptation evaluation
- **THEN** it states that the results come from a small local sanitized seed set and do not claim benchmark ranking, SOTA, production readiness, unrestricted public-web autonomy, ASR/TTS quality, or model fine-tuning completion
