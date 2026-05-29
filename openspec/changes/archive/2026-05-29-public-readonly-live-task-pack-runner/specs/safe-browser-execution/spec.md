## ADDED Requirements

### Requirement: Enforce public-readonly policy during task-pack runner attempts
The browser executor SHALL apply the existing public-readonly safety contract to every live task-pack runner attempt.

#### Scenario: Runner starts a live task attempt
- **WHEN** the task-pack runner starts a useful public-readonly task in live mode
- **THEN** execution uses an isolated local browser context with no persistent user profile, no reused cookies, no stored credentials, configured step and timeout budgets, and only the read-only action classes allowed by the task contract

#### Scenario: Runner reaches unsafe state
- **WHEN** a live task-pack attempt reaches login, submit, post, purchase, delete, star, fork, comment, issue creation, pull request creation, upload, download, private-data entry, captcha bypass, off-allowlist navigation, private-network target, or another mutation/account boundary
- **THEN** the executor stops or blocks before the action and returns the matched policy reason for the run manifest

### Requirement: Prevent task-pack runner bypasses
The browser executor SHALL prevent task-pack runner configuration from bypassing task contracts, URL safety, route policy, completion verification, or artifact privacy.

#### Scenario: Runner supplies unsafe target
- **WHEN** a selected task has an unsafe target URL, unsafe URL template, non-allowlisted origin, credential-bearing URL, private-network host, unsupported protocol, or requested slot outside the task contract safe slots
- **THEN** execution is blocked before navigation and the manifest records a policy or contract mismatch outcome

#### Scenario: Runner tries unsupported action
- **WHEN** a live task-pack attempt proposes an action that is not allowed by the selected task contract
- **THEN** the executor rejects the action, records an action-policy stop reason, and does not continue as a completed task

### Requirement: Return completion-aware runner results
The browser executor SHALL return task-pack runner results that distinguish task completion proof from simple page-open evidence.

#### Scenario: Completion verifier passes
- **WHEN** a live task-pack attempt observes all configured task-specific proof
- **THEN** the executor returns completed outcome with observed proof summary, browser action evidence, completion criteria id, and guarded visual artifact metadata when available

#### Scenario: Completion verifier does not pass
- **WHEN** a live task-pack attempt opens a page or collects useful evidence but fails to observe all configured proof
- **THEN** the executor returns partial, stopped, or failed outcome with unmet criteria and stop or failure reason rather than succeeded status

### Requirement: Keep task-pack runner artifacts local private
The executor SHALL keep task-pack runner traces and visual artifacts local/private unless explicit sanitizer approval marks them public-safe.

#### Scenario: Runner captures visual evidence
- **WHEN** a live task-pack attempt captures a step screenshot, final screenshot, page title, browser action, or page-state proof
- **THEN** the execution result records guarded local/private artifact references, sanitized origin, completion state, and sanitizer status without embedding raw screenshot bytes or raw page text in public payloads

#### Scenario: Runner artifact fails sanitizer
- **WHEN** sanitizer checks do not approve a task-pack runner trace or visual artifact
- **THEN** the executor and export workflow keep the artifact local/private and report sanitizer-pending or sanitizer-failed status without presenting it as public-ready evidence
