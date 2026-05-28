## ADDED Requirements

### Requirement: Define public-readonly smoke evidence
The evidence set SHALL define a small public-readonly smoke set that demonstrates real public webpage operation under the bounded safety contract.

#### Scenario: Public-readonly smoke set is documented
- **WHEN** a reviewer opens the demo evidence documentation
- **THEN** it lists the allowlisted public task ids, target labels, browser intent types, expected safety boundaries, execution mode, and private/public artifact status

#### Scenario: Public-readonly smoke run stops safely
- **WHEN** a public-readonly smoke task reaches login, mutation, private-data, upload, download, or unsupported state
- **THEN** the evidence records the stop as reliability evidence rather than a successful public automation claim

### Requirement: Keep public-readonly evidence private until sanitized
The evidence set SHALL exclude public-readonly runtime traces from public artifacts unless an explicit sanitizer marks them public-safe.

#### Scenario: Release pack scans evidence
- **WHEN** the release-pack workflow encounters a public-readonly trace without public-safe sanitizer approval
- **THEN** it excludes the trace from public artifacts or marks it local/private with a clear reason

#### Scenario: Public-readonly trace is approved
- **WHEN** a public-readonly trace passes the explicit public-readonly sanitizer
- **THEN** the public artifact records evidence mode, target label, sanitized origin, final status, stop or failure reason, privacy-scan status, and limitations

### Requirement: Avoid public-readonly overclaiming
The evidence set SHALL describe public-readonly execution as bounded local evidence, not production automation or unrestricted web autonomy.

#### Scenario: Public evidence page describes public-readonly mode
- **WHEN** public evidence documentation mentions public-readonly execution
- **THEN** it states the allowlist, read-only action limits, private-by-default trace boundary, and non-goals for login, mutation, account automation, and long-horizon browsing
