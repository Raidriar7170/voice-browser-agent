# operator-task-routing Specification

## Purpose
Defines deterministic command routing after normalization and validation, including controlled local targets, preview-only outcomes, clarification and blocked states, audio transcript provenance, and route evidence recorded for the Operator Console.
## Requirements
### Requirement: Select an execution route for each command
The system SHALL select an explicit execution route after normalization and validation and before browser execution.

#### Scenario: Command maps to controlled live task
- **WHEN** a validated Browser Task Request matches a supported controlled local target
- **THEN** the route decision identifies the controlled fixture id, target reference, execution mode, route reason, and user-visible explanation

#### Scenario: Command is preview-only
- **WHEN** a validated Browser Task Request describes a public showcase or unsupported live task that is not selected for controlled live execution
- **THEN** the route decision keeps the request in demo-preview mode and explains that no live browser action will be claimed

#### Scenario: Command requires clarification
- **WHEN** normalization produces a Clarification Request
- **THEN** the route decision prevents browser execution and preserves the clarification reason for the Operator Console

### Requirement: Route reviewed audio and typed transcript consistently
The system SHALL use the same route-selection rules for typed transcript commands and operator-reviewed audio transcripts.

#### Scenario: Reviewed audio matches controlled task
- **WHEN** reviewed audio transcript text maps to a supported controlled task and passes validation
- **THEN** the selected route uses the controlled target while preserving audio input and transcript-review provenance

#### Scenario: Typed transcript matches same controlled task
- **WHEN** typed transcript text maps to the same supported controlled task and passes validation
- **THEN** the selected route uses the same controlled target without requiring manual fixture or execution-mode dropdown selection

### Requirement: Preserve route decision evidence
The system SHALL record route decisions in the execution response or trace metadata.

#### Scenario: Route is selected
- **WHEN** a route decision is made for an execution attempt
- **THEN** the response includes route type, selected target when present, route reason, supported execution mode, and whether the result may be treated as live evidence

#### Scenario: Route is unsupported
- **WHEN** the command cannot be executed live under current safety and readiness boundaries
- **THEN** the response includes a user-visible unsupported-route explanation without presenting the run as successful live browser execution

### Requirement: Keep route selection deterministic and bounded
The system SHALL route only to bounded Browser Intent Types and configured targets.

#### Scenario: Command asks for broad web autonomy
- **WHEN** a command requires unrestricted browsing, login completion, posting, purchasing, deletion, private-data entry, or long-horizon planning
- **THEN** the route selector returns clarification, confirmation, blocked, or preview-only state instead of selecting live execution

### Requirement: Route allowlisted public commands to public-readonly execution
The system SHALL select a public-readonly route only when a validated Browser Task Request maps to an allowlisted public target and public-readonly execution is enabled.

#### Scenario: Allowlisted public command is routed
- **WHEN** a validated command targets an allowlisted public documentation, search, or read-only information page
- **THEN** the route decision identifies `live_public_readonly`, the sanitized target label, the route reason, execution limits, private evidence state, and user-visible explanation

#### Scenario: Public-readonly is disabled
- **WHEN** a public command would otherwise match a public-readonly target but public-readonly is disabled
- **THEN** the route decision keeps the command in controlled-showcase, demo-preview, or unsupported-route state and explains that public-readonly is disabled

### Requirement: Prevent public-readonly override bypass
The system SHALL prevent manual execution-mode, fixture, or client-side overrides from forcing public-readonly execution outside route policy.

#### Scenario: Manual override requests public-readonly for non-allowlisted target
- **WHEN** a request includes a public-readonly execution override for a non-allowlisted or unsafe target
- **THEN** the route selector returns blocked or preview-only output and records the unsupported-route reason

#### Scenario: Unsafe command requests public-readonly
- **WHEN** a command requires login, posting, purchasing, deletion, upload, download, private-data entry, or long-horizon browsing
- **THEN** the route selector returns clarification, confirmation, blocked, or preview-only state instead of public-readonly execution

### Requirement: Preserve public-readonly route evidence
The system SHALL record enough route evidence to audit why a public command did or did not execute.

#### Scenario: Public-readonly route is selected
- **WHEN** route selection chooses public-readonly execution
- **THEN** the response and trace include route type, execution mode, target label, sanitized origin, allowlist id, route reason, evidence privacy state, and live evidence eligibility

#### Scenario: Public command is unsupported
- **WHEN** route selection rejects public-readonly execution
- **THEN** the response and trace include a user-visible explanation without claiming live public webpage operation

### Requirement: Route public commands to task contracts
The system SHALL select public-readonly execution only when a validated command maps to a configured public task contract.

#### Scenario: Public command matches task contract
- **WHEN** a validated Browser Task Request includes supported public task slots and matches a configured public task contract
- **THEN** the route decision records route type, execution mode, task id, task kind, target label, sanitized origin, allowlist id, execution limits, route reason, and private evidence state

#### Scenario: Public command lacks matching task contract
- **WHEN** a public command mentions an allowlisted site but requests a task kind, query, extraction target, or navigation path outside configured task contracts
- **THEN** route selection returns blocked, clarification, controlled-showcase, or demo-preview output without launching a public browser session

### Requirement: Preserve public task slot provenance
The route decision SHALL preserve safe public task slots needed by the executor and completion verifier.

#### Scenario: Search task is routed
- **WHEN** a command asks to search an allowlisted public documentation site
- **THEN** the route decision includes the target task id, normalized search query, read-only intent, and completion criteria identifier without accepting arbitrary transcript-emitted URLs

#### Scenario: Extraction task is routed
- **WHEN** a command asks to read or extract visible information from an allowlisted public page
- **THEN** the route decision includes the read target or extraction target needed to verify completion

### Requirement: Reject unsafe public route shortcuts
The route selector SHALL reject manual overrides or transcript tricks that would bypass public task policy.

#### Scenario: Manual public mode override lacks task contract
- **WHEN** a request manually selects public-readonly execution but no configured public task contract matches the normalized command
- **THEN** the route selector blocks live public execution and records a public task contract mismatch reason

#### Scenario: Transcript includes unsafe URL alongside public keyword
- **WHEN** a transcript contains a non-allowlisted, private-network, credential-bearing, unsafe-protocol, or mixed public/private URL while also mentioning an allowlisted public target
- **THEN** the route selector rejects live public execution and records the unsafe target reason

### Requirement: Prefer configured real GitHub public-readonly routes
The route selector SHALL route supported GitHub commands to real public-readonly execution only when public-readonly is enabled and a matching GitHub task contract exists.

#### Scenario: GitHub repository search route is selected
- **WHEN** a validated command asks to search public GitHub repositories and a matching `github-repo-search` task contract is configured
- **THEN** the route decision records `public_readonly`, `live_public_readonly`, GitHub target label, sanitized `https://github.com` origin, allowlist id, public task id, task kind, normalized search query, completion criteria id, execution limits, and local/private evidence state

#### Scenario: GitHub public repository read route is selected
- **WHEN** a validated command asks to read a specific public GitHub repository page and a matching `github-public-repo-read` task contract is configured
- **THEN** the route decision records the owner/repository slots, GitHub task id, task kind, sanitized origin, completion criteria id, execution limits, and local/private evidence state

### Requirement: Preserve controlled GitHub fallback when real execution is unavailable
The route selector SHALL preserve existing controlled showcase or preview behavior for GitHub-shaped commands when real GitHub public-readonly execution is not explicitly available.

#### Scenario: GitHub public-readonly is disabled
- **WHEN** a GitHub-shaped command would match a real GitHub task but public-readonly is disabled
- **THEN** the route decision selects the controlled GitHub showcase, demo-preview, clarification, or blocked state and explains that real GitHub public-readonly execution is disabled

#### Scenario: GitHub command is unsupported by task contract
- **WHEN** a GitHub-shaped command asks for broad browsing, account state, mutation, or a task outside configured GitHub contracts
- **THEN** the route decision does not launch a real GitHub browser session and records an unsupported GitHub task or safety reason

### Requirement: Reject GitHub route bypasses
The route selector SHALL reject attempts to force GitHub public-readonly execution outside configured task and safety policy.

#### Scenario: Manual override lacks GitHub task contract
- **WHEN** a request manually asks for `live_public_readonly` on GitHub but no configured GitHub task contract matches the normalized command
- **THEN** the system blocks the route before navigation and records a public task contract mismatch reason

#### Scenario: Transcript mixes GitHub with unsafe URL
- **WHEN** a transcript mentions GitHub but also includes a private-network, credential-bearing, non-HTTP(S), non-allowlisted, or mixed-origin URL
- **THEN** the system rejects real GitHub public-readonly execution and records the unsafe target reason

### Requirement: Route reliability smoke tasks by explicit contract
The route selector SHALL route public-readonly reliability tasks only when a validated Browser Task Request matches an enabled allowlisted task contract.

#### Scenario: Documentation task matches contract
- **WHEN** a validated command asks for an allowlisted documentation, reference, or repository read-only task that matches a configured reliability smoke contract
- **THEN** the route decision records public-readonly route type, execution mode, task id, task kind, target class, target label, sanitized origin, allowlist id, completion criteria id, execution limits, private evidence state, and route reason

#### Scenario: Command lacks matching reliability contract
- **WHEN** a public command mentions an allowlisted site but requests a task kind, query, extraction target, account action, or navigation path outside the configured reliability contracts
- **THEN** route selection returns blocked, clarification, controlled-showcase, or demo-preview output without launching a public browser session

### Requirement: Preserve reliability route audit fields
The route decision SHALL preserve enough fields to explain why a public command became a matrix row or was excluded.

#### Scenario: Reliability route is selected
- **WHEN** route selection chooses public-readonly execution for a reliability smoke task
- **THEN** the response and trace include matrix eligibility, task id, target class, route reason, public-readonly enabled state, evidence privacy state, and sanitizer status

#### Scenario: Reliability route is rejected
- **WHEN** route selection rejects a public-readonly reliability task
- **THEN** the response and trace include a user-visible explanation and a stable reason suitable for blocked reliability-matrix reporting

### Requirement: Reject public-readonly reliability bypasses
The route selector SHALL reject manual overrides or transcript tricks that would force public-readonly reliability execution outside configured policy.

#### Scenario: Manual override lacks task contract
- **WHEN** a request manually selects `live_public_readonly` but no configured reliability task contract matches the normalized command
- **THEN** the route selector blocks public execution and records a task-contract mismatch reason

#### Scenario: Transcript includes unsafe target
- **WHEN** a transcript includes an arbitrary URL, private-network address, credential-bearing URL, unsafe protocol, or mixed-origin target while also mentioning an allowlisted public site
- **THEN** the route selector rejects live public execution and records the unsafe target reason

### Requirement: Route useful public-readonly commands by task contract
The router SHALL route useful public-readonly commands to `live_public_readonly` only when public-readonly is enabled and a matching useful task contract exists.

#### Scenario: Useful task contract matches command
- **WHEN** a normalized command matches a useful task contract for documentation, reference, package metadata, release notes, or public repository read/search
- **THEN** the route decision records `public_readonly` route type, `live_public_readonly` execution mode, allowlist id, task id, task category, completion criteria id, limits, evidence privacy state, sanitizer status, and route reason

#### Scenario: Useful task contract is absent
- **WHEN** a command mentions an allowlisted public target but no useful task contract matches the requested slots or task kind
- **THEN** the router rejects live public execution before navigation and records a stable unsupported useful public task reason

### Requirement: Reject broad or unsafe useful-task routing
The router SHALL reject broad browsing, arbitrary URL, account, mutation, upload, download, private-network, and manual override attempts for useful public-readonly tasks.

#### Scenario: Unsafe public command is routed
- **WHEN** a normalized command asks for login, posting, starring, forking, issue creation, pull request creation, purchase, form submission, private data entry, upload, download, private network access, or a transcript-emitted arbitrary URL
- **THEN** the route decision is clarification, confirmation, or blocked rather than `live_public_readonly`

#### Scenario: Manual override attempts useful public execution
- **WHEN** an operator attempts to force `live_public_readonly` without a matching useful task contract
- **THEN** the route decision records manual override rejection and does not launch public navigation
