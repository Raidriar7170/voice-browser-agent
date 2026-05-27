## Context

The repository has completed the bounded Voice-to-Browser Agent MVP: fixture-backed demo-preview traces, selected live-controlled visual tasks, agentic step evidence, confirmation gates, clarification handling, and sanitized exports. The immediate weakness is usability. A user can select `github-search` and `live_controlled`, then click `Run`, which executes the text transcript path rather than the selected fixture path and returns a preview-style trace. Technically this is bounded and safe, but it is not self-explanatory.

This change turns the current debugging console into a clearer demo console without making it a consumer product or broad automation agent.

## Goals / Non-Goals

**Goals:**

- Make `Run Transcript`, `Run Fixture`, and `Run Uploaded Audio` distinct controls with clear state.
- Show which fixtures support live-controlled execution and prevent unsupported live-controlled fixture runs from looking successful.
- Preserve explicit preview traces for public website tasks and selected live-controlled traces for controlled visual tasks.
- Make final status, execution mode, stop/failure/clarification reasons, and confirmation prompts easy to scan.
- Keep generated/exported artifacts sanitized.

**Non-Goals:**

- Add open-web live automation for public websites such as GitHub or OpenAI.
- Add auth, browser profiles, cookies, production automation, remote browser sessions, or a large UI framework.
- Add new ASR/TTS model capability, streaming voice conversation, benchmark tables, or SOTA claims.
- Redesign the whole product as a polished landing page.

## Decisions

### Add fixture metadata as a small backend contract

Expose a lightweight `/api/fixtures` endpoint with fixture ids, expected transcripts, supported execution modes, visual-heavy flag, and short labels. The static UI can use this to populate selects and mode help instead of hardcoding ambiguous options.

Alternatives considered:

- Keep static fixture options: simple, but repeats the ambiguity that caused the current confusion.
- Infer support entirely in JS: avoids an endpoint, but duplicates backend live-controlled task knowledge.

### Split execution buttons by input source

Rename the controls so the operator chooses the source intentionally: transcript text, selected fixture, or uploaded/recorded audio. Store the last ingested `audio_id` in the UI state and run it through `/api/executions` when requested.

Alternatives considered:

- Keep one `Run` button that guesses source: compact, but fragile and hard to explain in a demo.
- Remove transcript execution: safer, but useful for quick normalizer/clarification demos.

### Treat unsupported live-controlled fixture selection as a UI-blocked state

When a fixture does not support live-controlled execution, the UI should either force `demo_preview` or disable the live option with an explanation. The backend should continue returning explicit errors for unsupported live-controlled fixture requests.

Alternatives considered:

- Silently downgrade to preview: safe, but makes results look surprising.
- Enable live-controlled for public sites: outside the bounded MVP and weaker privacy posture.

### Improve evidence readability without changing trace semantics

Render a compact summary above raw JSON and annotate timeline rows by event type. The raw trace remains available for audit. This keeps the console useful for both presentation and debugging.

## Risks / Trade-offs

- More UI labels can become clutter -> use compact mode/source/status text and keep raw JSON collapsible or below the main evidence.
- Backend fixture metadata can drift from docs -> derive live-supported ids from `demo_tasks.py` and fixture manifests.
- Browser upload/recording may fail without ASR configured -> surface adapter errors as status text, not silent failure.
- Tests may become string-fragile -> assert stable ids and behavior-relevant labels rather than pixel layout.

## Migration Plan

This is additive. Existing endpoints continue to work. The console JS gains fixture metadata loading and uploaded-audio execution state. If the metadata endpoint fails, the UI can fall back to the current static fixture list.

## Open Questions

None for this phase. Keep the slice focused on demo-flow clarity and do not add live public-web automation.
