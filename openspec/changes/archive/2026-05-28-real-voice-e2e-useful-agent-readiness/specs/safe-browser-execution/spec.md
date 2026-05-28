## ADDED Requirements

### Requirement: Execute real audio-derived controlled requests safely
The system SHALL route real audio-derived Browser Task Requests through the same validation, confirmation, stop-condition, and controlled execution boundaries used by fixture and transcript requests.

#### Scenario: Real voice controlled execution succeeds
- **WHEN** an audio-derived transcript normalizes to a supported controlled visual task and passes validation without pending confirmation
- **THEN** the system executes only the selected controlled local page, records `real_voice_controlled` evidence metadata, browser action evidence, grounding references, final status, and sanitized runtime metadata

#### Scenario: Real voice controlled execution requires confirmation
- **WHEN** an audio-derived transcript normalizes to a safety-sensitive Browser Task Request
- **THEN** the system pauses at the Confirmation Gate and records the pending confirmation state before any browser action is executed

### Requirement: Reject unsafe real voice execution shortcuts
The system SHALL NOT treat fixture transcripts, direct text input, or unchecked ASR output as successful real voice evidence.

#### Scenario: Fixture is mislabeled as real voice
- **WHEN** evidence generation attempts to mark fixture-only or transcript-only input as `real_voice_controlled`
- **THEN** the workflow fails with a clear source-mismatch reason

#### Scenario: Unreviewed low-confidence ASR is unsafe
- **WHEN** ASR metadata reports low confidence or an unavailable diagnostic and the operator has not reviewed the transcript
- **THEN** the system requires transcript review or produces a clarification/failure trace instead of executing blindly
