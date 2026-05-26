## ADDED Requirements

### Requirement: Gate optional status voice playback
The Operator Console SHALL play Status Voice Feedback only when feedback is enabled and browser speech synthesis is available.

#### Scenario: Status voice feedback is enabled
- **WHEN** an execution response includes enabled Status Voice Feedback
- **THEN** the console requests browser-native speech playback for the status, confirmation, stop, or failure text

#### Scenario: Status voice feedback is disabled
- **WHEN** an execution response includes disabled Status Voice Feedback
- **THEN** the console does not request spoken playback and continues to display the textual status

#### Scenario: Browser speech synthesis is unavailable
- **WHEN** Status Voice Feedback is enabled but the browser has no speech synthesis capability
- **THEN** the console silently keeps textual feedback without creating raw audio artifacts
