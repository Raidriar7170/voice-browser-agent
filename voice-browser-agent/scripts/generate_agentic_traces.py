from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from voice_browser_agent.agentic import ControlledAgenticVisionAdapter
from voice_browser_agent.app import CommandPayload, create_app
from voice_browser_agent.models import BrowserTaskRequest, ExecutionMode, ExecutionTrace
from voice_browser_agent.trace_writer import TraceWriter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = PROJECT_ROOT / "fixtures/traces/agentic-sanitized"
AGENTIC_FIXTURES = ("icon-search", "color-swatch", "svg-dashboard")


def main() -> None:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="voice-browser-agentic-") as runtime_dir:
        app = create_app(runtime_dir=runtime_dir)
        client = TestClient(app)
        writer = TraceWriter(TRACE_DIR)
        for fixture_id in AGENTIC_FIXTURES:
            if fixture_id == "color-swatch":
                trace = asyncio.run(
                    build_variant_trace(
                        app.state.voice_browser,
                        fixture_id,
                        variant="first_no_effect_then_recover",
                    )
                )
            else:
                response = client.post(
                    f"/api/fixtures/{fixture_id}/executions",
                    json={"execution_mode": "live_controlled"},
                )
                response.raise_for_status()
                trace = ExecutionTrace.model_validate(response.json())
            trace.execution_id = f"agentic-{fixture_id}"
            writer.write_sanitized(trace, export_dir=TRACE_DIR)


async def build_variant_trace(state, fixture_id: str, variant: str) -> ExecutionTrace:
    payload = CommandPayload(fixture_id=fixture_id)
    trace = await state.prepare_trace(payload)
    mode = ExecutionMode.LIVE_CONTROLLED
    controlled_task = state.controlled_task_for_mode(fixture_id, mode)
    assert isinstance(trace.normalized_output, BrowserTaskRequest)
    request = state.with_controlled_target(trace.normalized_output, controlled_task)
    trace.normalized_output = request
    trace.execution_mode = mode

    executor = state.executor_for_mode(mode, controlled_task)

    def adapter_factory(task, runtime, vision_backend_url=None):
        return ControlledAgenticVisionAdapter(
            task=task,
            runtime={**runtime, "controlled_fixture_variant": variant},
            vision_backend_url=vision_backend_url,
        )

    executor.agentic_adapter_factory = adapter_factory
    result = await executor.execute(request, trace.execution_id)
    state.apply_execution_result(trace, result)
    return trace


if __name__ == "__main__":
    main()
