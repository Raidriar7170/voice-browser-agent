# agentic-vision-execution Specification

## Purpose
Defines the bounded observe-act-verify visual execution loop for validated Browser Task Requests, including visual target resolution, step evidence, recovery decisions, safety stops, and local browser execution through the `browser-use-vision` dependency boundary.
## Requirements
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
The system SHALL verify browser state after each agentic action through an explicit visual verification result before deciding whether to continue, recover, succeed, or stop.

#### Scenario: Action changes page state
- **WHEN** an action completes and the follow-up observation or verifier indicates meaningful progress toward the Browser Task Request
- **THEN** the step records a positive verification decision, a visual verification result with outcome `passed`, and the loop may continue or finish successfully

#### Scenario: Action has no meaningful effect
- **WHEN** an action completes but the follow-up observation or verifier shows no meaningful progress or page-state change
- **THEN** the step records the failed verification, a visual verification result with outcome `failed` or `uncertain`, and the loop either performs a bounded recovery or stops with an explicit reason

### Requirement: Recover or stop from visual execution uncertainty
The system SHALL handle missing targets, stale observations, no-effect actions, and unsupported page states through bounded recovery or explicit stops.

#### Scenario: Stale observation is detected
- **WHEN** the action target came from an observation that no longer matches the current browser state
- **THEN** the system performs a bounded re-observation or stops with a stale visual state reason

#### Scenario: Target remains missing after recovery
- **WHEN** a required visual target remains missing after the allowed recovery attempt
- **THEN** the system stops execution and records the missing target reason in the Execution Trace

### Requirement: Preserve agentic step evidence
The system SHALL preserve structured step-level evidence and visual verification evidence for every agentic vision execution.

#### Scenario: Agentic step is recorded
- **WHEN** an agentic execution step observes, acts, verifies, recovers, succeeds, fails, or stops
- **THEN** the Execution Trace includes the step index, observation summary, selected action, action result, verification decision, visual verification result when applicable, recovery or stop decision, and sanitized evidence references

#### Scenario: Agentic execution has no meaningful evidence
- **WHEN** an agentic live controlled run returns no step evidence, no action event, no visual verification result, and no grounding evidence reference
- **THEN** the system marks the execution as failed or stopped with an explicit missing evidence reason

### Requirement: Keep agentic execution bounded to supported browser intents
The system SHALL restrict agentic execution to the existing supported Browser Intent Types and normalized request fields.

#### Scenario: Unsupported long-horizon objective is requested
- **WHEN** a normalized request requires unrestricted browsing, login completion, purchase, deletion, posting, private-data submission, or unrelated long-horizon planning
- **THEN** the agentic executor does not run and the system returns a validation, clarification, confirmation, blocked, or stopped state according to the safety decision

### Requirement: Preserve explicit visual verification results
The system SHALL preserve explicit post-action visual verification results separately from browser action status.

#### Scenario: Visual verification passes
- **WHEN** an agentic action is followed by visual evidence that the expected browser state or target condition was achieved
- **THEN** the trace records a visual verification result with outcome `passed`, expected condition, observed state summary, reason text, sanitized evidence references, and provider mode or verifier mode metadata

#### Scenario: Visual verification fails
- **WHEN** an agentic action completes but follow-up visual evidence shows the expected browser state or target condition was not achieved
- **THEN** the trace records a visual verification result with outcome `failed`, the unmet condition, observed state summary, reason text, sanitized evidence references, and the recovery or stop decision

#### Scenario: Visual verification is uncertain
- **WHEN** the verifier cannot safely determine whether the expected browser state or target condition was achieved
- **THEN** the trace records a visual verification result with outcome `uncertain` and the loop either performs bounded recovery or stops with an explicit verification uncertainty reason

### Requirement: Keep visual verification keyless by default
The system SHALL provide a deterministic or mock visual verifier path for controlled local tasks without requiring model credentials or external network access.

#### Scenario: Controlled verification runs locally
- **WHEN** an agentic controlled task reaches post-action verification
- **THEN** the default verifier checks controlled expected-state evidence and produces a verification result without calling a real VLM provider

#### Scenario: Optional provider verifier is configured
- **WHEN** a real VLM or provider verifier is explicitly configured
- **THEN** the system records safe provider provenance and still applies deterministic safety, route, confirmation, and privacy boundaries before presenting the result as evidence

### Requirement: Preserve visual verifier privacy
The system SHALL exclude provider-private and raw visual data from public or sanitized visual verification artifacts.

#### Scenario: Verification trace is sanitized
- **WHEN** a trace containing visual verification results is exported for review or release-pack evidence
- **THEN** the export includes safe verification outcome metadata while excluding raw screenshots, raw annotated images, raw provider prompts, raw provider responses, request headers, API keys, credentials, cookies, browser profiles, private URLs, local file URIs, and remote host details
