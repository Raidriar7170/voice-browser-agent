## ADDED Requirements

### Requirement: Preserve adaptation-ready normalized outputs
The system SHALL preserve normalized Browser Task Requests or Clarification Requests in a form that can be reused by later Speech-to-Task Adaptation.

#### Scenario: Accepted request is used for training example derivation
- **WHEN** a trace-derived example is created from an accepted Browser Task Request
- **THEN** the example includes the structured task, intent type, constraints, visual references, confirmation requirement, stop conditions, and safety flags

#### Scenario: Clarification request is used for training example derivation
- **WHEN** a trace-derived example is created from a Clarification Request
- **THEN** the example includes the clarification question, reason, and original transcript text
