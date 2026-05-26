from voice_browser_agent.models import BrowserIntentType, BrowserTaskRequest, ConfirmationState
from voice_browser_agent.safety import ConfirmationGate, detect_browser_state_stop
from voice_browser_agent.validator import NormalizerValidator


def _request(requires_confirmation: bool) -> BrowserTaskRequest:
    return BrowserTaskRequest(
        task="提交付款",
        intent_type=BrowserIntentType.FILL_FORM,
        constraints=["stop before final submit"],
        visual_references=[],
        requires_confirmation=requires_confirmation,
        stop_conditions=["payment_or_checkout", "irreversible_submit"],
        safety_flags=["payment"],
    )


def test_confirmation_gate_pauses_required_confirmation_before_execution():
    request = _request(requires_confirmation=True)
    validation = NormalizerValidator().validate(request)

    decision = ConfirmationGate().evaluate(request, validation)

    assert decision.state is ConfirmationState.PENDING
    assert "confirmation" in decision.reason


def test_confirmation_gate_supports_confirm_and_cancel_transitions():
    gate = ConfirmationGate()
    pending = gate.evaluate(_request(requires_confirmation=True), NormalizerValidator().validate(_request(True)))

    assert gate.confirm(pending, decided_by="operator").state is ConfirmationState.CONFIRMED
    assert gate.cancel(pending, decided_by="operator").state is ConfirmationState.CANCELLED


def test_confirmation_gate_blocks_rejected_validation():
    request = _request(requires_confirmation=False)
    validation = NormalizerValidator().validate(
        request.model_copy(update={"stop_conditions": []})
    )

    decision = ConfirmationGate().evaluate(request, validation)

    assert decision.state is ConfirmationState.BLOCKED


def test_browser_state_safety_stop_detection():
    stop = detect_browser_state_stop(
        {
            "url": "https://shop.example.test/checkout",
            "title": "Checkout",
            "visible_text": "Please log in before payment",
        }
    )

    assert stop is not None
    assert stop.reason in {"login_required", "payment_or_checkout"}

