# Demo Video Plan

Target length: 60-90 seconds. Use controlled fixtures and sanitized generated
artifacts only. Do not show raw recordings, raw screenshots, browser profiles,
credentials, private URLs, remote host details, or unsanitized runtime folders.

1. Open the Operator Console locally.
2. Run `uv run python scripts/preflight_real_use.py` and show readiness categories.
3. Run a transcript command from the primary command control and show the route decision before the trace JSON.
4. Run `打开 GitHub` with public-readonly disabled and show that it routes to the controlled local code-search showcase instead of a real public website.
5. Open Advanced Replay and run `icon-search` or `color-swatch` in `live_controlled` mode to show reproducible fixture replay.
6. Optional: enable an allowlisted docs or GitHub public-readonly target locally and run one `live_public_readonly` smoke command, emphasizing the task-contract, completion verifier, visible result panel, No login, read-only actions, private-by-default screenshots, and bounded public scope.
7. Point to `fixtures/traces/real-vision-sanitized/real-vision-icon-search.json` and show the `real_vision_controlled` provider/adapter metadata from `browser_use_vision.som.annotate_screenshot`.
8. Upload or record one supported audio command, review and edit the ASR transcript, then run the reviewed audio through the same route-aware command path.
9. Point to `fixtures/traces/real-voice-sanitized/real-voice-icon-search.json` and show audio input source, ASR adapter metadata, transcript review status, and sanitized grounding refs.
10. Run `ambiguous` and show the Clarification Request without browser execution.
11. Run `checkout-stop` and show the Confirmation Gate prompt before any sensitive action.
12. Cancel the confirmation and show the final sanitized trace export.
13. Point to `fixtures/traces/live-sanitized/live-github-showcase.json` and `fixtures/traces/real-use-sanitized/` as controlled-showcase, failure, and operator-decision evidence.
14. Note that real GitHub public search/read now exists only behind explicit public-readonly configuration; controlled showcase evidence remains the stable default, while raw GitHub runtime screenshots remain local/private unless sanitizer-approved.
15. Run `uv run python scripts/build_demo_evidence_pack.py`.
16. Open `runtime/demo-evidence-release-pack/index.html` and show the generated evidence index.
17. Inspect `runtime/demo-evidence-release-pack/manifest.json` and point back to the committed sanitized trace folders.
18. Run `uv run python scripts/build_speech_to_task_dataset.py --seed-set`.
19. Inspect `runtime/speech-to-task-adaptation-dataset/manifest.json` and `runtime/speech-to-task-adaptation-dataset/examples.jsonl` as local Speech-to-Task adaptation preparation evidence.
20. Close with the sanitized trace artifact and quick reminder that raw recordings and private traces stay local.
