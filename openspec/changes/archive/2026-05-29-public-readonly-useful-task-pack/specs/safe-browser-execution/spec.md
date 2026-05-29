## ADDED Requirements

### Requirement: Enforce useful task-pack safety boundaries
The browser executor SHALL enforce the existing public-readonly safety contract for every useful task-pack attempt.

#### Scenario: Useful task starts execution
- **WHEN** a useful public-readonly task starts
- **THEN** execution uses an isolated local browser context, no persistent user profile, no cookie or credential reuse, configured step and timeout budgets, and only the allowed read-only actions from the task contract

#### Scenario: Useful task reaches unsafe action
- **WHEN** execution would log in, submit, post, purchase, delete, star, fork, comment, create an issue, open a pull request, upload, download, enter private data, bypass verification, or leave the configured task boundary
- **THEN** execution stops before the action and records the policy reason as the useful task outcome reason

### Requirement: Record useful task execution evidence privately
The browser executor SHALL record useful task execution evidence as local/private runtime evidence unless sanitizer approval is explicit.

#### Scenario: Useful task captures visual evidence
- **WHEN** a useful task captures a step screenshot, final screenshot, page title, browser action, or page-state proof
- **THEN** the trace records local/private artifact references, sanitized origin, completion state, and sanitizer status without embedding raw screenshot bytes or raw page text in public payloads

#### Scenario: Useful task encounters public-site variance
- **WHEN** a public site returns captcha, verification, rate-limit, unavailable, access-denied, permission-required, redirect, selector-drift, or network failure state
- **THEN** execution records stopped, failed, blocked, or partial outcome with a precise site-variance reason and does not claim completion
