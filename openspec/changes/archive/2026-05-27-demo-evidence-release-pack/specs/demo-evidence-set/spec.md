## ADDED Requirements

### Requirement: Build reproducible demo evidence release pack
The project SHALL provide a local workflow that builds a reproducible demo evidence release pack from sanitized demo artifacts.

#### Scenario: Release pack is generated
- **WHEN** the evidence pack workflow is run from the project checkout
- **THEN** it creates a release directory containing a manifest, browser-openable HTML index, and references or copies of selected sanitized trace artifacts

#### Scenario: Release pack uses sanitized sources
- **WHEN** the workflow collects trace artifacts
- **THEN** it uses only checked-in sanitized preview, live-controlled, or agentic trace sources and does not include raw recordings, raw screenshots, browser profiles, credentials, private URLs, remote host details, or unsanitized runtime traces

### Requirement: Emit evidence manifest
The release pack SHALL include a machine-readable manifest that summarizes every included trace artifact.

#### Scenario: Trace row is recorded
- **WHEN** a trace is included in the release pack
- **THEN** the manifest records fixture id, evidence mode, source path, final status, stop reason or failure reason when present, grounding evidence references, agentic step count, and privacy-scan result

#### Scenario: Evidence mode is classified
- **WHEN** the manifest describes preview, live-controlled, or agentic trace artifacts
- **THEN** it classifies them as `demo_preview`, `live_controlled`, or `agentic_live_controlled` without relying only on the trace `execution_mode` field

### Requirement: Provide reviewer-readable HTML evidence index
The release pack SHALL include a browser-openable HTML index generated from the evidence manifest.

#### Scenario: Reviewer opens index
- **WHEN** a reviewer opens the generated HTML index locally
- **THEN** they can identify the included fixtures, evidence modes, final statuses, stop or failure reasons, trace paths, and privacy-scan status without running the Operator Console

#### Scenario: HTML preserves bounded positioning
- **WHEN** the HTML index describes the release pack
- **THEN** it presents the project as a bounded demo evidence pack and avoids benchmark, SOTA, production automation, or unrestricted public-web autonomy claims

### Requirement: Gate release pack completeness and privacy
The release pack workflow SHALL fail when required evidence is missing, ambiguous, malformed, or privacy-unsafe.

#### Scenario: Required evidence is missing
- **WHEN** the sanitized preview traces do not cover the demo task suite or selected live/agentic trace groups do not cover the required controlled visual fixtures
- **THEN** the workflow exits non-zero with a clear reason naming the missing fixture or evidence mode

#### Scenario: Private marker is detected
- **WHEN** a candidate trace or generated release artifact contains raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, local file URIs, or unsanitized runtime fields
- **THEN** the workflow exits non-zero and does not present the release pack as public-ready
