# Demo Video Plan

Target length: 60-90 seconds. Use controlled fixtures and sanitized generated
artifacts only. Do not show raw recordings, raw screenshots, browser profiles,
credentials, private URLs, remote host details, or unsanitized runtime folders.

1. Open the Operator Console locally.
2. Run a transcript demo by pasting a fixture transcript into the transcript control.
3. Run fixture replay for `github-search` in `demo_preview` mode and show that public showcase evidence is preview-only.
4. Run fixture replay for `icon-search` or `color-swatch` in `live_controlled` mode and show controlled local-page action and grounding evidence.
5. Point to `fixtures/traces/real-vision-sanitized/real-vision-icon-search.json` and show the `real_vision_controlled` provider/adapter metadata from `browser_use_vision.som.annotate_screenshot`.
6. Upload or record one supported audio command, then run the stored audio command from the audio execution control.
7. Run `ambiguous` and show the Clarification Request without browser execution.
8. Run `checkout-stop` and show the Confirmation Gate prompt before any sensitive action.
9. Cancel the confirmation and show the final sanitized trace export.
10. Run `uv run python scripts/build_demo_evidence_pack.py`.
11. Open `runtime/demo-evidence-release-pack/index.html` and show the generated evidence index.
12. Inspect `runtime/demo-evidence-release-pack/manifest.json` and point back to the committed sanitized trace folders.
13. Run `uv run python scripts/build_speech_to_task_dataset.py --seed-set`.
14. Inspect `runtime/speech-to-task-adaptation-dataset/manifest.json` and `runtime/speech-to-task-adaptation-dataset/examples.jsonl` as local Speech-to-Task adaptation preparation evidence.
15. Close with the sanitized trace artifact and quick reminder that raw recordings and private traces stay local.
