## ADDED Requirements

### Requirement: Preserve public task slots during normalization
The normalizer SHALL preserve safe public task slots needed for public-readonly route selection and completion verification.

#### Scenario: Public documentation search command is normalized
- **WHEN** a transcript asks to search an allowlisted public documentation or reference site
- **THEN** the Browser Task Request preserves target site hint, search query, read-only intent, constraints, stop conditions, and safety flags needed by the public task router

#### Scenario: Public reference read command is normalized
- **WHEN** a transcript asks to read or extract visible information from an allowlisted public reference page
- **THEN** the Browser Task Request preserves target site hint, read target or extraction target, read-only intent, constraints, and stop conditions needed by the completion verifier

### Requirement: Clarify unsupported public task commands
The normalizer and validator SHALL prefer clarification or rejection when a public command cannot be mapped to one bounded read-only task.

#### Scenario: Public command is too broad
- **WHEN** a transcript asks the agent to browse broadly, compare many sites, keep searching until satisfied, use an account, bypass a barrier, or complete a long-horizon public web goal
- **THEN** the normalized output is rejected or converted to a Clarification Request instead of a public-readonly Browser Task Request

#### Scenario: Public command implies mutation
- **WHEN** a transcript asks to log in, submit, post, purchase, delete, upload, download, enter private data, or perform another non-read-only public action
- **THEN** the normalized output records safety flags and requires confirmation, clarification, or blocking before browser execution
