## ADDED Requirements

### Requirement: Record real browser-use-vision controlled evidence
The system SHALL provide a controlled execution evidence path that invokes `browser-use-vision` visual grounding functionality through the installed package dependency boundary and records a sanitized Execution Trace.

#### Scenario: Real visual grounding path runs on controlled page
- **WHEN** a selected controlled visual task is executed in real-vision controlled mode
- **THEN** the system invokes `browser-use-vision` visual grounding code and records evidence mode, provider metadata, adapter metadata, grounding references, final status, and failure or stop reason when present

#### Scenario: Real visual evidence is separated from deterministic evidence
- **WHEN** the real-vision controlled trace is exported as a public artifact
- **THEN** its file path or metadata distinguishes it from demo-preview, deterministic live-controlled, and deterministic agentic live-controlled traces

### Requirement: Gate real-vision evidence honesty
The system SHALL NOT count deterministic controlled adapter output as real `browser-use-vision` visual grounding evidence.

#### Scenario: browser-use-vision entry point is unavailable
- **WHEN** the installed `browser-use-vision` package or required visual grounding entry point cannot be imported or invoked
- **THEN** the real-vision evidence workflow fails or marks the trace unavailable with a clear reason instead of producing passing real-vision evidence

#### Scenario: Visual grounding produces no meaningful evidence
- **WHEN** real-vision controlled mode returns no provider metadata, no grounding references, and no visual evidence summary
- **THEN** the system marks the run as failed or unavailable instead of counting it as real-vision evidence

### Requirement: Preserve privacy in real-vision controlled traces
The system SHALL export only sanitized real-vision controlled traces.

#### Scenario: Real-vision trace is committed or packaged
- **WHEN** a real-vision controlled trace is included in committed evidence or a release pack
- **THEN** it excludes raw screenshots, raw audio, browser profile data, cookies, credentials, private URLs, remote host details, absolute local file URIs, and unsanitized runtime state
