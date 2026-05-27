## Why

The MVP works, but the current Operator Console makes the demo paths easy to confuse: `Run` executes the free-text transcript path, `Run Fixture` executes selected fixtures, and selecting `live_controlled` beside a public fixture can look like it should launch a live website run even though the bounded MVP only supports live-controlled execution for selected local demo pages. The next phase should improve demo clarity before adding more agent capability.

## What Changes

- Make the Operator Console clearly distinguish transcript execution, fixture replay, upload/recording execution, demo-preview mode, and live-controlled mode.
- Expose fixture metadata in the UI so unsupported live-controlled fixture selections are disabled or explained before execution.
- Allow uploaded or recorded audio to be executed from the console after ingestion instead of requiring a separate API call.
- Improve status, timeline, and trace labels so preview stops, clarification, confirmation, live-controlled actions, and agentic steps are understandable at a glance.
- Update tests and docs for the improved demo flow while preserving bounded scope, sanitized artifacts, and local browser execution by default.
- Do not add unrestricted public-web automation, remote browser execution, benchmark claims, or new model-training scope.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `operator-console`: Clarify run modes, fixture support, uploaded-audio execution, and status/timeline presentation in the web console.
- `safe-browser-execution`: Make unsupported live-controlled fixture requests fail or downgrade with explicit user-visible reasons instead of ambiguous preview output.
- `demo-evidence-set`: Document the intended console demo flow for preview, live-controlled visual tasks, clarification, and confirmation examples.

## Impact

- Affects the FastAPI app, static Operator Console HTML/CSS/JS, tests, README/demo docs, and OpenSpec specs.
- Does not change the core normalizer, validator, trace schema, `browser-use-vision` dependency boundary, sanitized trace policy, or live-controlled task set unless needed to expose existing metadata cleanly.
