# Useful Local Scenarios

This small scenario pack moves beyond one-off visual fixtures while staying inside controlled local workflows. The goal is to show realistic operator intent, safety behavior, and trace evidence without credentials, external sites, or unstable public pages.

These scenarios are not broad public-web automation. They are local controlled pages that exercise common browser-agent patterns:

| Scenario | Local Page | Intent Type | Safety Behavior | Evidence Mode | Privacy Boundary |
| --- | --- | --- | --- | --- | --- |
| CRM filter | `demo/pages/crm_filter.html` | `select_filter` | Non-destructive filter selection only | `real_use_failure` or controlled local trace | local controlled page |
| Settings toggle | `demo/pages/settings_toggle.html` | `fill_form` | Confirmation before any irreversible setting | `real_use_failure` or controlled local trace | local controlled page |
| Metrics dashboard | `demo/pages/metrics_dashboard.html` | `extract_compare_info` | Read-only visible-data extraction | `real_use_failure` or controlled local trace | local controlled page |
| Controlled code search | `demo/pages/github_showcase.html` | `search_open` | Local public-site-shaped route only | `controlled_showcase` inside live trace metadata | local controlled page |
| Public docs lookup | allowlisted public docs URL | `search_open` | Requires task-contract match, completion verifier proof, and No login/read-only actions | `live_public_readonly` with local private trace | private-by-default until sanitized |
| Public package metadata | allowlisted PyPI or npm package URL | `extract_compare_info` | Requires package task contract, package-name proof, No login, and no download action | useful task-pack summary | local/private until sanitized |
| Public release notes | allowlisted public releases URL | `extract_compare_info` | Requires release-notes task contract, repository proof, No login, and no write-capable repository action | useful task-pack summary | local/private until sanitized |
| Real GitHub repository search | `https://github.com/search?q={search_query}&type=repositories` | `search_open` | Requires GitHub allowlist, `github-repo-search` contract, No login, and no account mutation | visible result panel plus local private screenshots | local/private until sanitized |
| Real GitHub public repo read | `https://github.com/{owner}/{repo}` | `extract_compare_visible_info` | Requires explicit owner/repo slots and `github-public-repo-read` contract | visible result panel plus repo-read proof | local/private until sanitized |

The pack is intentionally small. It proves the app shape that matters for real use: preflight readiness, ASR review, bounded normalization, safety gates, local visual execution, and sanitized failure or usage traces.

The public-readonly lane is intentionally narrower than unrestricted public-web autonomy: it starts with allowlisted documentation/reference targets plus explicit GitHub public repository search/read contracts, and rejects arbitrary transcript URLs, mutation actions, private-network targets, missing task contracts, and sensitive browser states. Incomplete public tasks are recorded as partial, stopped, failed, or blocked instead of successful live public automation.

The public-readonly reliability matrix is the compact reviewer summary for those outcomes. The public-readonly useful task pack broadens the same local/private contract to package metadata and release notes while preserving task-specific completion proof. Both summaries explicitly exclude production-use claims, verification-barrier bypassing, account workflows, ranking claims, model-quality claims, and raw public evidence releases.
