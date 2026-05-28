## ADDED Requirements

### Requirement: Preserve expanded public-readonly task slots
The normalizer SHALL preserve safe task slots required by the expanded public-readonly reliability smoke set.

#### Scenario: Documentation search command is normalized
- **WHEN** a transcript asks to search an allowlisted documentation or reference site
- **THEN** the Browser Task Request preserves target site hint, search query, read-only intent, constraints, stop conditions, and safety flags needed by the matching reliability task contract

#### Scenario: Public repository read command is normalized
- **WHEN** a transcript asks to read a specific public repository or public reference page
- **THEN** the Browser Task Request preserves target site hint, owner/repository or read target slots when present, read-only intent, constraints, stop conditions, and safety flags needed by completion verification

### Requirement: Clarify unsupported reliability commands
The normalizer and validator SHALL prefer clarification, rejection, or blocking when a public command cannot map to one bounded reliability task.

#### Scenario: Command is broad public browsing
- **WHEN** a transcript asks the agent to browse broadly, compare many sites, keep searching until satisfied, make an open-ended recommendation, use an account, bypass a barrier, or complete a long-horizon public web goal
- **THEN** the normalized output is rejected or converted to a Clarification Request instead of a public-readonly reliability Browser Task Request

#### Scenario: Command implies mutation or private data
- **WHEN** a transcript asks to log in, submit, post, purchase, delete, star, fork, comment, create an issue, open a pull request, upload, download, enter private data, or perform another non-read-only action
- **THEN** the normalized output records safety flags and requires clarification, confirmation, or blocking before route selection

#### Scenario: Command includes arbitrary URL
- **WHEN** a transcript includes an arbitrary URL, unsafe protocol, private-network host, credential-bearing URL, or mixed-origin target outside configured task slots
- **THEN** the normalizer or validator preserves the safety concern so route selection cannot treat it as an approved reliability task
