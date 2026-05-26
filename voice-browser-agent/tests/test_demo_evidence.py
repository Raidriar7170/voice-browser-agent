import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_demo_task_suite_has_eight_tasks_and_half_visual_grounding_heavy():
    doc = (PROJECT_ROOT / "docs/demo/demo-task-suite.md").read_text(encoding="utf-8")
    task_rows = [line for line in doc.splitlines() if line.startswith("| ") and ".fixture.json" in line]
    visual_rows = [line for line in task_rows if "| Yes," in line]

    assert len(task_rows) == 8
    assert len(visual_rows) >= 4
    assert "scoped demo" in doc


def test_public_fixtures_are_metadata_not_raw_audio():
    fixtures = sorted((PROJECT_ROOT / "fixtures/audio").glob("*.fixture.json"))

    assert len(fixtures) == 8
    for fixture in fixtures:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        assert payload["sanitized_public"] is True
        assert fixture.suffix == ".json"


def test_sanitized_trace_artifacts_exist_for_each_demo_task_and_exclude_private_data():
    traces = sorted((PROJECT_ROOT / "fixtures/traces/sanitized").glob("*.json"))
    forbidden = ("raw_audio_path", "credential", "password", "token", "remote_host", "private_url")

    assert len(traces) == 8
    for trace in traces:
        text = trace.read_text(encoding="utf-8")
        payload = json.loads(text)
        assert payload["execution_id"].startswith("demo-")
        assert payload["final_status"] in {
            "succeeded",
            "clarification_required",
            "pending_confirmation",
            "cancelled",
            "stopped",
        }
        if payload["final_status"] == "stopped":
            assert payload["stop_reason"]
        assert not any(word in text for word in forbidden)


def test_live_controlled_sanitized_trace_artifacts_exist_for_selected_visual_tasks():
    traces = sorted((PROJECT_ROOT / "fixtures/traces/live-sanitized").glob("*.json"))
    forbidden = (
        "raw_audio_path",
        "raw_screenshot",
        "browser_profile",
        "cookie",
        "credential",
        "password",
        "token",
        "remote_host",
        "private_url",
        "file:///Users/",
    )

    assert len(traces) >= 2
    fixture_ids = set()
    for trace in traces:
        text = trace.read_text(encoding="utf-8")
        payload = json.loads(text)
        fixture_ids.add(payload["transcript"]["metadata"]["input_audio_id"])
        assert payload["execution_mode"] == "live_controlled"
        assert payload["final_status"] in {"succeeded", "failed", "stopped"}
        assert payload["browser_actions"] or payload["grounding_evidence_refs"]
        assert payload["execution_runtime"]["execution_mode"] == "live_controlled"
        assert not any(word in text for word in forbidden)

    assert {"icon-search", "color-swatch"}.issubset(fixture_ids)


def test_public_readme_uses_bounded_demo_positioning():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "bounded" in readme
    assert "scoped demo" in readme
    assert "benchmark" not in readme
    assert "sota" not in readme
    assert "production-ready" not in readme
