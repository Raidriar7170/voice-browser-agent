## Context

`voice-browser-agent` now has a command-first Operator Console, deterministic route selection, controlled local live execution, reviewed audio provenance, `browser-use-vision` evidence, and sanitized traces. Public-site-shaped commands currently route to controlled local pages or demo-preview output. That keeps evidence safe, but it leaves the project short of the user's next goal: a complete agent that can actually operate real webpages.

The design keeps the original bounded-agent promise. Public webpage operation becomes a narrow, opt-in, read-only execution mode with explicit allowlists, local isolated browser contexts, short budgets, safety stops, and private-by-default traces. It is not a logged-in web automation feature.

## Goals / Non-Goals

**Goals:**

- Add a `live_public_readonly` mode for stable allowlisted public pages.
- Preserve the normalize -> validate -> confirm -> route -> execute -> trace flow.
- Keep controlled local routes as the default public evidence path.
- Run public browser sessions locally in isolated Playwright contexts without persistent profiles, cookies, or login reuse.
- Stop before mutation boundaries such as login, posting, checkout, submit, upload, download, private data entry, or irreversible actions.
- Record useful private execution evidence: route decision, visited origin, page title, action timeline, grounding references, final status, stop/failure reason, and sanitization state.
- Let the Operator Console explain whether a public command is executable, preview-only, controlled-showcase, unsupported, or private public-readonly evidence.

**Non-Goals:**

- No unrestricted public-web autonomy, long-horizon browsing, account login, purchases, posting, deletion, private-data entry, file upload/download, or persistent user browser profile reuse.
- No public claim that public-readonly traces are publishable until sanitizer checks pass.
- No production-grade website compatibility layer, anti-bot bypass, captcha handling, or credential management.
- No remote browser execution; remote services remain limited to optional ASR or visual inference.
- No benchmark, leaderboard, or SOTA framing.

## Decisions

1. **Introduce `live_public_readonly` as a separate execution mode**

   Public-readonly execution should not overload `live_controlled`. The trace must show that the browser touched a real public origin, and the privacy boundary is different from controlled local evidence. A dedicated mode keeps route decisions, UI labels, tests, and evidence packaging honest.

   Alternative considered: treat allowlisted public pages as another controlled fixture. Rejected because real public webpages have network variance, external URLs, and privacy implications that controlled fixtures do not.

2. **Gate public execution through backend route selection**

   The route selector should decide public-readonly eligibility after normalization, validation, and confirmation checks. Manual UI dropdowns or client-side overrides must not force a public command into live execution. This keeps transcript, fixture, reviewed audio, and API calls under the same safety contract.

   Alternative considered: expose a console toggle that directly selects public-readonly. Rejected because it duplicates policy in the UI and makes safety bypass too easy.

3. **Use explicit allowlists and derived URL targets**

   Public-readonly routes should be selected only for configured domains or target templates such as public documentation/search pages. The normalizer may identify intent, but it should not cause arbitrary URL navigation. The route decision records a sanitized origin or target label, not private URLs.

   Alternative considered: let the LLM or normalizer emit any URL. Rejected because it creates open navigation and public trace leakage risk.

4. **Run public sessions in isolated ephemeral contexts**

   The executor should create a fresh Playwright context for each run, avoid persistent browser profile paths, clear storage by construction, and reject non-HTTP(S), file, localhost, private network, and credential-bearing URLs unless they are explicitly controlled local routes. It should set a short max-step budget and small timeout envelope.

   Alternative considered: reuse the user's browser profile for more realistic access. Rejected because cookies, logged-in state, and personal data would immediately break the project's public-safe evidence boundary.

5. **Add a small policy engine before and during execution**

   Public-readonly actions should be restricted to navigation, search-field fill on allowlisted pages, read-only click/expand/filter controls, and visible information extraction. The executor should stop before form submit, login, checkout, posting, deletion, upload/download, private input, or sensitive browser state. Policy decisions should be testable independently from Playwright.

   Alternative considered: rely only on existing keyword stop checks. Rejected because real public pages need action-level constraints and URL/protocol checks before navigation.

6. **Keep public-readonly traces private until sanitized**

   Public-readonly traces are useful local evidence, but they may contain real URLs, page titles, screenshots, or third-party content. The release-pack builder should not include them by default. A sanitizer must explicitly mark a trace as public-safe before it enters committed docs or public evidence pages.

   Alternative considered: commit all public-readonly traces after key filtering. Rejected because third-party page content and screenshots need stricter review than controlled local traces.

## Risks / Trade-offs

- **Public pages are unstable** -> Start with 2-3 stable allowlisted tasks and keep failures as private reliability evidence.
- **Safety policy blocks useful tasks** -> Prefer conservative stops first; expand action classes only with targeted tests and sanitized examples.
- **Trace privacy is harder than controlled demos** -> Keep runtime traces ignored and require an explicit public-readonly sanitizer before publication.
- **Route selector misclassifies a public command** -> Expose route reasons and add tests for allowlisted, non-allowlisted, unsafe, and manual-override cases.
- **Browser automation hits bot/captcha/network issues** -> Treat those as stopped or failed evidence; do not add bypass logic.
- **Scope drifts toward general agent platform** -> Keep one-command execution, local browser, bounded intent types, and no login or mutation.

## Migration Plan

1. Add models/config for `live_public_readonly`, public route metadata, allowlist entries, and private/public evidence state.
2. Add public-readonly policy tests before implementing route/executor changes.
3. Implement backend route selection for allowlisted public commands while preserving current controlled and preview routes.
4. Implement an isolated public-readonly executor adapter with safety checks, action evidence, and missing-evidence failure behavior.
5. Update trace writing/export and release-pack logic so public-readonly traces remain local/private unless explicitly sanitized.
6. Update Operator Console readiness, route/evidence panels, docs, and public evidence explanations.
7. Generate or document a tiny local private smoke set, then validate with OpenSpec, targeted tests, full pytest, and privacy scans.

Rollback is straightforward: keep `live_public_readonly` disabled by default, and route all public commands back to controlled-showcase or demo-preview if the policy or executor fails validation.

## Open Questions

- Which first allowlisted public pages are stable enough: OpenAI docs, Python docs, MDN, Wikipedia, or GitHub public search?
- Should the first implementation perform real `browser-use-vision` grounding on public pages, or begin with Playwright page-state evidence plus the existing visual dependency metadata?
- Should sanitized public-readonly artifacts ever be committed in this change, or should the first change only produce private runtime traces and sanitizer tests?
