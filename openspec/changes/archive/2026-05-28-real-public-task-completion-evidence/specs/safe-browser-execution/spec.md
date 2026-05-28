## ADDED Requirements

### Requirement: Execute public tasks with completion-aware verifier
The public-readonly executor SHALL run allowed public task actions and then verify task-specific completion criteria before returning success.

#### Scenario: Public task verifier passes
- **WHEN** the executor performs the configured read-only task steps and observes the required task-specific proof
- **THEN** the execution result records succeeded status, completed public task state, observed proof summary, browser action evidence, and grounding references when available

#### Scenario: Public task verifier fails
- **WHEN** the executor performs safe actions but cannot observe the required task-specific proof
- **THEN** the execution result is failed or stopped with a missing public task completion reason instead of succeeded

### Requirement: Preserve policy stops during public task execution
The public-readonly executor SHALL enforce URL, action, browser-state, and stop-condition policy checks before and during task execution.

#### Scenario: Sensitive state appears before completion
- **WHEN** a public task reaches login, captcha, checkout, submit, posting, deletion, upload, download, password entry, private-data entry, off-allowlist navigation, or another configured sensitive state
- **THEN** the executor stops before the next action and records the matched policy reason and incomplete task state

#### Scenario: Next action is outside task policy
- **WHEN** the next proposed action is not listed in the task contract's allowed read-only action classes
- **THEN** the executor blocks the action and records an action-policy stop reason

### Requirement: Classify real public task outcomes
The execution result SHALL distinguish completed, partial, stopped, failed, and blocked public task outcomes.

#### Scenario: Public task partially completes
- **WHEN** the run collects useful public page evidence but does not meet all completion criteria before a safe stop or budget limit
- **THEN** the trace records partial completion state with collected proof and the remaining unmet criteria

#### Scenario: Public task is blocked before navigation
- **WHEN** validation, confirmation, route policy, URL safety, or task contract policy blocks a public command before opening a public page
- **THEN** the trace records blocked outcome without claiming that a public webpage was operated
