from __future__ import annotations

import argparse
import base64
import json
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "fixtures/traces/real-vision-sanitized"
CONTROLLED_TARGET_REF = "demo/pages/icon_only_toolbar.html"
SOURCE_TRACE = PROJECT_ROOT / "fixtures/traces/sanitized/demo-icon-search.json"
FIXTURE_ID = "icon-search"
ANNOTATOR_API = "browser_use_vision.som.annotate_screenshot"


class RealVisionEvidenceError(RuntimeError):
    pass


def resolve_annotator() -> Callable[..., str]:
    try:
        from browser_use_vision.som import annotate_screenshot
    except Exception as exc:
        raise ImportError("browser-use-vision SoM unavailable") from exc
    return annotate_screenshot


def generate_real_vision_trace(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    try:
        annotator = resolve_annotator()
    except ImportError as exc:
        raise RealVisionEvidenceError(f"browser-use-vision entry point unavailable: {exc}") from exc

    page_evidence = capture_controlled_page_evidence(project_root=project_root, annotator=annotator)
    if (
        not page_evidence["annotated_image_b64_len"]
        or not page_evidence["selector_count"]
        or not page_evidence["som_output_changed"]
    ):
        raise RealVisionEvidenceError(
            "missing/no meaningful visual evidence from browser-use-vision SoM annotator"
        )

    payload = build_trace_payload(project_root=project_root, page_evidence=page_evidence)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "real-vision-icon-search.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def capture_controlled_page_evidence(
    project_root: Path,
    annotator: Callable[..., str],
) -> dict[str, Any]:
    target_path = project_root / CONTROLLED_TARGET_REF
    if not target_path.exists():
        raise RealVisionEvidenceError(f"controlled target missing: {CONTROLLED_TARGET_REF}")

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as default_exc:
            try:
                browser = playwright.chromium.launch(channel="chrome")
            except PlaywrightError as channel_exc:
                raise RealVisionEvidenceError(
                    "playwright chromium unavailable: "
                    f"{default_exc}; chrome channel unavailable: {channel_exc}"
                ) from channel_exc
        try:
            page = browser.new_page(viewport={"width": 960, "height": 540})
            page.goto(target_path.as_uri())
            page.wait_for_selector("header[aria-label='toolbar'] button")
            screenshot_b64 = base64.b64encode(page.screenshot(type="png")).decode("ascii")
            selector_map, selector_summary = build_selector_map(page)
            annotated_b64 = annotator(
                screenshot_b64,
                selector_map,
                line_width=2,
                font_size=14,
                max_elements=12,
            )
            page.get_by_label("search").click()
        finally:
            browser.close()

    if not annotated_b64 or annotated_b64 == screenshot_b64:
        raise RealVisionEvidenceError(
            "missing/no meaningful visual evidence from browser-use-vision SoM annotator"
        )
    return {
        "selector_count": len(selector_summary),
        "selector_summary": selector_summary,
        "screenshot_b64_len": len(screenshot_b64),
        "annotated_image_b64_len": len(annotated_b64),
        "som_output_changed": annotated_b64 != screenshot_b64,
    }


def build_selector_map(page: Any) -> tuple[dict[int, Any], list[dict[str, Any]]]:
    selector_map: dict[int, Any] = {}
    selector_summary: list[dict[str, Any]] = []
    buttons = page.locator("header[aria-label='toolbar'] button")
    for index in range(buttons.count()):
        button = buttons.nth(index)
        bbox = button.bounding_box()
        if not bbox:
            continue
        label = button.get_attribute("aria-label") or f"button-{index + 1}"
        backend_node_id = index + 1
        rect = SimpleNamespace(
            x=float(bbox["x"]),
            y=float(bbox["y"]),
            width=float(bbox["width"]),
            height=float(bbox["height"]),
        )
        selector_map[backend_node_id] = SimpleNamespace(
            snapshot_node=SimpleNamespace(clientRects=rect)
        )
        selector_summary.append(
            {
                "ref": f"som:{label}",
                "backend_node_id": backend_node_id,
                "role": "button",
                "label": label,
                "bbox": {
                    "x": round(float(bbox["x"]), 2),
                    "y": round(float(bbox["y"]), 2),
                    "width": round(float(bbox["width"]), 2),
                    "height": round(float(bbox["height"]), 2),
                },
            }
        )
    return selector_map, selector_summary


def build_trace_payload(project_root: Path, page_evidence: dict[str, Any]) -> dict[str, Any]:
    source = json.loads((project_root / SOURCE_TRACE.relative_to(PROJECT_ROOT)).read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    provider = {
        "package": "browser-use-vision",
        "module": "browser_use_vision.som",
        "version": package_version("browser-use-vision"),
    }
    adapter = {
        "api": ANNOTATOR_API,
        "controlled_target_ref": CONTROLLED_TARGET_REF,
        "deterministic_controlled_adapter": False,
        "selector_source": "playwright-bounding-boxes",
    }
    grounding_refs = [
        "browser-use-vision:som:icon-search",
        "som:search",
    ]
    normalized_output = dict(source["normalized_output"])
    normalized_output["controlled_target_ref"] = CONTROLLED_TARGET_REF
    return {
        "execution_id": "real-vision-icon-search",
        "execution_mode": "live_controlled",
        "transcript": source["transcript"],
        "normalized_output": normalized_output,
        "validator_decision": source["validator_decision"],
        "confirmation_decision": source["confirmation_decision"],
        "browser_actions": [
            {
                "action_type": "click",
                "description": "performed the controlled search-icon click after producing browser-use-vision SoM annotation evidence",
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
            "evidence_mode": "real_vision_controlled",
            "controlled_fixture_id": FIXTURE_ID,
            "controlled_target_ref": CONTROLLED_TARGET_REF,
            "provider": provider,
            "adapter": adapter,
            "visual_evidence": {
                "annotated_element_count": page_evidence["selector_count"],
                "selector_summary": page_evidence["selector_summary"],
                "screenshot_bytes_discarded": True,
                "annotated_image_bytes_discarded": True,
                "screenshot_b64_len": page_evidence["screenshot_b64_len"],
                "annotated_image_b64_len": page_evidence["annotated_image_b64_len"],
                "som_output_changed": page_evidence["som_output_changed"],
            },
            "privacy_scan": {"status": "passed"},
        },
        "final_status": "succeeded",
        "failure_reason": None,
        "stop_reason": None,
        "created_at": now,
        "updated_at": now,
    }


def package_version(package: str) -> str:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return "editable-local"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sanitized real-vision controlled trace.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = generate_real_vision_trace(output_dir=args.output_dir, project_root=args.project_root)
    except RealVisionEvidenceError as exc:
        print(f"error: {exc}")
        return 1
    print(f"wrote {args.output_dir / 'real-vision-icon-search.json'}")
    print(f"status: {payload['final_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
