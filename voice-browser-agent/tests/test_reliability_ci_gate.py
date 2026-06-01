from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
WORKFLOW_PATH = REPO_ROOT / ".github/workflows/reliability.yml"
FRONT_DOOR_PATH = REPO_ROOT / ".github/workflows/front-door.yml"


def _workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(line.strip().removesuffix("\\").strip() for line in text.splitlines())


def test_reliability_workflow_is_separate_and_has_expected_triggers():
    assert FRONT_DOOR_PATH.exists()
    assert WORKFLOW_PATH.exists()

    text = _workflow_text()

    assert "name: Reliability" in text
    assert "pull_request:" in text
    assert "push:" in text
    assert "branches:" in text
    assert "- main" in text
    assert "workflow_dispatch:" in text
    assert "front-door.yml" not in text


def test_reliability_workflow_runs_openspec_strict_validation():
    text = _workflow_text()
    normalized = _normalized(text)

    assert "OPENSPEC_TELEMETRY: \"0\"" in text
    assert "npm install -g @fission-ai/openspec" in text
    assert "OPENSPEC_TELEMETRY=0 openspec validate --all --strict" in normalized


def test_reliability_workflow_documents_ci_safe_dependency_strategy():
    text = _workflow_text()
    normalized = _normalized(text)

    assert "CI-safe pytest subset" in text
    assert "browser-use-vision remains local-only" in text
    assert "../../../browser-use-vision" not in text
    assert 'python -m pip install -e "voice-browser-agent[dev]" --no-deps' in normalized
    assert "pydantic-settings" in normalized


def test_reliability_workflow_runs_deterministic_subset_without_private_runtime():
    text = _workflow_text()
    normalized = _normalized(text)

    assert "CI_SAFE_PYTEST_TARGETS" in text
    assert "tests/test_reliability_ci_gate.py" in text
    assert "tests/test_reliability_snapshot.py" in text
    assert "tests/test_demo_evidence.py" in text
    assert "tests/test_demo_evidence_release_pack.py" in text
    assert "tests/test_real_vision_controlled_evidence.py" not in text
    assert "uv run pytest" not in normalized
    assert "python -m pytest $CI_SAFE_PYTEST_TARGETS" in normalized
