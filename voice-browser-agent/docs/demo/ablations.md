# Demo Ablations

These ablations explain module value without presenting ranked evaluation results.

## Visual Grounding Disabled

Task: click the icon-only search control in `demo/pages/icon_only_toolbar.html`.

Expected limitation: a text-only browser executor can see toolbar structure but lacks enough visual evidence to distinguish the icon-only search button from adjacent icon-only controls. The trace should mark missing or weak grounding evidence rather than claiming a score.

## Normalizer and Validator Removed

Task: run the noisy transcript `打开那个页面`.

Expected limitation: raw transcript execution is ambiguous because the target page is missing. With the normalizer and validator enabled, the system returns a Clarification Request and does not start browser execution.

## Confirmation Gate Triggered

Task: `帮我结账并提交付款`.

Expected limitation: the command is safety-sensitive. The Confirmation Gate pauses before execution and records `pending_confirmation`; if the operator cancels, the trace records `cancelled` and `operator_cancelled`.

## Re-observation Removed

Task: click the icon-only search control after a stale visual observation.

Expected limitation: without re-observation, the executor may keep acting on a stale target and stop with no meaningful progress. With agentic re-observation enabled, the trace records the stale/no-effect step, observes the current page again, and either selects the fresh target or stops with an explicit reason.

## Visual Target Resolution Removed

Task: select the green swatch in `demo/pages/color_swatch.html`.

Expected limitation: without visual target resolution, the executor cannot justify which swatch matches the spoken color reference. With visual grounding enabled, the agentic trace records the selected target reference and grounding evidence before the click.
