from __future__ import annotations

import argparse
import json
from pathlib import Path

from voice_browser_agent.preflight import build_readiness_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local real-use readiness.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--runtime-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_readiness_report(project_root=args.project_root, runtime_dir=args.runtime_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
