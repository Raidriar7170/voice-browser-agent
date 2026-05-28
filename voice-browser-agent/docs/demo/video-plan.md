# Demo Video Plan

Target length: 60-90 seconds. Use controlled fixtures and sanitized generated
artifacts only. Do not show raw recordings, raw screenshots, browser profiles,
credentials, private URLs, remote host details, or unsanitized runtime folders.

1. Open the Operator Console locally.
2. Run `uv run python scripts/preflight_real_use.py` and show readiness categories.
3. Run a transcript demo by pasting a fixture transcript into the transcript control.
4. Run fixture replay for `github-search` in `demo_preview` mode and show that public showcase evidence is preview-only.
5. Run fixture replay for `icon-search` or `color-swatch` in `live_controlled` mode and show controlled local-page action and grounding evidence.
6. Point to `fixtures/traces/real-vision-sanitized/real-vision-icon-search.json` and show the `real_vision_controlled` provider/adapter metadata from `browser_use_vision.som.annotate_screenshot`.
7. Upload or record one supported audio command, review and edit the ASR transcript, preview normalization, then run reviewed audio on the controlled `icon-search` page.
8. Point to `fixtures/traces/real-voice-sanitized/real-voice-icon-search.json` and show audio input source, ASR adapter metadata, transcript review status, and sanitized grounding refs.
9. Run `ambiguous` and show the Clarification Request without browser execution.
10. Run `checkout-stop` and show the Confirmation Gate prompt before any sensitive action.
11. Cancel the confirmation and show the final sanitized trace export.
12. Point to `fixtures/traces/real-use-sanitized/` as failure and operator-decision evidence.
13. Run `uv run python scripts/build_demo_evidence_pack.py`.
14. Open `runtime/demo-evidence-release-pack/index.html` and show the generated evidence index.
15. Inspect `runtime/demo-evidence-release-pack/manifest.json` and point back to the committed sanitized trace folders.
16. Run `uv run python scripts/build_speech_to_task_dataset.py --seed-set`.
17. Inspect `runtime/speech-to-task-adaptation-dataset/manifest.json` and `runtime/speech-to-task-adaptation-dataset/examples.jsonl` as local Speech-to-Task adaptation preparation evidence.
18. Close with the sanitized trace artifact and quick reminder that raw recordings and private traces stay local.
