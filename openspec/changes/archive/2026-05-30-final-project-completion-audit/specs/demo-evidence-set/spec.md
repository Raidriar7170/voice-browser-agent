## MODIFIED Requirements

### Requirement: Maintain context coverage matrix
The project SHALL keep `CONTEXT.md` as the durable coverage matrix for domain terms, example-dialogue commitments, and final completion audit status.

#### Scenario: Coverage matrix is reviewed
- **WHEN** a reviewer audits `CONTEXT.md`
- **THEN** every domain term and example-dialogue commitment has mapped implementation, tests, docs, OpenSpec specs, demo evidence, and a coverage status or justified deferral

#### Scenario: Commitment is deferred
- **WHEN** a `CONTEXT.md` commitment is not implemented in the current MVP
- **THEN** the matrix marks it as deferred or non-goal with a reason consistent with the bounded Voice-to-Browser Agent scope

#### Scenario: Final audit evidence is represented
- **WHEN** final reviewer-facing capabilities have been archived into main OpenSpec specs
- **THEN** the matrix includes current coverage for visual verification, LLM structured-output normalization, public-readonly task-pack runner evidence, normalizer comparison, Speech-to-Task seed-set splits, and Speech-to-Task adaptation evaluation without presenting model fine-tuning as complete

### Requirement: Provide final project closeout handoff pack
The project SHALL provide a final closeout handoff pack that ties together the bounded MVP evidence, current validation commands, generated local artifacts, and archive readiness.

#### Scenario: Reviewer follows closeout checklist
- **WHEN** a reviewer opens the closeout checklist after all prior changes have been archived
- **THEN** it identifies the required commands for demo evidence release-pack generation, public-readonly task-pack run generation, normalizer comparison, Speech-to-Task dataset generation with evaluation splits, Speech-to-Task adaptation evaluation, optional release-pack inclusion of adaptation evaluation, OpenSpec strict main-spec validation, full test execution, diff whitespace checks, and git ignored-output review

#### Scenario: Checklist avoids archived change validation commands
- **WHEN** the checklist documents final OpenSpec validation
- **THEN** it uses current main-spec validation commands and does not require `openspec validate <archived-change> --strict` commands that fail after archive

#### Scenario: Checklist distinguishes committed sources from generated artifacts
- **WHEN** the checklist describes release-pack, task-pack runner, normalizer comparison, adaptation dataset, or adaptation evaluation outputs
- **THEN** it states that generated runtime artifacts stay local and points back to committed sanitized trace sources or explicit fixture/configuration sources

### Requirement: Provide browser-openable interview briefing
The project SHALL include a browser-openable interview/project briefing derived from repository evidence.

#### Scenario: Reviewer opens briefing locally
- **WHEN** a reviewer opens the briefing HTML file from the repository
- **THEN** it explains the problem, bounded scope, architecture, execution flow, evidence modes, safety and privacy gates, adaptation dataset output, adaptation evaluation output, validation surface, limitations, and interview talk track

#### Scenario: Briefing links to evidence sources
- **WHEN** the briefing discusses project claims
- **THEN** it references the README, demo task suite, ablations, video plan, release-pack workflow, adaptation dataset workflow, adaptation evaluation workflow, sanitized trace directories, public evidence page, and OpenSpec validation surface

### Requirement: Guard final handoff positioning
The final handoff pack SHALL preserve bounded Voice-to-Browser Agent positioning and avoid unsupported claims.

#### Scenario: Final handoff wording is checked
- **WHEN** README, closeout checklist, demo docs, public evidence page, or interview briefing are reviewed by automated wording guards
- **THEN** they avoid benchmark, SOTA, production automation, unrestricted autonomy, ASR/TTS quality, model checkpoint, fine-tuned model completion, and public raw-dataset claims

#### Scenario: Limitations are stated
- **WHEN** a reviewer reads the briefing or final closeout checklist
- **THEN** it states that model fine-tuning, expanded dataset collection, public hosting, and broad public-web automation are out of scope for the closeout MVP and may be handled in a separate future project

## ADDED Requirements

### Requirement: Verify final review artifact chain
The project SHALL define and verify a final local review chain that rebuilds or inspects the current reviewer artifacts without committing generated runtime outputs.

#### Scenario: Final review commands are run
- **WHEN** the final completion audit is verified from the project checkout
- **THEN** the validation evidence includes successful main-spec validation, full project tests, whitespace checks, ignored-output status review, and local generation or inspection of release-pack, normalizer comparison, Speech-to-Task dataset split, and Speech-to-Task adaptation evaluation artifacts

#### Scenario: Generated artifacts remain local
- **WHEN** the final review artifact chain writes under `runtime/`
- **THEN** git status shows those outputs as ignored or unstaged local artifacts rather than committed public evidence
