## ADDED Requirements

### Requirement: Maintain context coverage matrix
The project SHALL keep `CONTEXT.md` as the durable coverage matrix for domain terms and example-dialogue commitments.

#### Scenario: Coverage matrix is reviewed
- **WHEN** a reviewer audits `CONTEXT.md`
- **THEN** every domain term and example-dialogue commitment has mapped implementation, tests, docs, OpenSpec specs, demo evidence, and a coverage status or justified deferral

#### Scenario: Commitment is deferred
- **WHEN** a `CONTEXT.md` commitment is not implemented in the current MVP
- **THEN** the matrix marks it as deferred or non-goal with a reason consistent with the bounded Voice-to-Browser Agent scope
