## ADDED Requirements

### Requirement: Include visual verification loop evidence
The evidence set SHALL include sanitized visual verification loop evidence for selected controlled visual-grounding-heavy tasks.

#### Scenario: Visual verification trace is committed
- **WHEN** a selected controlled visual task has agentic trace evidence
- **THEN** at least one committed sanitized trace records post-action visual verification outcome, expected condition, observed state summary, reason text, recovery or stop decision, and sanitized evidence references

#### Scenario: Visual verification failure is committed
- **WHEN** the evidence set demonstrates a no-effect action, uncertain visual state, ambiguous target, or unrecovered visual mismatch
- **THEN** the committed sanitized trace records the failed or uncertain verification result and does not report the task as successfully verified

### Requirement: Summarize visual verification in release pack
The release pack SHALL summarize visual verification outcomes in the manifest and browser-readable HTML index.

#### Scenario: Release pack includes verification evidence
- **WHEN** the release-pack workflow collects an agentic trace with visual verification results
- **THEN** the manifest records verification outcome counts, verified fixture ids, recovery count, failed or uncertain reason summary, privacy-scan status, and source trace paths

#### Scenario: Reviewer opens release-pack index
- **WHEN** a reviewer opens the generated release-pack HTML index locally
- **THEN** they can identify which visual tasks were verified, which failed or remained uncertain, and what recovery or stop decision occurred without inspecting raw trace JSON

### Requirement: Gate visual verification privacy in evidence artifacts
The evidence workflow SHALL reject visual verification artifacts that expose raw visual data or provider-private data.

#### Scenario: Private verification marker is detected
- **WHEN** a trace, manifest, or generated evidence page contains raw screenshots, raw annotated images, raw provider prompts, raw provider responses, request headers, API keys, credentials, cookies, browser profile data, private URLs, local file URIs, remote host details, or unsanitized runtime fields
- **THEN** the workflow exits non-zero and does not present the visual verification evidence as public-safe

### Requirement: Document visual verification positioning
The project SHALL document visual verification evidence as bounded controlled-task reliability evidence rather than model-quality, benchmark, production automation, or broad autonomy evidence.

#### Scenario: Reviewer reads public evidence docs
- **WHEN** public evidence documentation describes visual verification loop evidence
- **THEN** it states that the default path is controlled and keyless, real VLM/provider verification is optional and local/private, and the evidence does not claim benchmark ranking, SOTA, production automation, unrestricted public-web autonomy, or model fine-tuning
