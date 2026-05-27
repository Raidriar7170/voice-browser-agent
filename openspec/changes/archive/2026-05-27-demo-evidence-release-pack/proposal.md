## Why

The project can now demonstrate transcript, fixture, uploaded-audio, preview, live-controlled, and agentic evidence paths, but the public handoff still depends on a reviewer manually finding traces, docs, and privacy guarantees across several folders. The next phase should package the existing bounded MVP evidence into one reproducible release artifact so interviews and repo review can focus on evidence rather than navigation.

## What Changes

- Add a release-pack workflow that gathers selected sanitized demo-preview, live-controlled, and agentic trace artifacts into one versioned evidence bundle.
- Generate a machine-readable manifest that records fixture ids, execution modes, trace paths, final statuses, stop/failure reasons, grounding references, and privacy-scan results.
- Generate a browser-openable HTML evidence index for interview walkthroughs and reviewer handoff.
- Add a privacy and completeness check that fails when raw audio paths, browser profile data, cookies, credentials, private URLs, remote host details, or missing required evidence appear in the release pack.
- Document how to build and inspect the evidence pack without claiming benchmark, SOTA, production automation, or unrestricted public-web autonomy.
- Do not add new ASR/TTS model capability, model fine-tuning, remote browser execution, public-web live automation, or benchmark scoring.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `demo-evidence-set`: Extend the public evidence contract with a reproducible release pack, manifest, HTML index, completeness checks, and privacy checks.

## Impact

- Affects demo evidence scripts, sanitized trace packaging, demo documentation, README handoff instructions, tests, and the `demo-evidence-set` OpenSpec capability.
- Does not change the core normalizer, validator, ASR adapters, trace schema, live-controlled task set, `browser-use-vision` dependency boundary, or Operator Console runtime behavior unless needed to read existing sanitized trace metadata.
