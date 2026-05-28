# demo-evidence-set Specification

## Purpose
Defines the reproducible public evidence contract for the bounded Voice-to-Browser Agent: controlled demo tasks, sanitized traces, live controlled and agentic evidence modes, demo ablations, privacy boundaries, and non-benchmark positioning.
## Requirements
### Requirement: Provide reproducible demo task suite
The project SHALL include a Demo Task Suite of 8-12 controlled or public non-destructive tasks.

#### Scenario: Demo task suite is listed
- **WHEN** a reviewer opens the demo task documentation
- **THEN** the documentation lists each task, audio fixture, expected browser intent type, expected stop condition, and whether visual grounding is required

### Requirement: Include visual-grounding-heavy tasks
At least half of the Demo Task Suite SHALL be Visual-Grounding-Heavy Tasks.

#### Scenario: Demo suite contains eight tasks
- **WHEN** the Demo Task Suite contains eight tasks
- **THEN** at least four tasks depend on visual UI evidence such as icons, color swatches, canvas/SVG content, image-like cards, or spatial references

### Requirement: Use reproducible audio fixtures
The project SHALL provide Reproducible Audio Fixtures for the stable demo path.

#### Scenario: Demo task is run from fixture
- **WHEN** a demo task is executed from its saved audio fixture
- **THEN** the system can reproduce the ASR-to-execution flow without requiring live microphone input

### Requirement: Store sanitized demo artifacts
The project SHALL store only sanitized public demo artifacts in the repository.

#### Scenario: Public trace artifact is committed
- **WHEN** a trace artifact is included in public documentation or version control
- **THEN** it contains no credentials, private URLs, personal data, raw user recordings, remote host details, or live browser state

### Requirement: Include demo ablations
The project SHALL include 2-3 Demo Ablations that show why major modules are needed without presenting a benchmark leaderboard.

#### Scenario: Visual grounding ablation is shown
- **WHEN** the documentation demonstrates a task without visual grounding
- **THEN** it explains the observed failure or limitation without claiming a benchmark result or SOTA comparison

### Requirement: Avoid benchmark positioning
The public documentation SHALL position the project as a bounded voice-driven browser agent demo, not as a benchmark or general autonomous assistant.

#### Scenario: README describes project scope
- **WHEN** a reviewer reads the README
- **THEN** the README describes bounded Chinese-first voice-driven browser execution, explicit safety stops, traceable artifacts, and no unrestricted web autonomy claim

### Requirement: Provide live controlled sanitized traces
The project SHALL include sanitized live controlled trace artifacts for at least two controlled visual-grounding-heavy demo tasks.

#### Scenario: Reviewer opens live controlled artifacts
- **WHEN** a reviewer opens the live controlled trace artifact directory
- **THEN** it contains sanitized traces for at least two selected controlled visual tasks and each trace is marked as live controlled evidence

#### Scenario: Live controlled task fails
- **WHEN** a selected live controlled task fails or stops
- **THEN** the sanitized trace records the final status, failure or stop reason, and any available browser action or grounding evidence references

### Requirement: Distinguish preview and live evidence sets
The project SHALL clearly distinguish demo-preview artifacts from live-controlled artifacts in file paths and documentation.

#### Scenario: Demo documentation lists evidence modes
- **WHEN** a reviewer reads the demo task documentation
- **THEN** the documentation identifies which artifacts are demo-preview traces and which artifacts are live-controlled traces

#### Scenario: Sanitized artifacts are committed
- **WHEN** sanitized preview and live artifacts are committed
- **THEN** their directory names or metadata make the execution mode unambiguous

### Requirement: Preserve public artifact privacy for live runs
The project SHALL publish only sanitized live controlled artifacts.

#### Scenario: Live trace is exported for public evidence
- **WHEN** a live controlled trace is written to the public artifact directory
- **THEN** it excludes raw audio, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, and unsanitized live browser state

### Requirement: Provide sanitized agentic execution traces
The project SHALL include sanitized agentic execution trace artifacts for selected controlled visual-grounding-heavy demo tasks.

#### Scenario: Reviewer opens agentic trace artifacts
- **WHEN** a reviewer opens the public agentic trace artifact directory
- **THEN** it contains sanitized traces for at least two selected controlled visual tasks and each trace includes agentic step evidence

#### Scenario: Agentic task fails or stops
- **WHEN** a selected agentic visual task fails, stops, or requires clarification
- **THEN** the sanitized trace records the final status, step evidence, and failure, stop, recovery, or clarification reason

### Requirement: Distinguish agentic evidence from preview evidence
The project SHALL clearly distinguish agentic live-controlled evidence from demo-preview evidence in documentation, paths, or trace metadata.

#### Scenario: Demo documentation lists evidence modes
- **WHEN** a reviewer reads the demo task documentation
- **THEN** the documentation identifies which artifacts are demo-preview traces, live-controlled action-list traces, and agentic live-controlled traces

### Requirement: Include agentic demo ablations
The project SHALL include small Demo Ablations that explain why re-observation and visual target resolution matter for agentic execution.

#### Scenario: Re-observation ablation is documented
- **WHEN** the documentation demonstrates a visual task without re-observation after action
- **THEN** it explains the observed failure or limitation without presenting a benchmark, leaderboard, or SOTA claim

#### Scenario: Visual target resolution ablation is documented
- **WHEN** the documentation demonstrates a visual task without visual grounding target resolution
- **THEN** it explains the observed failure or limitation using controlled demo evidence

### Requirement: Preserve privacy in agentic artifacts
The project SHALL publish only sanitized agentic execution artifacts.

#### Scenario: Agentic trace is committed
- **WHEN** an agentic execution trace is included in public documentation or version control
- **THEN** it excludes raw audio, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, and unsanitized live browser state

### Requirement: Maintain context coverage matrix
The project SHALL keep `CONTEXT.md` as the durable coverage matrix for domain terms and example-dialogue commitments.

#### Scenario: Coverage matrix is reviewed
- **WHEN** a reviewer audits `CONTEXT.md`
- **THEN** every domain term and example-dialogue commitment has mapped implementation, tests, docs, OpenSpec specs, demo evidence, and a coverage status or justified deferral

#### Scenario: Commitment is deferred
- **WHEN** a `CONTEXT.md` commitment is not implemented in the current MVP
- **THEN** the matrix marks it as deferred or non-goal with a reason consistent with the bounded Voice-to-Browser Agent scope

### Requirement: Document console demo flow
The project SHALL document the intended Operator Console demo flow for the bounded MVP.

#### Scenario: Reviewer follows demo instructions
- **WHEN** a reviewer reads the demo documentation or README
- **THEN** they can identify which controls to use for transcript demos, fixture replay, uploaded audio execution, live-controlled visual tasks, clarification examples, confirmation examples, and sanitized trace export

#### Scenario: Reviewer chooses a public showcase task
- **WHEN** a reviewer selects a public showcase task
- **THEN** the documentation explains that the stable path is demo-preview evidence rather than live public-web automation

### Requirement: Build reproducible demo evidence release pack
The project SHALL provide a local workflow that builds a reproducible demo evidence release pack from sanitized demo artifacts.

#### Scenario: Release pack is generated
- **WHEN** the evidence pack workflow is run from the project checkout
- **THEN** it creates a release directory containing a manifest, browser-openable HTML index, and references or copies of selected sanitized trace artifacts

#### Scenario: Release pack uses sanitized sources
- **WHEN** the workflow collects trace artifacts
- **THEN** it uses only checked-in sanitized preview, live-controlled, or agentic trace sources and does not include raw recordings, raw screenshots, browser profiles, credentials, private URLs, remote host details, or unsanitized runtime traces

### Requirement: Emit evidence manifest
The release pack SHALL include a machine-readable manifest that summarizes every included trace artifact.

#### Scenario: Trace row is recorded
- **WHEN** a trace is included in the release pack
- **THEN** the manifest records fixture id, evidence mode, source path, final status, stop reason or failure reason when present, grounding evidence references, agentic step count, and privacy-scan result

#### Scenario: Evidence mode is classified
- **WHEN** the manifest describes preview, live-controlled, or agentic trace artifacts
- **THEN** it classifies them as `demo_preview`, `live_controlled`, or `agentic_live_controlled` without relying only on the trace `execution_mode` field

### Requirement: Provide reviewer-readable HTML evidence index
The release pack SHALL include a browser-openable HTML index generated from the evidence manifest.

#### Scenario: Reviewer opens index
- **WHEN** a reviewer opens the generated HTML index locally
- **THEN** they can identify the included fixtures, evidence modes, final statuses, stop or failure reasons, trace paths, and privacy-scan status without running the Operator Console

#### Scenario: HTML preserves bounded positioning
- **WHEN** the HTML index describes the release pack
- **THEN** it presents the project as a bounded demo evidence pack and avoids benchmark, SOTA, production automation, or unrestricted public-web autonomy claims

### Requirement: Gate release pack completeness and privacy
The release pack workflow SHALL fail when required evidence is missing, ambiguous, malformed, or privacy-unsafe.

#### Scenario: Required evidence is missing
- **WHEN** the sanitized preview traces do not cover the demo task suite or selected live/agentic trace groups do not cover the required controlled visual fixtures
- **THEN** the workflow exits non-zero with a clear reason naming the missing fixture or evidence mode

#### Scenario: Private marker is detected
- **WHEN** a candidate trace or generated release artifact contains raw audio paths, raw screenshots, browser profile data, cookies, credentials, private URLs, remote host details, local file URIs, or unsanitized runtime fields
- **THEN** the workflow exits non-zero and does not present the release pack as public-ready

### Requirement: Include real-use evidence mode
The evidence pack SHALL include a distinct `real_voice_controlled` evidence mode for sanitized traces that start from uploaded or recorded audio and execute a controlled local visual task.

#### Scenario: Release pack includes real voice evidence
- **WHEN** the release-pack workflow finds a sanitized real voice controlled trace
- **THEN** the manifest and HTML index classify it as `real_voice_controlled` and include input source, ASR adapter metadata, transcript review status, final status, grounding references, and privacy-scan status

#### Scenario: Required real voice evidence is missing
- **WHEN** final real-use evidence validation runs without the required sanitized real voice controlled trace
- **THEN** it fails with a clear missing real voice evidence reason

### Requirement: Include useful local scenario pack
The project SHALL document and evidence a small set of local useful scenarios that are closer to real workflows than one-off visual demos while staying controlled and non-destructive.

#### Scenario: Useful scenarios are listed
- **WHEN** a reviewer opens the scenario documentation
- **THEN** it lists local CRM, settings, dashboard, or similar controlled scenarios with user intent, browser intent type, expected safety behavior, evidence mode, and privacy boundary

### Requirement: Preserve failure and usage traces
The evidence set SHALL include sanitized traces for representative real-use failures and operator decisions.

#### Scenario: Failure traces are packaged
- **WHEN** the release-pack workflow builds real-use evidence
- **THEN** it includes or references sanitized traces for ASR unavailable, clarification required, confirmation pending or cancelled, ambiguous visual target, and successful real voice controlled execution

#### Scenario: Failure evidence avoids overclaiming
- **WHEN** public evidence docs describe failure and usage traces
- **THEN** they explain that failures are reliability evidence, not score, model-quality, unrestricted autonomy, or production-readiness claims

### Requirement: Document improved console demo flow
The project SHALL document a command-first Operator Console demo flow that distinguishes controlled live evidence, demo-preview evidence, and optional public-readonly experiments.

#### Scenario: Reviewer follows console demo flow
- **WHEN** a reviewer opens the console demo instructions
- **THEN** they can run a primary command-first flow without needing fixture or execution-mode dropdowns and can still find advanced replay and trace inspection controls

### Requirement: Include controlled showcase evidence
The evidence set SHALL include controlled local showcase evidence for at least one public-site-shaped command if that route is implemented.

#### Scenario: Controlled showcase evidence exists
- **WHEN** the evidence workflow includes a GitHub-shaped controlled showcase task
- **THEN** it includes sanitized trace evidence with controlled target metadata, route decision, final status, browser action evidence, and privacy-scan status

#### Scenario: Controlled showcase evidence is absent
- **WHEN** the controlled showcase route is not implemented in this change
- **THEN** documentation explicitly says public-site-shaped commands remain demo-preview or optional spike behavior

### Requirement: Preserve preview-vs-live evidence separation
The evidence set SHALL preserve a clear separation between preview, controlled live, real voice controlled, real vision controlled, and optional public-readonly artifacts.

#### Scenario: Release pack classifies routed traces
- **WHEN** the release-pack workflow describes traces produced by route selection
- **THEN** it classifies each trace by route/evidence mode and does not infer live execution only from user-facing command text

#### Scenario: Public-readonly artifact is local-only
- **WHEN** a public-readonly trace exists but has not passed explicit sanitization
- **THEN** it remains local/private and is not included as a public sanitized demo artifact

### Requirement: Define public-readonly smoke evidence
The evidence set SHALL define a small public-readonly smoke set that demonstrates real public webpage operation under the bounded safety contract.

#### Scenario: Public-readonly smoke set is documented
- **WHEN** a reviewer opens the demo evidence documentation
- **THEN** it lists the allowlisted public task ids, target labels, browser intent types, expected safety boundaries, execution mode, and private/public artifact status

#### Scenario: Public-readonly smoke run stops safely
- **WHEN** a public-readonly smoke task reaches login, mutation, private-data, upload, download, or unsupported state
- **THEN** the evidence records the stop as reliability evidence rather than a successful public automation claim

### Requirement: Keep public-readonly evidence private until sanitized
The evidence set SHALL exclude public-readonly runtime traces from public artifacts unless an explicit sanitizer marks them public-safe.

#### Scenario: Release pack scans evidence
- **WHEN** the release-pack workflow encounters a public-readonly trace without public-safe sanitizer approval
- **THEN** it excludes the trace from public artifacts or marks it local/private with a clear reason

#### Scenario: Public-readonly trace is approved
- **WHEN** a public-readonly trace passes the explicit public-readonly sanitizer
- **THEN** the public artifact records evidence mode, target label, sanitized origin, final status, stop or failure reason, privacy-scan status, and limitations

### Requirement: Avoid public-readonly overclaiming
The evidence set SHALL describe public-readonly execution as bounded local evidence, not production automation or unrestricted web autonomy.

#### Scenario: Public evidence page describes public-readonly mode
- **WHEN** public evidence documentation mentions public-readonly execution
- **THEN** it states the allowlist, read-only action limits, private-by-default trace boundary, and non-goals for login, mutation, account automation, and long-horizon browsing

### Requirement: Provide static public evidence page
The project SHALL provide a sanitized static evidence page suitable for local review or static hosting.

#### Scenario: Reviewer opens public evidence page
- **WHEN** a reviewer opens the static public evidence page
- **THEN** it identifies the standalone Voice-to-Browser Agent scope, architecture, evidence modes, sanitized trace directories, release-pack workflow, seed-set workflow, validation commands, demo media contract, and limitations without requiring the Operator Console to run

#### Scenario: Public evidence page avoids raw runtime artifacts
- **WHEN** the page references generated release packs, demo media, traces, or datasets
- **THEN** it links to committed sanitized sources or documented local generation commands and does not require raw runtime outputs, raw recordings, private screenshots, credentials, private URLs, browser profiles, or remote host details

### Requirement: Include real-vision evidence in reviewer handoff
The reviewer evidence handoff SHALL surface real `browser-use-vision` controlled evidence separately from deterministic controlled evidence.

#### Scenario: Release pack includes real-vision evidence
- **WHEN** the release-pack workflow finds a sanitized real-vision controlled trace
- **THEN** the manifest and HTML index classify it with a distinct evidence mode and include provider metadata and privacy-scan status

#### Scenario: Required real-vision evidence is missing
- **WHEN** final public-evidence validation runs without the required sanitized real-vision controlled trace
- **THEN** it fails with a clear missing real-vision evidence reason

### Requirement: Provide short demo media contract
The project SHALL define a 60-90 second demo video or GIF contract for the bounded end-to-end workflow.

#### Scenario: Demo media plan is reviewed
- **WHEN** a reviewer opens the demo media plan
- **THEN** it describes exact steps for spoken or transcript input, normalization, safety gate behavior, visual execution, sanitized trace export, release-pack inspection, and seed-set inspection

#### Scenario: Demo media artifact is public-safe
- **WHEN** a demo video or GIF artifact is committed or referenced by the public evidence page
- **THEN** it contains no raw private recordings, credentials, private URLs, browser profile data, remote host details, or unsanitized runtime screenshots

### Requirement: Provide final project closeout handoff pack
The project SHALL provide a final closeout handoff pack that ties together the bounded MVP evidence, validation commands, generated local artifacts, and archive readiness.

#### Scenario: Reviewer follows closeout checklist
- **WHEN** a reviewer opens the closeout checklist
- **THEN** it identifies the required commands for demo evidence release-pack generation, Speech-to-Task dataset generation, OpenSpec strict validation, full test execution, diff whitespace checks, and git ignored-output review

#### Scenario: Checklist distinguishes committed sources from generated artifacts
- **WHEN** the checklist describes release-pack or adaptation dataset outputs
- **THEN** it states that generated runtime artifacts stay local and points back to committed sanitized trace sources

### Requirement: Provide browser-openable interview briefing
The project SHALL include a browser-openable interview/project briefing derived from repository evidence.

#### Scenario: Reviewer opens briefing locally
- **WHEN** a reviewer opens the briefing HTML file from the repository
- **THEN** it explains the problem, bounded scope, architecture, execution flow, evidence modes, safety and privacy gates, adaptation dataset output, validation surface, limitations, and interview talk track

#### Scenario: Briefing links to evidence sources
- **WHEN** the briefing discusses project claims
- **THEN** it references the README, demo task suite, ablations, video plan, release-pack workflow, adaptation dataset workflow, sanitized trace directories, and OpenSpec validation surface

### Requirement: Guard final handoff positioning
The final handoff pack SHALL preserve bounded Voice-to-Browser Agent positioning and avoid unsupported claims.

#### Scenario: Final handoff wording is checked
- **WHEN** README, closeout checklist, demo docs, or interview briefing are reviewed by automated wording guards
- **THEN** they avoid benchmark, SOTA, production automation, unrestricted autonomy, ASR/TTS quality, model checkpoint, and public raw-dataset claims

#### Scenario: Limitations are stated
- **WHEN** a reviewer reads the briefing
- **THEN** it states that model fine-tuning, expanded dataset collection, public hosting, and broad public-web automation are out of scope for the closeout MVP

### Requirement: Define real public task smoke evidence
The evidence set SHALL define a small real public task smoke set that proves task completion or honest failure under the public-readonly safety contract.

#### Scenario: Public task smoke set is documented
- **WHEN** a reviewer opens public-readonly smoke documentation or fixtures
- **THEN** it lists each task id, target label, allowlist id, browser intent type, task kind, requested slots, expected completion criteria, safety boundaries, execution mode, and private/public artifact status

#### Scenario: Public task smoke run is incomplete
- **WHEN** a smoke task fails, partially completes, or stops due to site variance, timeout, missing selector, login boundary, or policy stop
- **THEN** the evidence records the outcome as reliability evidence rather than a successful public automation claim

### Requirement: Publish only sanitized public task summaries
The public evidence set SHALL exclude raw real public task traces unless public-readonly sanitizer approval passes.

#### Scenario: Release pack encounters private public task trace
- **WHEN** the release-pack workflow sees a public task trace with local/private or pending sanitizer state
- **THEN** it excludes the raw trace from public artifacts or includes only an approved summary explaining target label, sanitized origin, completion state, stop/failure reason, and limitations

#### Scenario: Public task trace is approved
- **WHEN** a public task trace passes explicit public-readonly sanitizer checks
- **THEN** the release-pack manifest and HTML classify it as real public task evidence and include privacy-scan status without exposing raw public page content

### Requirement: Avoid real public task overclaiming
The public evidence documentation SHALL describe real public task execution as bounded, local, read-only, allowlisted, and private-by-default.

#### Scenario: Reviewer reads public evidence docs
- **WHEN** public evidence docs mention real public webpage task execution
- **THEN** they state the allowlist, task-contract boundary, completion verifier, private trace policy, and non-goals for login, mutation, account automation, broad site support, captcha bypass, and long-horizon browsing

### Requirement: Define real GitHub public-readonly smoke evidence
The evidence set SHALL define a local/private real GitHub public-readonly smoke path that is distinct from the controlled GitHub showcase.

#### Scenario: GitHub smoke fixture is documented
- **WHEN** a reviewer opens the public-readonly smoke fixture or demo task documentation
- **THEN** it lists the GitHub task id, target label, allowlist id, browser intent type, task kind, requested slots, URL template or target shape, completion criteria, visual artifact policy, execution mode, and safety boundaries

#### Scenario: Controlled GitHub showcase remains documented
- **WHEN** a reviewer reads GitHub demo documentation
- **THEN** it distinguishes controlled local GitHub showcase evidence from real `github.com` public-readonly evidence and explains when each route is selected

### Requirement: Keep GitHub runtime visuals local until sanitized
The evidence set SHALL exclude raw GitHub runtime screenshots and raw public page traces from public artifacts unless sanitizer approval is explicit.

#### Scenario: Release pack sees GitHub local/private visual artifact
- **WHEN** the release-pack workflow encounters a GitHub public-readonly trace or screenshot marked local/private or sanitizer-pending
- **THEN** it excludes the raw artifact or includes only an approved summary with target label, sanitized origin, completion state, stop/failure reason, and limitations

#### Scenario: GitHub public-readonly smoke is blocked
- **WHEN** GitHub search or repo read is blocked by captcha, login boundary, rate limit, timeout, network failure, or selector drift
- **THEN** the evidence records the outcome as reliability evidence and does not present it as successful public automation

### Requirement: Document visible real GitHub demo flow
The project SHALL document a reviewer-facing local demo flow for seeing real GitHub public-readonly behavior in the Operator Console.

#### Scenario: Reviewer follows visible GitHub demo
- **WHEN** a reviewer follows README or video-plan instructions for the GitHub public-readonly demo
- **THEN** they can enable the GitHub allowlist/task contract, run a bounded command, see the real-page visual result or block state in the console, and understand that artifacts remain local/private

### Requirement: Publish public-readonly reliability matrix summary
The evidence set SHALL include a reviewer-readable public-readonly reliability matrix summary.

#### Scenario: Reviewer opens reliability evidence
- **WHEN** a reviewer opens public evidence documentation or a generated release-pack index
- **THEN** they can inspect each reliability task row with task id, target label, target class, task kind, completion criteria, outcome, observed proof summary, unmet criteria, stop or failure reason, privacy state, sanitizer status, and regression coverage

#### Scenario: Matrix row has local/private runtime evidence
- **WHEN** a reliability matrix row references a trace, screenshot, page text, or public runtime artifact that is not sanitizer-approved
- **THEN** the public evidence includes only an approved summary or local/private marker and does not include raw runtime content

### Requirement: Gate reliability matrix completeness and privacy
The evidence workflow SHALL fail or mark the matrix incomplete when required reliability evidence is missing, ambiguous, malformed, or privacy-unsafe.

#### Scenario: Required outcome class is missing
- **WHEN** the reliability matrix lacks coverage for completed, partial, stopped, failed, or blocked outcome classes
- **THEN** the workflow reports the missing outcome class instead of presenting the matrix as complete

#### Scenario: Private marker is detected
- **WHEN** a candidate reliability summary or release-pack artifact contains raw screenshots, raw page text, cookies, credentials, browser profile paths, local file URIs, private URLs, private data, remote host details, or unsanitized runtime fields
- **THEN** the workflow exits non-zero or marks the row sanitizer-failed and does not present it as public-ready

### Requirement: Preserve bounded public-readonly positioning
The public evidence documentation SHALL describe the reliability matrix as bounded local read-only evidence, not production automation, broad public-web autonomy, or benchmark ranking.

#### Scenario: Reviewer reads matrix limitations
- **WHEN** public evidence docs describe the public-readonly reliability matrix
- **THEN** they state the allowlist, task-contract boundary, completion verifier, private-by-default trace policy, and non-goals for arbitrary URLs, login, mutation, account automation, captcha bypass, long-horizon browsing, production deployment, and benchmark claims
