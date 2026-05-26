## ADDED Requirements

### Requirement: Run bounded agentic visual execution loop
The system SHALL execute validated Browser Task Requests through a bounded agentic loop that observes the browser, resolves visual evidence, chooses an action, executes the action, and verifies progress.

#### Scenario: Validated visual request enters loop
- **WHEN** a Browser Task Request passes validation and required confirmation is not pending
- **THEN** the system starts an agentic vision execution loop with the request constraints, visual references, stop conditions, supported intent type, and maximum step budget

#### Scenario: Step budget is reached
- **WHEN** the agentic loop reaches its configured maximum step count before satisfying the task or a stop condition
- **THEN** the system stops execution and records a bounded step budget stop reason in the Execution Trace

### Requirement: Resolve visual targets through visual grounding evidence
The system SHALL use the Visual Grounding Engine dependency to resolve visible UI targets before executing visual browser actions.

#### Scenario: Visual target is resolved
- **WHEN** the current step needs to click, select, extract, or compare a visible UI target
- **THEN** the step records the visual observation summary, selected target reference, and grounding evidence references used to choose the action

#### Scenario: Visual target is ambiguous
- **WHEN** visual grounding returns multiple plausible targets without enough evidence to choose safely
- **THEN** the system pauses for clarification or stops with an ambiguous visual target reason instead of guessing

### Requirement: Verify progress after each action
The system SHALL verify browser state after each agentic action before deciding whether to continue, recover, succeed, or stop.

#### Scenario: Action changes page state
- **WHEN** an action completes and the follow-up observation indicates meaningful progress toward the Browser Task Request
- **THEN** the step records a positive verification decision and the loop may continue or finish successfully

#### Scenario: Action has no meaningful effect
- **WHEN** an action completes but the follow-up observation shows no meaningful progress or page-state change
- **THEN** the step records the failed verification and the loop either performs a bounded recovery or stops with an explicit reason

### Requirement: Recover or stop from visual execution uncertainty
The system SHALL handle missing targets, stale observations, no-effect actions, and unsupported page states through bounded recovery or explicit stops.

#### Scenario: Stale observation is detected
- **WHEN** the action target came from an observation that no longer matches the current browser state
- **THEN** the system performs a bounded re-observation or stops with a stale visual state reason

#### Scenario: Target remains missing after recovery
- **WHEN** a required visual target remains missing after the allowed recovery attempt
- **THEN** the system stops execution and records the missing target reason in the Execution Trace

### Requirement: Preserve agentic step evidence
The system SHALL preserve structured step-level evidence for every agentic vision execution.

#### Scenario: Agentic step is recorded
- **WHEN** an agentic execution step observes, acts, verifies, recovers, succeeds, fails, or stops
- **THEN** the Execution Trace includes the step index, observation summary, selected action, action result, verification decision, recovery or stop decision, and sanitized evidence references

#### Scenario: Agentic execution has no meaningful evidence
- **WHEN** an agentic live controlled run returns no step evidence, no action event, and no grounding evidence reference
- **THEN** the system marks the execution as failed or stopped with an explicit missing evidence reason

### Requirement: Keep agentic execution bounded to supported browser intents
The system SHALL restrict agentic execution to the existing supported Browser Intent Types and normalized request fields.

#### Scenario: Unsupported long-horizon objective is requested
- **WHEN** a normalized request requires unrestricted browsing, login completion, purchase, deletion, posting, private-data submission, or unrelated long-horizon planning
- **THEN** the agentic executor does not run and the system returns a validation, clarification, confirmation, blocked, or stopped state according to the safety decision
