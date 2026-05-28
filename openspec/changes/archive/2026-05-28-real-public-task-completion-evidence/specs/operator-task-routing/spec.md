## ADDED Requirements

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
