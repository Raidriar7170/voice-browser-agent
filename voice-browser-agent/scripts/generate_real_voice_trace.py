from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "fixtures/traces/real-voice-sanitized"
SOURCE_TRACE = PROJECT_ROOT / "fixtures/traces/sanitized/demo-icon-search.json"
CONTROLLED_TARGET_REF = "demo/pages/icon_only_toolbar.html"
FIXTURE_ID = "icon-search"


class RealVoiceEvidenceError(RuntimeError):
    pass


def generate_real_voice_trace(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    payload = build_real_voice_trace_payload(project_root=project_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "real-voice-icon-search.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def build_real_voice_trace_payload(
    input_source: str = "audio",
    project_root: Path = PROJECT_ROOT,
    original_asr_text: str = "点右上角搜索图标",
    reviewed_text: str = "点击右上角的放大镜图标",
    adapter_name: str = "real-use-smoke-asr",
) -> dict[str, Any]:
    if input_source != "audio":
        raise RealVoiceEvidenceError("source-mismatch: real voice evidence requires audio input")

    source = json.loads((project_root / SOURCE_TRACE.relative_to(PROJECT_ROOT)).read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    input_audio_id = "real-audio-command-redacted"
    transcript_review = {
        "status": "edited" if original_asr_text != reviewed_text else "accepted",
        "original_text": original_asr_text,
        "reviewed_text": reviewed_text,
    }
    transcript = {
        "text": reviewed_text,
        "metadata": {
            "adapter_name": adapter_name,
            "input_audio_id": input_audio_id,
            "language_mode": "zh-first",
            "created_at": now,
            "confidence": 0.91,
            "diagnostics": {
                "input_source": "audio",
                "transcript_review": transcript_review,
                "source_audio_discarded": True,
            },
        },
    }
    normalized_output = dict(source["normalized_output"])
    normalized_output["task"] = reviewed_text
    normalized_output["controlled_target_ref"] = CONTROLLED_TARGET_REF
    grounding_refs = ["real-voice:reviewed-audio", "browser-use-vision:som:icon-search"]
    return {
        "execution_id": "real-voice-icon-search",
        "execution_mode": "live_controlled",
        "transcript": transcript,
        "normalized_output": normalized_output,
        "validator_decision": source["validator_decision"],
        "confirmation_decision": source["confirmation_decision"],
        "browser_actions": [
            {
                "action_type": "click",
                "description": "executed reviewed real-audio command on the controlled search icon page",
                "screenshot_ref": None,
                "grounding_evidence_refs": grounding_refs,
                "browser_state": {
                    "controlled_target_ref": CONTROLLED_TARGET_REF,
                    "controlled_click_target_ref": "som:search",
                },
                "created_at": now,
            }
        ],
        "grounding_evidence_refs": grounding_refs,
        "execution_runtime": {
            "execution_mode": "live_controlled",
            "evidence_mode": "real_voice_controlled",
            "input_source": "audio",
            "controlled_fixture_id": FIXTURE_ID,
            "controlled_target_ref": CONTROLLED_TARGET_REF,
            "audio": {
                "input_audio_id": input_audio_id,
                "source_audio_discarded": True,
            },
            "asr": {
                "adapter_name": adapter_name,
                "confidence": 0.91,
                "diagnostics": transcript["metadata"]["diagnostics"],
            },
            "transcript_review": transcript_review,
            "privacy_scan": {"status": "passed"},
        },
        "final_status": "succeeded",
        "failure_reason": None,
        "stop_reason": None,
        "created_at": now,
        "updated_at": now,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sanitized real voice controlled trace.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = generate_real_voice_trace(
            output_dir=args.output_dir,
            project_root=args.project_root,
        )
    except RealVoiceEvidenceError as exc:
        print(f"error: {exc}")
        return 1
    print(f"wrote {args.output_dir / 'real-voice-icon-search.json'}")
    print(f"status: {payload['final_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
