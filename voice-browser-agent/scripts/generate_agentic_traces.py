from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from voice_browser_agent.app import create_app
from voice_browser_agent.models import ExecutionTrace
from voice_browser_agent.trace_writer import TraceWriter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = PROJECT_ROOT / "fixtures/traces/agentic-sanitized"
AGENTIC_FIXTURES = ("icon-search", "color-swatch", "svg-dashboard")


def main() -> None:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="voice-browser-agentic-") as runtime_dir:
        client = TestClient(create_app(runtime_dir=runtime_dir))
        writer = TraceWriter(TRACE_DIR)
        for fixture_id in AGENTIC_FIXTURES:
            response = client.post(
                f"/api/fixtures/{fixture_id}/executions",
                json={"execution_mode": "live_controlled"},
            )
            response.raise_for_status()
            trace = ExecutionTrace.model_validate(response.json())
            trace.execution_id = f"agentic-{fixture_id}"
            writer.write_sanitized(trace, export_dir=TRACE_DIR)


if __name__ == "__main__":
    main()
