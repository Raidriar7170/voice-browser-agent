## Why

The MVP now has bounded execution, sanitized traces, and a reproducible demo evidence release pack, but Speech-to-Task Adaptation is still only represented by single trace-derived examples. The next phase should turn the existing sanitized execution evidence into a curated, auditable adaptation dataset contract without jumping straight to model fine-tuning or benchmark claims.

## What Changes

- Add a dataset-building workflow that derives Speech-to-Task adaptation examples from checked-in sanitized Execution Traces and, optionally, the demo evidence release-pack manifest.
- Produce a machine-readable dataset manifest and JSONL-style example export with stable example ids, source trace provenance, transcript inputs, normalized targets, validator outcomes, final statuses, safety flags, language metadata, and privacy-scan status.
- Support a human correction overlay for accepted browser tasks and clarification targets while preserving the original trace-derived target for auditability.
- Add dataset quality gates for missing transcript or normalized output, duplicate example ids, malformed corrections, unsafe source traces, and private runtime markers.
- Document the dataset as local adaptation evidence, not a public benchmark, model-quality claim, ASR/TTS training set, or unrestricted web-autonomy corpus.
- Do not add model training, checkpoint export, remote GPU jobs, public raw audio, raw screenshots, browser profiles, credentials, private URLs, or unsanitized live traces.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `trace-derived-training-examples`: Extend single-example derivation into a curated dataset workflow with provenance, correction overlays, dataset manifests, and privacy/quality gates.

## Impact

- Affects trace-derived training example utilities, dataset builder scripts, sanitized trace fixture handling, docs, tests, and the `trace-derived-training-examples` OpenSpec capability.
- May read the generated demo evidence release-pack manifest as an optional input, but generated release artifacts remain local and ignored.
- Does not change browser execution behavior, the normalizer/validator contract, ASR/TTS adapter behavior, `browser-use-vision` dependency boundaries, or public demo evidence claims.
