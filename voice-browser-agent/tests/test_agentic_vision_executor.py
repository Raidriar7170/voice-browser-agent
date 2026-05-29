import pytest

from voice_browser_agent.agentic import (
    AgenticVisionExecutor,
    ScriptedAgenticVisionAdapter,
    VisualActionOutcome,
    VisualObservation,
)
from voice_browser_agent.executor import BrowserExecutorConfig
from voice_browser_agent.models import BrowserIntentType, BrowserTaskRequest, ExecutionStatus


def _request() -> BrowserTaskRequest:
    return BrowserTaskRequest(
        task="Click the icon-only search button.",
        intent_type=BrowserIntentType.CLICK_VISUAL_TARGET,
        constraints=["controlled demo page only"],
        visual_references=[{"kind": "icon", "text": "magnifying glass", "source": "fixture"}],
        requires_confirmation=False,
        stop_conditions=["login_required", "payment_or_checkout"],
    )


@pytest.mark.asyncio
async def test_agentic_executor_records_successful_observe_act_verify_step():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(
                summary="Saw toolbar with one search icon.",
                target_status="resolved",
                selected_target_ref="som:search",
                grounding_evidence_refs=["grounding/step-1.json"],
            )
        ],
        outcomes=[
            VisualActionOutcome(
                status="succeeded",
                action_type="click",
                description="clicked the search icon",
                browser_state={"result_state": "Search panel open"},
                grounding_evidence_refs=["grounding/step-1-post-action.json"],
            )
        ],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(dry_run=False, execution_mode="live_controlled", max_steps=3),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-success")

    assert result.final_status is ExecutionStatus.SUCCEEDED
    assert result.runtime["execution_style"] == "agentic_vision"
    assert result.agentic_steps[0].observation_summary == "Saw toolbar with one search icon."
    assert result.agentic_steps[0].selected_target_ref == "som:search"
    assert result.agentic_steps[0].verification_decision.passed is True
    assert result.agentic_steps[0].visual_verification_result.outcome == "passed"
    assert result.agentic_steps[0].visual_verification_result.verifier_mode == (
        "deterministic_controlled"
    )
    assert result.actions[0].action_type == "click"
    assert result.grounding_evidence_refs == [
        "grounding/step-1.json",
        "grounding/step-1-post-action.json",
    ]


@pytest.mark.asyncio
async def test_agentic_executor_stops_at_step_budget():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(summary="Search icon is absent.", target_status="missing"),
        ],
        outcomes=[],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(dry_run=False, execution_mode="live_controlled", max_steps=1),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-budget")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "step_budget_exceeded"
    assert result.agentic_steps[0].recovery_decision.kind == "stop"


@pytest.mark.asyncio
async def test_agentic_executor_stops_when_target_remains_missing_after_recovery():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(summary="No search icon yet.", target_status="missing"),
            VisualObservation(summary="Still no search icon.", target_status="missing"),
        ],
        outcomes=[],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode="live_controlled",
            max_steps=3,
            max_recoveries=1,
        ),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-missing")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "missing_visual_target"
    assert [step.recovery_decision.kind for step in result.agentic_steps] == ["reobserve", "stop"]


@pytest.mark.asyncio
async def test_agentic_executor_stops_without_guessing_ambiguous_targets():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(
                summary="Two similar icon buttons are visible.",
                target_status="ambiguous",
                target_candidates=["som:search-left", "som:search-right"],
            )
        ],
        outcomes=[],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(dry_run=False, execution_mode="live_controlled"),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-ambiguous")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "ambiguous_visual_target"
    assert result.agentic_steps[0].target_candidates == ["som:search-left", "som:search-right"]


@pytest.mark.asyncio
async def test_agentic_executor_recovers_from_no_effect_action_with_reobservation():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(
                summary="Initial search icon target.",
                target_status="resolved",
                selected_target_ref="som:stale-search",
            ),
            VisualObservation(
                summary="Fresh search icon target after re-observation.",
                target_status="resolved",
                selected_target_ref="som:fresh-search",
                grounding_evidence_refs=["grounding/fresh.json"],
            ),
        ],
        outcomes=[
            VisualActionOutcome(
                status="no_effect",
                action_type="click",
                description="clicked stale target",
            ),
            VisualActionOutcome(
                status="succeeded",
                action_type="click",
                description="clicked fresh target",
                browser_state={"result_state": "Search panel open"},
                grounding_evidence_refs=["grounding/fresh-post-action.json"],
            ),
        ],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode="live_controlled",
            max_steps=3,
            max_recoveries=1,
        ),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-recovery")

    assert result.final_status is ExecutionStatus.SUCCEEDED
    assert [step.recovery_decision.kind for step in result.agentic_steps] == ["reobserve", "none"]
    assert result.agentic_steps[-1].selected_target_ref == "som:fresh-search"


@pytest.mark.asyncio
async def test_agentic_executor_does_not_pass_with_only_pre_action_grounding():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(
                summary="Initial search icon target.",
                target_status="resolved",
                selected_target_ref="som:search",
                grounding_evidence_refs=["grounding/pre-action-only.json"],
            )
        ],
        outcomes=[
            VisualActionOutcome(
                status="succeeded",
                action_type="click",
                description="clicked target without post-action proof",
            )
        ],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode="live_controlled",
            max_steps=1,
            max_recoveries=0,
        ),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-pre-action-only")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "visual_verification_uncertain"
    assert result.agentic_steps[0].visual_verification_result.outcome == "uncertain"
    assert result.agentic_steps[0].verification_decision.passed is False


@pytest.mark.asyncio
async def test_agentic_executor_reobserves_when_action_succeeds_but_visual_verification_fails():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(
                summary="Initial controlled toolbar target.",
                target_status="resolved",
                selected_target_ref="som:search",
                grounding_evidence_refs=["grounding/initial.json"],
            ),
            VisualObservation(
                summary="Fresh controlled toolbar target after re-observation.",
                target_status="resolved",
                selected_target_ref="som:search-fresh",
                grounding_evidence_refs=["grounding/fresh.json"],
            ),
        ],
        outcomes=[
            VisualActionOutcome(
                status="succeeded",
                action_type="click",
                description="clicked the search icon but the visual state did not change",
                browser_state={
                    "visual_verification": {
                        "outcome": "failed",
                        "expected_condition": "Search panel should be visibly open.",
                        "observed_state_summary": "Toolbar remained visible with no search panel.",
                        "reason": "post-action state did not include the expected panel marker",
                        "sanitized_evidence_refs": ["grounding/verify-failed.json"],
                    }
                },
            ),
            VisualActionOutcome(
                status="succeeded",
                action_type="click",
                description="clicked the fresh search target",
                browser_state={
                    "visual_verification": {
                        "outcome": "passed",
                        "expected_condition": "Search panel should be visibly open.",
                        "observed_state_summary": "Search panel open marker is visible.",
                        "reason": "post-action state matched the expected panel marker",
                        "sanitized_evidence_refs": ["grounding/verify-passed.json"],
                    }
                },
            ),
        ],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode="live_controlled",
            max_steps=3,
            max_recoveries=1,
        ),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-visual-recovery")

    assert result.final_status is ExecutionStatus.SUCCEEDED
    assert result.agentic_steps[0].action_result.status == "succeeded"
    assert result.agentic_steps[0].visual_verification_result.outcome == "failed"
    assert result.agentic_steps[0].verification_decision.passed is False
    assert result.agentic_steps[0].recovery_decision.kind == "reobserve"
    assert result.agentic_steps[1].visual_verification_result.outcome == "passed"


@pytest.mark.asyncio
async def test_agentic_executor_stops_with_reason_when_visual_verification_is_uncertain():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(
                summary="Controlled toolbar target is visible.",
                target_status="resolved",
                selected_target_ref="som:search",
            )
        ],
        outcomes=[
            VisualActionOutcome(
                status="succeeded",
                action_type="click",
                description="clicked the search icon",
                browser_state={
                    "visual_verification": {
                        "outcome": "uncertain",
                        "expected_condition": "Search panel should be visibly open.",
                        "observed_state_summary": "The captured state was partially occluded.",
                        "reason": "controlled verifier could not safely determine completion",
                    }
                },
            )
        ],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(
            dry_run=False,
            execution_mode="live_controlled",
            max_steps=1,
            max_recoveries=0,
        ),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-uncertain")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason == "visual_verification_uncertain"
    assert result.agentic_steps[0].action_result.status == "succeeded"
    assert result.agentic_steps[0].visual_verification_result.outcome == "uncertain"
    assert result.agentic_steps[0].recovery_decision.kind == "stop"
    assert "could not safely determine" in result.agentic_steps[0].recovery_decision.reason


@pytest.mark.asyncio
async def test_agentic_executor_rejects_empty_live_evidence():
    adapter = ScriptedAgenticVisionAdapter(observations=[], outcomes=[])
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(dry_run=False, execution_mode="live_controlled"),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-empty")

    assert result.final_status is ExecutionStatus.FAILED
    assert result.failure_reason == "agentic_live_controlled_missing_evidence"


@pytest.mark.asyncio
async def test_agentic_executor_stops_before_action_on_sensitive_browser_state():
    adapter = ScriptedAgenticVisionAdapter(
        observations=[
            VisualObservation(
                summary="Checkout page is visible.",
                target_status="resolved",
                selected_target_ref="som:pay",
                browser_state={
                    "url": "https://shop.example.test/checkout",
                    "title": "Checkout",
                    "visible_text": "Please log in before payment",
                },
            )
        ],
        outcomes=[
            VisualActionOutcome(status="succeeded", action_type="click", description="should not run")
        ],
    )
    executor = AgenticVisionExecutor(
        config=BrowserExecutorConfig(dry_run=False, execution_mode="live_controlled"),
        observation_adapter=adapter,
    )

    result = await executor.execute(_request(), execution_id="exec-agentic-sensitive")

    assert result.final_status is ExecutionStatus.STOPPED
    assert result.stop_reason in {"login_required", "payment_or_checkout"}
    assert result.actions == []
