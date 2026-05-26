## ADDED Requirements

### Requirement: Preserve adaptation-ready transcript source data
The system SHALL preserve transcript source metadata needed by trace-derived Speech-to-Task examples while keeping raw audio outside public artifacts.

#### Scenario: Transcript is used for training example derivation
- **WHEN** a Trace-Derived Training Example is created
- **THEN** the transcript metadata identifies the adapter, input audio identifier, language mode, timestamp, and diagnostics without exposing raw audio storage paths
