# Useful Local Scenarios

This small scenario pack moves beyond one-off visual fixtures while staying inside controlled local workflows. The goal is to show realistic operator intent, safety behavior, and trace evidence without credentials, external sites, or unstable public pages.

These scenarios are not broad public-web automation. They are local controlled pages that exercise common browser-agent patterns:

| Scenario | Local Page | Intent Type | Safety Behavior | Evidence Mode | Privacy Boundary |
| --- | --- | --- | --- | --- | --- |
| CRM filter | `demo/pages/crm_filter.html` | `select_filter` | Non-destructive filter selection only | `real_use_failure` or controlled local trace | local controlled page |
| Settings toggle | `demo/pages/settings_toggle.html` | `fill_form` | Confirmation before any irreversible setting | `real_use_failure` or controlled local trace | local controlled page |
| Metrics dashboard | `demo/pages/metrics_dashboard.html` | `extract_compare_info` | Read-only visible-data extraction | `real_use_failure` or controlled local trace | local controlled page |
| Controlled code search | `demo/pages/github_showcase.html` | `search_open` | Local public-site-shaped route only | `controlled_showcase` inside live trace metadata | local controlled page |
| Public docs lookup | allowlisted public docs URL | `search_open` | No login; read-only navigation or extraction only | `live_public_readonly` with local private trace | private-by-default until sanitized |

The pack is intentionally small. It proves the app shape that matters for real use: preflight readiness, ASR review, bounded normalization, safety gates, local visual execution, and sanitized failure or usage traces.

The public-readonly lane is intentionally narrower than unrestricted public-web autonomy: it starts with allowlisted documentation/reference targets and rejects arbitrary transcript URLs, mutation actions, private-network targets, and sensitive browser states.
