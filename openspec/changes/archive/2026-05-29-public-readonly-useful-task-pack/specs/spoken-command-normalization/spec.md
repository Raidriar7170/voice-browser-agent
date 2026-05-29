## ADDED Requirements

### Requirement: Normalize safe useful public-readonly slots
The normalizer SHALL preserve structured slots needed for useful public-readonly documentation, reference, package metadata, release-note, and public repository read/search tasks.

#### Scenario: Useful public command is normalized
- **WHEN** a spoken or typed command asks to read documentation, inspect reference material, check package metadata, inspect release notes, search public repositories, or read a public repository page
- **THEN** the normalized Browser Task Request preserves safe slots such as target site hint, search query, read target, package ecosystem, package name, release target, owner, repository, repository slug, and task category without emitting arbitrary navigation URLs

### Requirement: Reject unsupported useful public-readonly commands
The normalizer and validator SHALL reject or clarify useful public commands that are broad, ambiguous, account-oriented, mutation-oriented, or private-data-oriented.

#### Scenario: Useful public command exceeds bounded scope
- **WHEN** a command asks for unrestricted browsing, open-ended comparison across arbitrary sites, login, account mutation, repository write action, comment, issue, pull request, star, fork, form submission, purchase, upload, download, private data entry, captcha bypass, or a credential-bearing/private-network URL
- **THEN** the normalized result is a clarification request, validation rejection, confirmation gate, or blocked state rather than an executable useful public-readonly task
