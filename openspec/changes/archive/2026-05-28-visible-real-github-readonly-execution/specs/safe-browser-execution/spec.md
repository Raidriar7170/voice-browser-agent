## ADDED Requirements

### Requirement: Capture local visual evidence for public-readonly execution
The public-readonly executor SHALL capture local/private visual artifacts for real public tasks when visual result capture is enabled.

#### Scenario: Public task step screenshot is captured
- **WHEN** a public-readonly task completes a meaningful navigation, search, read, or stop step
- **THEN** the executor records a screenshot artifact reference, page title, sanitized origin, action type, completion state, and local/private privacy state in the trace runtime metadata

#### Scenario: Public task final screenshot is captured
- **WHEN** a public-readonly task finishes, stops, fails, or is blocked after navigation
- **THEN** the executor records a final visual result artifact that the local Operator Console can display without embedding raw screenshot bytes in exported public trace JSON

### Requirement: Preserve isolation for visible public browser runs
The executor SHALL preserve public-readonly isolation even when the operator enables a visible headed browser debug mode.

#### Scenario: Headed public browser mode is enabled
- **WHEN** the operator configures public-readonly execution to use a visible local browser window
- **THEN** the executor still launches a fresh ephemeral browser context with no persistent user profile, no reused cookies, no stored credentials, and the same read-only action policy

#### Scenario: Headed public browser mode is disabled
- **WHEN** headed browser mode is not configured
- **THEN** the executor may run headless while still capturing local/private visual artifacts for the Operator Console

### Requirement: Protect local visual artifacts from public export
The system SHALL prevent local public-readonly visual artifacts from being treated as public-safe evidence unless sanitizer approval is explicit.

#### Scenario: Public visual artifact is in local runtime
- **WHEN** a trace references public-readonly visual artifacts under the local runtime directory
- **THEN** sanitized API responses expose only guarded local artifact references and metadata needed by the local console

#### Scenario: Public visual artifact fails sanitizer checks
- **WHEN** an export workflow sees raw screenshots, raw page text, private URLs, cookies, credentials, browser profile paths, local file URIs, or remote host details in a public-readonly visual artifact
- **THEN** the export fails or marks the trace local/private and does not present the artifact as public-ready
