## ADDED Requirements

### Requirement: Normalize reviewed ASR transcript text
The normalizer SHALL accept operator-reviewed transcript text while preserving the original ASR provenance in the Execution Trace.

#### Scenario: Reviewed transcript differs from ASR output
- **WHEN** the operator edits the ASR transcript before normalization
- **THEN** the normalized Browser Task Request or Clarification Request is based on the reviewed transcript while the trace preserves original ASR text, edited text, edit status, and adapter metadata

### Requirement: Clarify uncertain real audio commands
The normalizer and validator SHALL prefer clarification over execution when real audio-derived transcript text is ambiguous or low-confidence.

#### Scenario: Real audio command is ambiguous
- **WHEN** an audio-derived reviewed transcript cannot be mapped to one bounded Browser Task Request
- **THEN** the system produces a Clarification Request and records the audio input source and transcript provenance without launching browser execution
