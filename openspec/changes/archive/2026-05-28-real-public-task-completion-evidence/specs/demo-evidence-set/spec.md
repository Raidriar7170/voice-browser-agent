## ADDED Requirements

### Requirement: Define real public task smoke evidence
The evidence set SHALL define a small real public task smoke set that proves task completion or honest failure under the public-readonly safety contract.

#### Scenario: Public task smoke set is documented
- **WHEN** a reviewer opens public-readonly smoke documentation or fixtures
- **THEN** it lists each task id, target label, allowlist id, browser intent type, task kind, requested slots, expected completion criteria, safety boundaries, execution mode, and private/public artifact status

#### Scenario: Public task smoke run is incomplete
- **WHEN** a smoke task fails, partially completes, or stops due to site variance, timeout, missing selector, login boundary, or policy stop
- **THEN** the evidence records the outcome as reliability evidence rather than a successful public automation claim

### Requirement: Publish only sanitized public task summaries
The public evidence set SHALL exclude raw real public task traces unless public-readonly sanitizer approval passes.

#### Scenario: Release pack encounters private public task trace
- **WHEN** the release-pack workflow sees a public task trace with local/private or pending sanitizer state
- **THEN** it excludes the raw trace from public artifacts or includes only an approved summary explaining target label, sanitized origin, completion state, stop/failure reason, and limitations

#### Scenario: Public task trace is approved
- **WHEN** a public task trace passes explicit public-readonly sanitizer checks
- **THEN** the release-pack manifest and HTML classify it as real public task evidence and include privacy-scan status without exposing raw public page content

### Requirement: Avoid real public task overclaiming
The public evidence documentation SHALL describe real public task execution as bounded, local, read-only, allowlisted, and private-by-default.

#### Scenario: Reviewer reads public evidence docs
- **WHEN** public evidence docs mention real public webpage task execution
- **THEN** they state the allowlist, task-contract boundary, completion verifier, private trace policy, and non-goals for login, mutation, account automation, broad site support, captcha bypass, and long-horizon browsing
