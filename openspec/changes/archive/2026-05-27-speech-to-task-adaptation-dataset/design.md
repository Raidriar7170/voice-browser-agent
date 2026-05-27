## Context

The current project already records transcript, normalized output, validator decision, final status, and sanitized trace evidence for demo-preview, live-controlled, and agentic runs. It also has `training_example_from_trace()` for converting one Execution Trace into one sanitized Trace-Derived Training Example. The missing layer is a reproducible dataset workflow: a reviewer or future training job cannot yet ask "which sanitized examples are in this adaptation set, why were they included, which ones were corrected, and did privacy/quality checks pass?"

This phase keeps the work local and evidence-oriented. It should prepare Speech-to-Task Adaptation inputs without adding a fine-tuning job, remote GPU workflow, benchmark table, or public raw dataset.

## Goals / Non-Goals

**Goals:**

- Build a deterministic local dataset artifact from checked-in sanitized trace sources.
- Emit both a manifest for audit/automation and JSONL examples for downstream adaptation experiments.
- Preserve source trace provenance, evidence mode, transcript metadata, normalized target, validator decision, final status, safety flags, and privacy-scan status.
- Allow optional human correction overlays without losing the original trace-derived target.
- Fail fast on missing adaptation inputs, duplicate ids, malformed corrections, and privacy-unsafe content.
- Document the dataset as bounded local adaptation evidence.

**Non-Goals:**

- Do not train, evaluate, or publish a model checkpoint.
- Do not claim ASR/TTS quality, benchmark scores, SOTA results, or production autonomy.
- Do not collect new raw audio, raw screenshots, browser profiles, credentials, private URLs, remote host details, or unsanitized runtime traces.
- Do not require the remote A100 machine for this phase.
- Do not change browser execution, visual grounding, normalizer, validator, or ASR adapter behavior unless a trace field is already present but not exported.

## Decisions

### Build a local dataset script over sanitized traces

Add a small script, for example `scripts/build_speech_to_task_dataset.py`, that reads checked-in sanitized trace directories and writes generated artifacts under a local runtime output directory. The script can optionally consume the demo evidence release-pack manifest when present, but it must still be able to derive the dataset from committed sanitized traces.

Alternatives considered:

- Build through the Operator Console: convenient for demos, but couples dataset creation to a live UI session and weakens reproducibility.
- Add remote training orchestration now: premature because the dataset contract, corrections, and quality gates are not yet stable.

### Use manifest plus JSONL

The manifest should summarize the dataset as a whole: generated timestamp, source directories or release manifest path, example count, evidence-mode counts, correction count, privacy-scan status, and per-example provenance. The JSONL file should be the adaptation-ready example stream.

Alternatives considered:

- JSONL only: useful for training, but weak for review and CI-style checks.
- Manifest only: auditable, but awkward for downstream adaptation experiments.

### Keep corrections as an overlay

Human corrections should live in an optional separate file keyed by source execution id or stable example id. The builder should include both the original trace-derived target and the corrected target plus correction metadata, so the dataset remains auditable.

Alternatives considered:

- Mutate sanitized traces directly: destroys the distinction between observed evidence and reviewer correction.
- Replace the target silently: cleaner for training, but bad for traceability.

### Treat privacy and quality checks as gates

The builder should reuse existing sanitization/privacy scanning patterns where possible and exit non-zero when source traces, corrections, generated manifest, or generated JSONL contain forbidden private markers. It should also reject examples that lack transcript or normalized output, corrections that do not match an included example, and duplicate stable ids.

Alternatives considered:

- Warn but continue: too easy to publish unsafe or unusable artifacts.
- Only test the single-example helper: insufficient because dataset assembly can introduce drift or private correction fields.

## Risks / Trade-offs

- Dataset scope can creep into training claims -> keep docs and output wording focused on local adaptation inputs and explicitly exclude model-quality claims.
- Correction overlays can introduce private data -> scan corrections before writing generated artifacts and keep correction metadata minimal.
- Stable ids can change if paths move -> derive ids from source execution id plus evidence mode rather than absolute file paths.
- Release-pack manifest may not exist -> make it optional and document the committed trace-directory fallback.
- Quality gates can block partially useful examples -> fail by default and allow future explicit exclusion manifests if a later phase needs them.

## Migration Plan

This is additive. Existing single-example helpers, sanitized traces, release-pack builder, and demo docs remain valid. Generated dataset outputs should stay under a local ignored directory. If the dataset builder fails, existing demo evidence and release packaging are unaffected.

## Open Questions

None for this phase. Defer model training, dataset size expansion, remote GPU runs, and model evaluation until the dataset contract is implemented and reviewed.
