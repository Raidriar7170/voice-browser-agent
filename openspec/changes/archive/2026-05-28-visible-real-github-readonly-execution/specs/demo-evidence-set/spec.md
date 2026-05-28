## ADDED Requirements

### Requirement: Define real GitHub public-readonly smoke evidence
The evidence set SHALL define a local/private real GitHub public-readonly smoke path that is distinct from the controlled GitHub showcase.

#### Scenario: GitHub smoke fixture is documented
- **WHEN** a reviewer opens the public-readonly smoke fixture or demo task documentation
- **THEN** it lists the GitHub task id, target label, allowlist id, browser intent type, task kind, requested slots, URL template or target shape, completion criteria, visual artifact policy, execution mode, and safety boundaries

#### Scenario: Controlled GitHub showcase remains documented
- **WHEN** a reviewer reads GitHub demo documentation
- **THEN** it distinguishes controlled local GitHub showcase evidence from real `github.com` public-readonly evidence and explains when each route is selected

### Requirement: Keep GitHub runtime visuals local until sanitized
The evidence set SHALL exclude raw GitHub runtime screenshots and raw public page traces from public artifacts unless sanitizer approval is explicit.

#### Scenario: Release pack sees GitHub local/private visual artifact
- **WHEN** the release-pack workflow encounters a GitHub public-readonly trace or screenshot marked local/private or sanitizer-pending
- **THEN** it excludes the raw artifact or includes only an approved summary with target label, sanitized origin, completion state, stop/failure reason, and limitations

#### Scenario: GitHub public-readonly smoke is blocked
- **WHEN** GitHub search or repo read is blocked by captcha, login boundary, rate limit, timeout, network failure, or selector drift
- **THEN** the evidence records the outcome as reliability evidence and does not present it as successful public automation

### Requirement: Document visible real GitHub demo flow
The project SHALL document a reviewer-facing local demo flow for seeing real GitHub public-readonly behavior in the Operator Console.

#### Scenario: Reviewer follows visible GitHub demo
- **WHEN** a reviewer follows README or video-plan instructions for the GitHub public-readonly demo
- **THEN** they can enable the GitHub allowlist/task contract, run a bounded command, see the real-page visual result or block state in the console, and understand that artifacts remain local/private
