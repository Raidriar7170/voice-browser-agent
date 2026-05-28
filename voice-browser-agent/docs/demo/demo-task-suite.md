# Demo Task Suite

This suite is a reproducible evidence set for a bounded Voice-to-Browser Agent. It is a scoped demo for single-command browser execution with traceable safety stops, not a public ranking or unrestricted web-autonomy claim.

| ID | Audio fixture | Target | Browser intent type | Visual grounding | Stop condition | Expected final status |
| --- | --- | --- | --- | --- | --- | --- |
| github-search | `fixtures/audio/github-search.fixture.json` | Public GitHub search | `search_open` | No | `login_required` | `stopped` in demo preview |
| icon-search | `fixtures/audio/icon-search.fixture.json` | `demo/pages/icon_only_toolbar.html` | `click_visual_target` | Yes, icon-only toolbar | `login_required` | `stopped` in demo preview |
| color-swatch | `fixtures/audio/color-swatch.fixture.json` | `demo/pages/color_swatch.html` | `select_filter_or_option` | Yes, color swatch | `irreversible_submit` | `stopped` in demo preview |
| svg-dashboard | `fixtures/audio/svg-dashboard.fixture.json` | `demo/pages/svg_dashboard.html` | `extract_compare_visible_info` | Yes, SVG chart | `login_required` | `stopped` in demo preview |
| checkout-stop | `fixtures/audio/checkout-stop.fixture.json` | `demo/pages/ecommerce_stop.html` | `fill_form` | No | `payment_or_checkout` | `pending_confirmation` |
| ambiguous | `fixtures/audio/ambiguous.fixture.json` | None | clarification | No | none | `clarification_required` |
| openai-public | `fixtures/audio/openai-public.fixture.json` | Public OpenAI docs | `search_open` | No | `login_required` | `stopped` in demo preview |
| dashboard-compare | `fixtures/audio/dashboard-compare.fixture.json` | Controlled dashboard card view | `extract_compare_visible_info` | Yes, colored cards | `login_required` | `stopped` in demo preview |

Four of the eight tasks are visual-grounding-heavy: icon-only toolbar, color swatch, SVG dashboard, and dashboard card comparison. The controlled pages are adapted from the same visual UI scenarios used by `browser-use-vision/demo`: icon-only controls, color swatches, SVG/canvas-like chart content, dynamic dashboard cards, and ecommerce stop states.

Public showcase tasks are limited to non-destructive browsing of public pages and must stop before login, checkout, payment, deletion, posting, private-data entry, file transfer, or irreversible submission.

The Operator Console v2 adds route-aware controlled showcase behavior for GitHub-shaped commands. A command such as "打开 GitHub" may execute `demo/pages/github_showcase.html` as controlled local live evidence, with the route decision recorded separately from the normalized command text. This does not claim that a real public website was operated.

`live_public_readonly` is the first real public-web execution lane, but only for allowlisted public read-only pages such as docs or reference material. A configured task-contract and completion verifier must match before execution can be reported as complete. No login, upload, download, purchase, posting, private-data entry, or destructive submission is in scope. Traces are private-by-default and use `local_private_until_sanitized` artifact status unless a sanitizer pass marks them public-safe; this is not unrestricted public-web autonomy.

The initial public-readonly smoke fixture is `fixtures/public-readonly-smoke.json`. It records `openai-docs-overview`, `python-docs-search`, and `mdn-readonly-reference` with task kind, allowed slots, completion criteria, execution mode, safety boundaries, and private/public artifact status. OpenAI Docs remains a conservative direct-read docs target, while GitHub public search stays a later or controlled-showcase target because login, captcha, UI drift, and anti-bot boundaries make it less stable for a required smoke.

The checked-in preview traces in `fixtures/traces/sanitized/` are generated in explicit demo-preview mode. A preview trace uses `demo_preview_not_executed` when the browser was not launched.

Live controlled traces belong in `fixtures/traces/live-sanitized/`. These artifacts are separate from preview traces, must be marked with `execution_mode: live_controlled`, and may report `succeeded`, `failed`, or `stopped` as long as the trace includes action evidence or grounding evidence plus an explicit failure or stop reason. The first required live controlled targets are `icon-search` and `color-swatch`; `svg-dashboard` is the optional third controlled visual task.

Controlled showcase traces also live in `fixtures/traces/live-sanitized/`, but they are not part of the required visual-grounding completeness set. They must include `route_decision` metadata so reviewers can distinguish controlled local evidence from real public-site execution.

agentic live-controlled traces belong in `fixtures/traces/agentic-sanitized/`. These artifacts are separate from both demo-preview traces and earlier live-controlled action-list traces. They must include `execution_style: agentic_vision`, step-level observation/action/verification evidence, sanitized grounding references, and no raw audio, raw screenshots, browser profile data, credentials, private URLs, or remote host details.
