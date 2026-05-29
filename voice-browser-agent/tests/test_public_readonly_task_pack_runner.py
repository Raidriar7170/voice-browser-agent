import importlib.util
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts/build_public_readonly_task_pack_summary.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("build_public_readonly_task_pack_summary", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_public_readonly_task_pack_runner_writes_local_private_summary(tmp_path):
    runner = load_runner()
    output_dir = tmp_path / "runtime/public-readonly-task-pack"

    summary = runner.build_task_pack_summary(
        project_root=PROJECT_ROOT,
        output_dir=output_dir,
    )

    summary_path = output_dir / "summary.json"
    assert summary_path.exists()
    written = json.loads(summary_path.read_text(encoding="utf-8"))
    assert written == summary
    assert summary["task_count"] >= 8
    assert summary["is_complete"] is True
    assert summary["public_ready"] is False
    assert set(summary["category_counts"]) >= {
        "documentation",
        "reference",
        "package_metadata",
        "release_notes",
        "public_repository_search",
        "public_repository_read",
    }
    assert all(row["evidence_privacy_state"] == "local_private" for row in summary["rows"])
    assert all(row["export_state"] == "local_private" for row in summary["rows"])
    serialized = json.dumps(summary, ensure_ascii=False)
    assert "raw_page_text" not in serialized
    assert "raw_screenshot" not in serialized
    assert "browser_profile" not in serialized
    assert "/Users/" not in serialized
