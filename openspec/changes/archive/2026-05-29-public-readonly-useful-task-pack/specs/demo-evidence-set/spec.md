## ADDED Requirements

### Requirement: Include useful public-readonly task-pack summary
The evidence set SHALL include a reviewer-readable useful public-readonly task-pack summary generated from explicit task contracts and local/private attempt evidence.

#### Scenario: Release pack includes useful task-pack summary
- **WHEN** the evidence-pack workflow builds local reviewer output
- **THEN** it includes a useful task-pack summary with task count, category coverage, outcome counts, task ids, target labels, target classes, completion criteria ids, observed proof summaries, unmet criteria, stop or failure reasons, privacy states, sanitizer statuses, export states, and limitations

#### Scenario: Useful task-pack summary is incomplete
- **WHEN** the useful task-pack summary is missing required categories, required outcome fields, privacy state, sanitizer status, or task-specific completion criteria
- **THEN** the evidence workflow reports a clear completeness or privacy error instead of presenting the summary as reviewer-ready

### Requirement: Exclude raw useful public-readonly artifacts from public evidence
The evidence set SHALL keep raw useful public-readonly traces and runtime artifacts out of committed public evidence unless an explicit sanitizer approves them.

#### Scenario: Release pack sees local/private useful task artifact
- **WHEN** the release-pack workflow encounters a useful public-readonly trace, screenshot, page text, browser profile, local file URI, private URL, credential, cookie, or raw runtime artifact
- **THEN** it excludes that raw artifact from public evidence and records only sanitizer-state metadata or a local/private exclusion reason

### Requirement: Document useful task-pack scope and limitations
The public evidence documentation SHALL describe useful public-readonly tasks as bounded local evidence, not production automation or unrestricted web autonomy.

#### Scenario: Reviewer reads useful task-pack docs
- **WHEN** a reviewer opens README, demo docs, public evidence page, closeout checklist, video plan, or interview overview
- **THEN** the docs distinguish controlled local demos, reliability matrix evidence, useful public-readonly task-pack summaries, and raw local/private public runtime artifacts while avoiding production, benchmark, SOTA, model-quality, captcha-bypass, account-automation, or broad-autonomy claims
