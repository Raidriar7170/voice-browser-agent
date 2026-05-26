## 1. Contract Audit and Documentation

- [x] 1.1 Add a line-referenced coverage matrix to `CONTEXT.md` for every domain term.
- [x] 1.2 Add a line-referenced coverage matrix to `CONTEXT.md` for every example-dialogue commitment.
- [x] 1.3 Mark any non-MVP or later-phase commitments as deferred/non-goals with reasons consistent with the bounded scope.
- [x] 1.4 Replace placeholder `Purpose` text in all main OpenSpec specs.

## 2. Trace-Derived Training Examples

- [x] 2.1 Add failing tests for deriving sanitized Speech-to-Task examples from browser-task and clarification traces.
- [x] 2.2 Implement a trace-derived training example model/helper using sanitized trace content and optional human correction.
- [x] 2.3 Add tests proving private nested fields and raw artifact references are excluded.
- [x] 2.4 Document trace-derived examples as later adaptation support, not a fine-tuning or benchmark claim.

## 3. Status Voice Feedback

- [x] 3.1 Add failing tests for gated Operator Console status voice playback.
- [x] 3.2 Implement optional browser-native playback only when `status_voice.enabled` is true and speech synthesis is available.
- [x] 3.3 Preserve textual status feedback when voice playback is disabled or unsupported.

## 4. Verification and Archive

- [x] 4.1 Run `openspec validate context-coverage-closeout --strict`.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run targeted tests for trace-derived examples and Operator Console status voice coverage.
- [x] 4.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 4.5 Run privacy scans for public fixtures, traces, docs, and coverage matrix.
- [x] 4.6 Confirm `git status --short --ignored` contains no unintended tracked changes or private artifacts before archive/commit.
