# spoken-command-ingestion Specification

## Purpose
Defines one-utterance spoken command ingestion, ASR adapter behavior, Chinese-first transcript metadata, fallback handling, and raw-audio privacy boundaries for reproducible Spoken Command Executions.
## Requirements
### Requirement: Accept one spoken command audio input
The system SHALL accept one recorded or uploaded audio clip as the input for one Spoken Command Execution.

#### Scenario: Uploaded audio fixture is accepted
- **WHEN** the operator uploads a supported audio file for a demo task
- **THEN** the system creates a new Spoken Command Execution using that audio as the command source

#### Scenario: Browser recording is accepted when available
- **WHEN** the operator records a command through the Operator Console
- **THEN** the system uses the recorded audio clip as the command source for one execution

### Requirement: Transcribe audio through an ASR adapter
The system SHALL convert each spoken command audio clip into a transcript through a replaceable ASR Adapter.

#### Scenario: Primary ASR adapter succeeds
- **WHEN** the Primary ASR Adapter transcribes an audio clip successfully
- **THEN** the system stores the transcript and ASR metadata for normalization

#### Scenario: Primary ASR adapter is unavailable
- **WHEN** the Primary ASR Adapter is unavailable and a Fallback ASR Adapter is configured
- **THEN** the system transcribes the audio through the Fallback ASR Adapter

### Requirement: Preserve transcript metadata
The system SHALL preserve metadata needed to audit the transcript source and support future trace-derived training examples.

#### Scenario: Transcript metadata is recorded
- **WHEN** ASR transcription completes
- **THEN** the transcript record includes adapter name, input audio identifier, language mode, timestamp, and any available confidence or diagnostic metadata

### Requirement: Support Chinese-first command input
The system SHALL support Chinese-first spoken commands with English code-switching for product names, URLs, UI labels, and technical terms.

#### Scenario: Mixed Chinese and English command is transcribed
- **WHEN** the audio contains a Chinese command with English terms such as GitHub, browser-use, or OpenAI
- **THEN** the transcript preserves the mixed-language intent for downstream normalization

### Requirement: Reject unusable audio input
The system SHALL fail fast when audio input cannot be decoded or is missing.

#### Scenario: Unsupported audio file is uploaded
- **WHEN** the operator uploads an unsupported or corrupt audio file
- **THEN** the system returns an ingestion error before calling the normalizer

### Requirement: Preserve adaptation-ready transcript source data
The system SHALL preserve transcript source metadata needed by trace-derived Speech-to-Task examples while keeping raw audio outside public artifacts.

#### Scenario: Transcript is used for training example derivation
- **WHEN** a Trace-Derived Training Example is created
- **THEN** the transcript metadata identifies the adapter, input audio identifier, language mode, timestamp, and diagnostics without exposing raw audio storage paths
