## ADDED Requirements

### Requirement: Preserve bounded GitHub public task slots
The normalizer SHALL preserve safe GitHub task slots needed for public-readonly route selection, execution, and completion verification.

#### Scenario: GitHub repository search command is normalized
- **WHEN** a transcript asks to search GitHub for public repositories or projects
- **THEN** the Browser Task Request preserves target site hint `GitHub`, normalized search query, repository search intent, read-only constraints, stop conditions, and safety flags without hardcoding an unrelated query

#### Scenario: GitHub public repository read command is normalized
- **WHEN** a transcript asks to open or read a specific public GitHub repository
- **THEN** the Browser Task Request preserves target site hint `GitHub`, owner/repository or repository slug slot when present, read target, read-only constraints, stop conditions, and safety flags

### Requirement: Clarify or reject unsupported GitHub commands
The normalizer and validator SHALL avoid converting broad or account-oriented GitHub commands into live public-readonly Browser Task Requests.

#### Scenario: GitHub command asks for account action
- **WHEN** a transcript asks to log in, star, fork, watch, comment, create an issue, open a pull request, edit a file, upload, download, or access a private repository on GitHub
- **THEN** the normalized output requires clarification, confirmation, or blocking instead of live GitHub public-readonly execution

#### Scenario: GitHub command is broad research
- **WHEN** a transcript asks to browse GitHub broadly, compare many repositories, keep searching until good projects are found, or make a ranking recommendation
- **THEN** the normalized output is a clarification request or a bounded search task that states the missing narrowing criteria
