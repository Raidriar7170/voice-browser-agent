## ADDED Requirements

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
