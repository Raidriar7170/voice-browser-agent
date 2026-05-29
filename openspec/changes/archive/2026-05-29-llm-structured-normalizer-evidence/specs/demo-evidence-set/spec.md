## ADDED Requirements

### Requirement: Build local normalizer comparison evidence
The evidence set SHALL include a local workflow that summarizes rule, mock-LLM, and optionally real-provider normalizer behavior over bounded spoken-command examples.

#### Scenario: Comparison evidence is generated
- **WHEN** the normalizer comparison workflow is run from the project checkout
- **THEN** it creates a local manifest or report containing input ids, normalizer modes, output kinds, schema status, validator outcome, fallback state, and route-readiness metadata

#### Scenario: Comparison includes unsupported examples
- **WHEN** the comparison set includes ambiguous, unsafe, broad public-web, account-oriented, or malformed-output cases
- **THEN** the evidence records clarification, confirmation, rejection, fallback, or blocked behavior rather than only successful task outputs

### Requirement: Include normalizer evidence in reviewer handoff
The release-pack and reviewer evidence handoff SHALL surface normalizer comparison evidence without presenting it as a benchmark leaderboard or model-quality claim.

#### Scenario: Release pack finds comparison evidence
- **WHEN** the evidence-pack workflow builds local reviewer output and a normalizer comparison report exists
- **THEN** the manifest and HTML index include a bounded summary of normalizer modes, schema/validation outcomes, fallback counts, and safety outcomes

#### Scenario: Comparison evidence is missing
- **WHEN** the evidence-pack workflow expects normalizer comparison evidence but the report is missing or malformed
- **THEN** it reports a clear completeness issue instead of silently omitting the normalizer evidence

### Requirement: Exclude raw LLM provider data from public evidence
The evidence workflow SHALL keep raw LLM prompts, raw provider responses, credentials, request headers, private transcripts, and remote host details out of committed public artifacts.

#### Scenario: Evidence workflow scans comparison artifacts
- **WHEN** a comparison report or generated release-pack artifact contains API keys, request headers, raw provider responses, private URLs, local file URIs, private transcripts, remote host details, or unsanitized runtime fields
- **THEN** the workflow fails or marks the artifact local/private instead of presenting it as public-safe

#### Scenario: Public evidence describes LLM normalization
- **WHEN** README, demo docs, public evidence page, closeout checklist, video plan, or interview overview mention LLM structured-output normalization
- **THEN** they describe it as bounded intent parsing behind schema validation and deterministic safety gates, not as unrestricted web autonomy, benchmark ranking, SOTA, or model-quality proof
