## ADDED Requirements

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
