## 1. Public-Readonly Contract Tests

- [x] 1.1 Add model/schema tests for `live_public_readonly` execution mode, route type, public target metadata, allowlist id, evidence privacy state, and sanitizer status.
- [x] 1.2 Add route-selection tests for enabled allowlisted public commands, disabled public-readonly commands, non-allowlisted targets, unsafe commands, and manual override bypass attempts.
- [x] 1.3 Add public-readonly policy tests for URL/protocol checks, private-network blocking, mutation-action blocking, login/submit/upload/download stops, and short step budgets.
- [x] 1.4 Add executor tests proving public-readonly runs use isolated browser contexts, reject missing evidence, and preserve action/page-state evidence without leaking profile or cookie data.

## 2. Configuration and Routing

- [x] 2.1 Extend runtime config and `.env.example` with disabled-by-default public-readonly enablement, allowlist entries, max step count, timeout budget, and sanitizer policy.
- [x] 2.2 Extend `ExecutionMode`, `RouteType`, `RouteDecision`, and trace/runtime metadata for public-readonly routes and private/public evidence state.
- [x] 2.3 Implement allowlist parsing and deterministic public target matching without accepting arbitrary transcript-emitted URLs.
- [x] 2.4 Wire route selection so public commands choose controlled local, public-readonly, preview-only, clarification, confirmation, or blocked routes with user-visible explanations.

## 3. Safety Policy Engine

- [x] 3.1 Add a public-readonly policy module for allowed origins, URL safety, action classes, sensitive DOM/browser-state detection, and unsupported-route reasons.
- [x] 3.2 Integrate policy checks before navigation, before each action, and after each observation.
- [x] 3.3 Extend sanitizer/private-key handling for public URLs, raw page text, raw screenshots, cookies, profile paths, local file URIs, and third-party private markers.
- [x] 3.4 Ensure unsafe public-readonly requests stop or block before browser action and record the precise policy reason.

## 4. Public-Readonly Executor

- [x] 4.1 Add a Playwright public-readonly executor adapter that creates one fresh isolated local browser context per execution.
- [x] 4.2 Implement bounded read-only interactions for the first smoke targets, such as documentation search, read-only navigation, expandable sections, and visible information extraction.
- [x] 4.3 Record browser action events, sanitized origin or target label, page title, grounding references when available, final status, and stop/failure reason.
- [x] 4.4 Preserve existing controlled-live, agentic-live, real-voice, demo-preview, and confirmation behaviors while adding the new executor path.

## 5. Operator Console and API

- [x] 5.1 Extend readiness API/preflight output with public-readonly enabled state, allowlist summary, isolation readiness, sanitizer readiness, and recommended actions.
- [x] 5.2 Update execution API responses so public-readonly route decisions and private evidence status render consistently with existing route panels.
- [x] 5.3 Update Operator Console UI to display public-readonly readiness, target label, allowlist id, private trace state, execution limits, stop/failure reasons, and sanitizer export status.
- [x] 5.4 Run desktop and mobile browser screenshot checks to verify the new UI state has no clipped text, overlap, or misleading success styling.

## 6. Evidence and Documentation

- [x] 6.1 Define 2-3 initial public-readonly smoke tasks in docs and fixtures using stable public read-only targets.
- [x] 6.2 Update README, demo task docs, useful scenario docs, public evidence docs, and video plan with public-readonly boundaries and non-goals.
- [x] 6.3 Update release-pack builder so unsanitized public-readonly traces are excluded or clearly marked local/private.
- [x] 6.4 Add optional sanitized public-readonly evidence only if privacy checks pass; otherwise document private smoke evidence without committing raw runtime traces.

## 7. Verification

- [x] 7.1 Run targeted public-readonly route, policy, executor, sanitizer, operator console, and evidence tests.
- [x] 7.2 Run `openspec validate live-public-readonly-web-execution --strict`.
- [x] 7.3 Run `openspec validate --all --strict`.
- [x] 7.4 Run `uv run pytest` from `voice-browser-agent/`.
- [x] 7.5 Run `git diff --check` and inspect `git status --short --ignored` for ignored runtime traces, raw screenshots, browser profiles, uploads, and caches.
