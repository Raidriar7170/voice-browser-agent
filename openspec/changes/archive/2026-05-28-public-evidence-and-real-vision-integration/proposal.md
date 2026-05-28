## Why

The standalone Voice-to-Browser Agent MVP is functionally complete, but its resume and reviewer story still needs higher-signal evidence that the system is more than a deterministic demo wrapper. This change adds a focused evidence layer: one real `browser-use-vision` controlled trace, a public-safe evidence page, a short demo/GIF artifact contract, and a modest Speech-to-Task seed set.

## What Changes

- Add a controlled-page evidence path that invokes real `browser-use-vision` visual grounding code through the package dependency boundary and exports a sanitized trace distinct from deterministic controlled traces.
- Add a public-safe static evidence page that summarizes the standalone project, evidence modes, sanitized traces, release-pack workflow, validation surface, demo media contract, and limitations.
- Add a 60-90 second demo video/GIF artifact contract that specifies the exact end-to-end walkthrough: spoken or transcript input, normalization, safety gate, visual execution, sanitized trace/export, release-pack inspection, and seed-set inspection.
- Extend the local Speech-to-Task adaptation workflow to produce a modest 20-50 example seed set from sanitized trace-derived examples plus reviewed correction or variant overlays.
- Preserve the current project boundary: `voice-browser-agent` remains an independent bounded application and `browser-use-vision` remains the Visual Grounding Engine dependency.
- Do not add model fine-tuning, checkpoint publication, raw public datasets, broad public-web automation, production automation claims, or benchmark/SOTA claims.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `safe-browser-execution`: Add a real `browser-use-vision` controlled evidence path with honest availability and privacy gates.
- `demo-evidence-set`: Add a static public evidence page and short demo/GIF artifact contract, and surface real-vision evidence in the release handoff.
- `trace-derived-training-examples`: Extend the dataset workflow into a modest 20-50 example Speech-to-Task seed set with correction/variant provenance and bounded positioning.

## Impact

- Affects controlled evidence generation, sanitized trace fixtures, release-pack classification, public/static evidence docs, demo media docs, dataset/seed-set builder behavior, privacy scans, tests, and OpenSpec specs.
- May add a narrow adapter or script that calls installed `browser-use-vision` modules such as SoM annotation, visual grounding backend interfaces, or `VisionEnhancedAgent`-compatible evidence extraction on controlled local pages.
- Does not change the spoken-command normalizer contract, validator rules, confirmation gate semantics, ASR/TTS adapter boundaries, or local-first browser execution policy.
- Does not require remote GPU inference, model training, live public-web automation, or public raw recordings.
