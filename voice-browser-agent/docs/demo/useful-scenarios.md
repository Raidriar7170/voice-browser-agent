# Useful Local Scenarios

This small scenario pack moves beyond one-off visual fixtures while staying inside controlled local workflows. The goal is to show realistic operator intent, safety behavior, and trace evidence without credentials, external sites, or unstable public pages.

These scenarios are not broad public-web automation. They are local controlled pages that exercise common browser-agent patterns:

| Scenario | Local Page | Intent Type | Safety Behavior | Evidence Mode | Privacy Boundary |
| --- | --- | --- | --- | --- | --- |
| CRM filter | `demo/pages/crm_filter.html` | `select_filter` | Non-destructive filter selection only | `real_use_failure` or controlled local trace | local controlled page |
| Settings toggle | `demo/pages/settings_toggle.html` | `fill_form` | Confirmation before any irreversible setting | `real_use_failure` or controlled local trace | local controlled page |
| Metrics dashboard | `demo/pages/metrics_dashboard.html` | `extract_compare_info` | Read-only visible-data extraction | `real_use_failure` or controlled local trace | local controlled page |

The pack is intentionally small. It proves the app shape that matters for real use: preflight readiness, ASR review, bounded normalization, safety gates, local visual execution, and sanitized failure or usage traces.
