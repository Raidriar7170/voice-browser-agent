## Context

The repository already has a final local MVP with archived OpenSpec changes,
sanitized trace sources, a release-pack builder, public-readonly task contracts,
normalizer comparison, and Speech-to-Task adaptation evaluation. The public
GitHub front door currently has a lightweight workflow that checks README
markers, license text, JSON parseability, and Python compilation. That workflow
is useful, but it does not reproduce the project-level reliability claims that
the README and interview materials ask reviewers to trust.

The main technical tension is dependency and artifact separation:

- `voice-browser-agent/pyproject.toml` currently resolves `browser-use-vision`
  through a local editable sibling path.
- Full browser, real voice, public-readonly live, and provider-backed checks can
  depend on local runtimes, Playwright browsers, network variance, or private
  artifacts.
- Existing release-pack and evaluation scripts intentionally write generated
  outputs under ignored `runtime/` paths.

This change should therefore make CI more credible without pretending that every
local/private evidence path can or should run in GitHub Actions.

## Goals / Non-Goals

**Goals:**

- Add a GitHub Actions reliability gate that runs OpenSpec validation and a
  deterministic, CI-safe Python test strategy.
- Make dependency resolution explicit for CI so the standalone GitHub checkout
  can validate meaningful behavior without relying on a missing sibling repo.
- Add a local reliability snapshot manifest that summarizes existing evidence
  surfaces and their privacy state.
- Update handoff docs to separate CI-verified checks from local/private generated
  evidence and avoid stale validation counts.
- Keep privacy and bounded-scope wording enforced by tests where practical.

**Non-Goals:**

- Do not add model fine-tuning, checkpoint publication, ASR/TTS evaluation, or a
  public benchmark claim.
- Do not make live public-readonly browsing, real-provider visual verification,
  raw screenshot inspection, or recorded-audio flows mandatory in CI.
- Do not commit generated `runtime/` outputs, browser profiles, raw public traces,
  raw provider payloads, credentials, local paths, or remote host details.
- Do not widen the agent from bounded task contracts into broad public-web
  autonomy.

## Decisions

### Decision 1: Add a separate reliability workflow instead of bloating front-door

Keep `front-door.yml` lightweight and add a new reliability workflow for heavier
project validation. The front-door workflow remains fast and public-surface
oriented; the reliability workflow owns OpenSpec and test evidence.

Alternative considered: expand `front-door.yml` directly. That would mix public
presentation checks with deeper project validation and make the existing badge
less predictable.

### Decision 2: Make CI dependency resolution explicit

CI must not depend on `../../../browser-use-vision` existing next to the checkout.
The implementation should choose one explicit strategy:

- allow installing `browser-use-vision` from a public Git source when available,
- vendor or stub only the narrow CI-tested interface if publication is not ready,
- or split tests so the CI-safe subset excludes import paths that require the
  local editable dependency while still running docs, schemas, privacy guards,
  and deterministic evidence builders.

The selected strategy must be visible in workflow commands and documentation.

Alternative considered: let `uv sync` fail and mark the workflow optional. That
would not create a trustworthy gate.

### Decision 3: Treat the reliability snapshot as a summary, not a new raw evidence source

The snapshot should consume existing committed sanitized traces and optional
local manifests, then emit counts, coverage, command provenance, and privacy
status. It should not copy raw artifacts, screenshots, provider payloads, page
text, local paths, or raw runtime traces into public docs.

Alternative considered: commit a generated snapshot. Keeping it generated avoids
turning local/private runtime state into a stale public artifact.

### Decision 4: Use documentation tests to guard wording drift

Because the project is public-facing and evidence-sensitive, tests should guard
against stale local pass counts, unsupported production/fine-tuning claims, and
missing CI/local distinction in final handoff surfaces.

Alternative considered: rely on manual README review. Prior phases already
showed that stale handoff language is easy to miss.

## Risks / Trade-offs

- [Risk] CI cannot run full `uv run pytest` because `browser-use-vision` is a
  local editable dependency. -> Mitigation: make dependency strategy part of the
  change, and if needed define a CI-safe subset with explicit skipped surfaces.
- [Risk] Snapshot output accidentally leaks local/private fields. -> Mitigation:
  reuse or extend existing privacy scans and add failure tests for local paths,
  raw screenshots, provider payloads, credentials, browser profiles, and
  checkpoint-like paths.
- [Risk] CI badge looks stronger than the evidence it proves. -> Mitigation:
  docs must distinguish front-door, reliability CI, and local/private generated
  evidence.
- [Risk] The phase becomes a release/rewrite phase. -> Mitigation: keep scope to
  gates, snapshot, and handoff wording; defer feature work and model training to
  later OpenSpec changes.

## Migration Plan

1. Create focused tests for workflow shape, dependency strategy, snapshot
   privacy, and final handoff wording.
2. Implement the reliability workflow and local snapshot builder.
3. Update docs to reflect CI/local evidence boundaries.
4. Run local validation, then check the GitHub Actions reliability workflow after
   pushing.

Rollback is straightforward: remove the new workflow and snapshot surfaces while
leaving the existing front-door workflow and local evidence scripts untouched.

## Open Questions

- Should CI install `browser-use-vision` from the public repository, or should
  the first implementation use a smaller CI-safe pytest subset while preserving
  full local validation?
- Should the reliability snapshot remain purely generated under `runtime/`, or
  should a tiny public-safe example manifest be committed later after a separate
  review?
