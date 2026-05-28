## Context

`voice-browser-agent` already supports uploaded/recorded audio ingestion, a replaceable ASR adapter, transcript normalization, safety gates, controlled browser execution, real `browser-use-vision` SoM evidence, sanitized release packs, and a public evidence page. The remaining credibility gap is that the committed evidence does not prove a real audio command can drive the full path; most public artifacts are fixture- or transcript-derived.

The next step should make the app locally usable without expanding into broad public-web automation. The design keeps the bounded one-command execution model, controlled local pages, and public privacy rules, but adds a real voice smoke path, readiness checks, ASR correction UX, practical local scenarios, and failure evidence.

## Goals / Non-Goals

**Goals:**

- Prove one real audio-derived command can run end to end through ASR, normalization, safety gates, controlled browser execution, and sanitized trace export.
- Let a local operator know whether ASR, browser execution, visual grounding, and privacy-safe output paths are ready before attempting real-use flows.
- Let an operator inspect and edit ASR output before normalization so real speech errors do not force blind execution.
- Add a small useful-scenario pack that resembles real product workflows while staying local, controlled, and non-destructive.
- Preserve failure evidence for unavailable ASR, clarification, confirmation, ambiguous visual targets, and successful real voice execution.

**Non-Goals:**

- No streaming ASR, wake word, multi-turn voice conversation, or continuous listening.
- No model fine-tuning, public raw audio dataset, ASR/TTS quality claim, or checkpoint publication.
- No broad public-web automation or logged-in website automation.
- No public hosting requirement; public artifacts remain static and sanitized.
- No raw audio, raw screenshots, browser profiles, cookies, credentials, local file URIs, or remote host details in committed evidence.

## Decisions

1. **Use a deterministic real-voice smoke generator with injectable ASR rather than committing raw audio.**
   - Rationale: a real local run can use `faster-whisper` or remote ASR, but public artifacts must not commit raw recordings. The committed smoke trace can preserve ASR metadata and source type while omitting storage paths.
   - Alternative considered: commit a raw `.wav` sample. Rejected because it weakens the privacy story and conflicts with existing `.gitignore` and public evidence rules.

2. **Represent real audio evidence as a distinct `real_voice_controlled` evidence mode.**
   - Rationale: this separates it from fixture preview, deterministic live controlled, agentic controlled, and real vision controlled traces. Reviewers can see exactly which path started from audio.
   - Alternative considered: reuse `live_controlled`. Rejected because it would hide the important source distinction.

3. **Add preflight as a script plus API status endpoint.**
   - Rationale: users need a command-line check before starting the app, and the console should display the same readiness information. The checks should be conservative and explain missing optional dependencies.
   - Alternative considered: only document manual setup steps. Rejected because the user concern is real usability, not just documentation.

4. **Add transcript review/correction as an explicit operator step.**
   - Rationale: real ASR is fallible. The app should expose ASR text, allow an edited transcript, and record provenance instead of blindly executing a possibly wrong transcript.
   - Alternative considered: auto-normalize immediately after upload. Rejected because it is less safe and less realistic for voice-driven browser control.

5. **Keep useful scenarios local and controlled.**
   - Rationale: CRM/settings/dashboard-style local pages can demonstrate realistic actions without credentials or public-web instability.
   - Alternative considered: run more public websites. Rejected because the goal is real use behavior under controlled privacy and safety boundaries, not fragile automation breadth.

## Risks / Trade-offs

- **ASR dependency may be unavailable locally** -> Preflight reports `not_configured` or `unavailable`; failure traces record the missing dependency without pretending success.
- **ASR transcription may be wrong** -> Console transcript review/correction gates normalization; trace metadata records original and edited transcript provenance.
- **Controlled scenarios may still feel demo-like** -> Scenario tasks should model realistic work patterns such as CRM filtering, settings toggles, and dashboard extraction, while docs clearly explain why they remain local.
- **Evidence modes may proliferate** -> Release-pack builders should group modes clearly and require only one real voice smoke trace initially.
- **Raw runtime artifacts could leak** -> Builders and tests scan real voice traces, overlays, docs, and manifests for private markers; raw audio remains ignored.
