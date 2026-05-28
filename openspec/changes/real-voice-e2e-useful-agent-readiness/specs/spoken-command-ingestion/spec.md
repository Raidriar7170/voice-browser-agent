## ADDED Requirements

### Requirement: Prove real audio command smoke path
The system SHALL provide a local real audio smoke workflow that starts from an uploaded or recorded audio command, transcribes it through a configured ASR adapter, and records sanitized transcript metadata for one bounded execution.

#### Scenario: Real audio smoke succeeds
- **WHEN** the real audio smoke workflow receives a supported audio command and an ASR adapter returns a transcript
- **THEN** the resulting trace records an audio-based input source, ASR adapter name, transcript text, input audio identifier, language mode, confidence or diagnostics when available, and no raw audio storage path

#### Scenario: Real audio smoke has no ASR backend
- **WHEN** no primary ASR endpoint is configured and the fallback ASR dependency is unavailable
- **THEN** the workflow fails or records an unavailable-ASR failure trace with a clear reason instead of producing successful real voice evidence

### Requirement: Report local real-use readiness
The system SHALL provide readiness checks for real audio execution prerequisites.

#### Scenario: Preflight reports ASR readiness
- **WHEN** the preflight command or readiness API runs
- **THEN** it reports whether a primary ASR endpoint is configured, whether fallback ASR can be imported, which fallback model is configured, and what action is needed when neither is available

#### Scenario: Preflight preserves privacy
- **WHEN** preflight reports runtime paths
- **THEN** it reports only relative or category-level paths for uploads, traces, and ignored runtime artifacts without exposing raw audio file names, local file URIs, credentials, or remote host details

### Requirement: Preserve edited transcript provenance
The system SHALL distinguish original ASR output from operator-edited transcript text before normalization.

#### Scenario: Operator edits ASR transcript
- **WHEN** an operator edits the ASR transcript before execution
- **THEN** the trace records the edited transcript as the normalized input and preserves metadata showing the original ASR adapter, original transcript text, edit status, and audio input source without exposing raw audio paths
