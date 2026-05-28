from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ControlledDemoTask:
    fixture_id: str
    target_ref: str
    evidence_ref: str
    release_required: bool = True

    @property
    def target_url(self) -> str:
        return (PROJECT_ROOT / self.target_ref).as_uri()


LIVE_CONTROLLED_TASKS: dict[str, ControlledDemoTask] = {
    "icon-search": ControlledDemoTask(
        fixture_id="icon-search",
        target_ref="demo/pages/icon_only_toolbar.html",
        evidence_ref="grounding/live-controlled/icon-search.json",
    ),
    "color-swatch": ControlledDemoTask(
        fixture_id="color-swatch",
        target_ref="demo/pages/color_swatch.html",
        evidence_ref="grounding/live-controlled/color-swatch.json",
    ),
    "svg-dashboard": ControlledDemoTask(
        fixture_id="svg-dashboard",
        target_ref="demo/pages/svg_dashboard.html",
        evidence_ref="grounding/live-controlled/svg-dashboard.json",
    ),
    "github-showcase": ControlledDemoTask(
        fixture_id="github-showcase",
        target_ref="demo/pages/github_showcase.html",
        evidence_ref="grounding/live-controlled/github-showcase.json",
        release_required=False,
    ),
}


def get_live_controlled_task(fixture_id: str) -> ControlledDemoTask | None:
    return LIVE_CONTROLLED_TASKS.get(fixture_id)


def selected_live_fixture_ids() -> tuple[str, ...]:
    return tuple(
        fixture_id
        for fixture_id, task in LIVE_CONTROLLED_TASKS.items()
        if task.release_required
    )
