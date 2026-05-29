## ADDED Requirements

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
