from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from voice_browser_agent.public_readonly import build_public_readonly_useful_task_pack_summary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runtime/public-readonly-task-pack"


def build_task_pack_summary(
    *,
    project_root: Path = PROJECT_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    project_root = Path(project_root)
    output_dir = Path(output_dir)
    manifest_path = project_root / "fixtures/public-readonly-useful-task-pack.json"
    summary = build_public_readonly_useful_task_pack_summary(manifest_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a local/private public-readonly useful task-pack summary."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    summary = build_task_pack_summary(
        project_root=args.project_root,
        output_dir=args.output_dir,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
