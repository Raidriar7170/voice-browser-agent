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


def test_controlled_showcase_sanitized_trace_exists_for_github_shaped_command():
    trace = PROJECT_ROOT / "fixtures/traces/live-sanitized/live-github-showcase.json"
    text = trace.read_text(encoding="utf-8")
    payload = json.loads(text)

    assert payload["execution_mode"] == "live_controlled"
    assert payload["execution_runtime"]["evidence_mode"] == "controlled_showcase"
    assert payload["route_decision"]["controlled_fixture_id"] == "github-showcase"
    assert payload["route_decision"]["controlled_target_ref"] == "demo/pages/github_showcase.html"
    assert payload["final_status"] == "succeeded"
    assert payload["browser_actions"] or payload["grounding_evidence_refs"]
    assert "github.com" not in text.lower()
    assert "file:///Users/" not in text


def test_agentic_sanitized_trace_artifacts_exist_for_selected_visual_tasks():
    traces = sorted((PROJECT_ROOT / "fixtures/traces/agentic-sanitized").glob("*.json"))
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
        assert payload["execution_runtime"]["execution_style"] == "agentic_vision"
        assert payload["agentic_steps"]
        assert payload["browser_actions"] or payload["grounding_evidence_refs"]
        assert not any(word in text for word in forbidden)

    assert {"icon-search", "color-swatch"}.issubset(fixture_ids)


def test_public_readme_uses_bounded_demo_positioning():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "bounded" in readme
    assert "scoped demo" in readme
    assert "benchmark" not in readme
    assert "sota" not in readme
    assert "production automation" not in readme
    assert "unrestricted public-web autonomy" not in readme
    assert "production-ready" not in readme


def test_release_pack_docs_define_build_command_and_artifact_boundaries():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    video_plan = (PROJECT_ROOT / "docs/demo/video-plan.md").read_text(encoding="utf-8")
    combined = f"{readme}\n{video_plan}"

    assert "uv run python scripts/build_demo_evidence_pack.py" in combined
    assert "runtime/demo-evidence-release-pack/" in combined
    assert "runtime/demo-evidence-release-pack/index.html" in combined
    assert "runtime/demo-evidence-release-pack/manifest.json" in combined
    assert "fixtures/traces/sanitized/" in readme
    assert "fixtures/traces/live-sanitized/" in readme
    assert "fixtures/traces/agentic-sanitized/" in readme
    assert "fixtures/traces/real-vision-sanitized/" in readme
    assert "fixtures/traces/real-voice-sanitized/" in readme
    assert "fixtures/traces/real-use-sanitized/" in readme
    assert "generated local artifact" in readme
    assert "committed evidence sources" in readme


def test_release_pack_docs_avoid_overclaiming():
    docs = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs/demo/video-plan.md",
        PROJECT_ROOT / "docs/demo/speech-to-task-dataset.md",
        PROJECT_ROOT / "docs/demo/closeout-checklist.md",
        PROJECT_ROOT / "docs/interview-project-overview.html",
    ]
    forbidden = (
        "benchmark",
        "sota",
        "production automation",
        "unrestricted public-web autonomy",
    )

    for doc in docs:
        text = doc.read_text(encoding="utf-8").lower()
        assert not any(term in text for term in forbidden), doc


def test_closeout_checklist_defines_final_commands_and_artifact_boundaries():
    checklist = (PROJECT_ROOT / "docs/demo/closeout-checklist.md").read_text(encoding="utf-8")

    required_commands = (
        "uv run python scripts/build_demo_evidence_pack.py",
        "uv run python scripts/build_speech_to_task_dataset.py",
        "openspec validate project-closeout-interview-pack --strict",
        "openspec validate --all --strict",
        "uv run pytest",
        "git diff --check",
        "git status --short --ignored",
    )
    for command in required_commands:
        assert command in checklist

    assert "runtime/demo-evidence-release-pack/manifest.json" in checklist
    assert "runtime/speech-to-task-adaptation-dataset/manifest.json" in checklist
    assert "generated runtime artifacts stay local" in checklist.lower()
    assert "fixtures/traces/sanitized/" in checklist
    assert "fixtures/traces/live-sanitized/" in checklist
    assert "fixtures/traces/agentic-sanitized/" in checklist
    assert "speech-to-task-adaptation-dataset" in checklist


def test_interview_project_overview_covers_required_story_and_evidence_sources():
    html = (PROJECT_ROOT / "docs/interview-project-overview.html").read_text(encoding="utf-8")
    lower = html.lower()

    required_sections = (
        "problem framing",
        "bounded scope",
        "architecture",
        "execution flow",
        "evidence modes",
        "safety and privacy gates",
        "adaptation dataset output",
        "validation surface",
        "limitations",
        "interview talk track",
    )
    for section in required_sections:
        assert section in lower

    required_references = (
        "README.md",
        "docs/demo/demo-task-suite.md",
        "docs/demo/ablations.md",
        "docs/demo/video-plan.md",
        "scripts/build_demo_evidence_pack.py",
        "scripts/build_speech_to_task_dataset.py",
        "fixtures/traces/sanitized/",
        "fixtures/traces/live-sanitized/",
        "fixtures/traces/agentic-sanitized/",
        "fixtures/traces/real-voice-sanitized/",
        "fixtures/traces/real-use-sanitized/",
        "runtime/demo-evidence-release-pack/manifest.json",
        "runtime/speech-to-task-adaptation-dataset/manifest.json",
        "openspec validate --all --strict",
        "uv run pytest",
    )
    for reference in required_references:
        assert reference in html

    limitations = (
        "model fine-tuning",
        "expanded dataset collection",
        "public hosting",
        "broad public-web automation",
    )
    for limitation in limitations:
        assert limitation in lower


def test_final_handoff_docs_avoid_private_markers_and_unsupported_claims():
    docs = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs/demo/closeout-checklist.md",
        PROJECT_ROOT / "docs/demo/video-plan.md",
        PROJECT_ROOT / "docs/interview-project-overview.html",
    ]
    forbidden = (
        "raw_audio_path",
        "raw_screenshot",
        "browser_profile",
        "password=",
        "token=",
        "sk-proj-",
        "/users/private",
        "file:///users/",
        "sota",
        "production automation",
        "unrestricted public-web autonomy",
        "asr/tts quality claim",
        "ships a model checkpoint",
        "public raw dataset",
    )

    for doc in docs:
        text = doc.read_text(encoding="utf-8").lower()
        assert not any(term in text for term in forbidden), doc


def test_readme_points_to_closeout_and_interview_handoff():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/demo/closeout-checklist.md" in readme
    assert "docs/interview-project-overview.html" in readme


def test_speech_to_task_dataset_docs_define_build_command_and_boundaries():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    dataset_doc = (PROJECT_ROOT / "docs/demo/speech-to-task-dataset.md").read_text(
        encoding="utf-8"
    )
    video_plan = (PROJECT_ROOT / "docs/demo/video-plan.md").read_text(encoding="utf-8")
    combined = f"{readme}\n{dataset_doc}\n{video_plan}"

    assert "uv run python scripts/build_speech_to_task_dataset.py" in combined
    assert "runtime/speech-to-task-adaptation-dataset/" in combined
    assert "runtime/speech-to-task-adaptation-dataset/manifest.json" in combined
    assert "runtime/speech-to-task-adaptation-dataset/examples.jsonl" in combined
    assert "--correction-overlay" in dataset_doc
    assert "local Speech-to-Task adaptation preparation evidence" in combined
    assert "not an ASR/TTS corpus" in dataset_doc
    assert "not a model checkpoint" in dataset_doc
    assert "not broad web-autonomy evidence" in dataset_doc


def test_normalizer_comparison_docs_define_local_private_boundaries():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    dataset_doc = (PROJECT_ROOT / "docs/demo/speech-to-task-dataset.md").read_text(
        encoding="utf-8"
    )
    closeout = (PROJECT_ROOT / "docs/demo/closeout-checklist.md").read_text(
        encoding="utf-8"
    )
    public_evidence = (PROJECT_ROOT / "docs/public-evidence/index.html").read_text(
        encoding="utf-8"
    )
    combined = f"{readme}\n{dataset_doc}\n{closeout}\n{public_evidence}"

    assert "uv run python scripts/build_normalizer_comparison.py --seed-set" in combined
    assert "runtime/normalizer-comparison/manifest.json" in combined
    assert "structured-output comparison" in combined
    assert "not model training" in combined
    assert "raw provider responses" in combined
    assert "API keys" in combined


def test_real_use_scenarios_are_documented_and_controlled():
    scenario_doc = (PROJECT_ROOT / "docs/demo/useful-scenarios.md").read_text(encoding="utf-8")
    scenario_manifest = json.loads(
        (PROJECT_ROOT / "fixtures/useful-scenarios.json").read_text(encoding="utf-8")
    )

    assert "controlled local workflows" in scenario_doc
    assert "not broad public-web automation" in scenario_doc
    assert len(scenario_manifest["scenarios"]) >= 3
    scenario_ids = {scenario["id"] for scenario in scenario_manifest["scenarios"]}
    assert {"crm-filter", "settings-toggle", "metrics-dashboard"}.issubset(scenario_ids)
    assert all(
        scenario["privacy_boundary"] == "local controlled page"
        for scenario in scenario_manifest["scenarios"]
    )


def test_real_voice_and_usage_traces_are_sanitized():
    trace_dirs = [
        PROJECT_ROOT / "fixtures/traces/real-voice-sanitized",
        PROJECT_ROOT / "fixtures/traces/real-use-sanitized",
    ]
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
        "storage_path",
    )
    traces = [trace for trace_dir in trace_dirs for trace in sorted(trace_dir.glob("*.json"))]
    assert traces
    usage_ids = {trace.stem for trace in traces if trace.parent.name == "real-use-sanitized"}
    assert {
        "usage-asr-unavailable",
        "usage-clarification-required",
        "usage-confirmation-pending",
        "usage-confirmation-cancelled",
        "usage-ambiguous-visual-target",
    }.issubset(usage_ids)
    for trace in traces:
        text = trace.read_text(encoding="utf-8")
        payload = json.loads(text)
        assert payload["execution_runtime"]["privacy_scan"]["status"] == "passed"
        assert not any(marker in text for marker in forbidden), trace


def test_demo_docs_distinguish_agentic_evidence_and_ablations():
    suite = (PROJECT_ROOT / "docs/demo/demo-task-suite.md").read_text(encoding="utf-8")
    ablations = (PROJECT_ROOT / "docs/demo/ablations.md").read_text(encoding="utf-8")

    assert "agentic live-controlled" in suite
    assert "fixtures/traces/agentic-sanitized/" in suite
    assert "re-observation" in ablations
    assert "visual target resolution" in ablations


def test_context_coverage_matrix_covers_domain_terms_and_dialogue_commitments():
    context = (PROJECT_ROOT.parent / "CONTEXT.md").read_text(encoding="utf-8")

    assert "## Coverage Matrix (2026-05-26)" in context
    assert "| L7-L9 | Voice-to-Browser Agent |" in context
    assert "| L127-L129 | Trace-Derived Training Example |" in context
    assert "| L205-L207 | Voice layer is outside `browser-use-vision`" in context
    assert "| L309-L311 | Execution Traces can become Trace-Derived Training Examples" in context
    assert "Covered for later-data support; training deferred" in context


def test_openspec_main_specs_have_purpose_text():
    spec_dir = PROJECT_ROOT.parent / "openspec/specs"
    specs = sorted(spec_dir.glob("*/spec.md"))

    assert specs
    for spec in specs:
        text = spec.read_text(encoding="utf-8")
        assert "## Purpose" in text
        assert "TBD" not in text
