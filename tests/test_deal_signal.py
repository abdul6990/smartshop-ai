"""Unit tests for deterministic deal-signal classification."""

from agents.deal_signal import evaluate_deal_signal, evaluate_from_history


def test_genuine_bargain_rule():
    result = evaluate_deal_signal(
        current_price=900,
        previous_day_price=1100,
        average_30_day_price=1200,
        min_30_day_price=900,
    )
    assert result["label"] == "GENUINE_BARGAIN"
    assert result["score"] > 0.9


def test_fake_discount_rule():
    result = evaluate_deal_signal(
        current_price=900,
        previous_day_price=1500,
        average_30_day_price=1000,
        min_30_day_price=850,
    )
    assert result["label"] == "FAKE_DISCOUNT"
    assert result["score"] < 0.2


def test_normal_rule():
    result = evaluate_deal_signal(
        current_price=980,
        previous_day_price=1000,
        average_30_day_price=1005,
        min_30_day_price=950,
    )
    assert result["label"] == "NORMAL"


def test_history_wrapper_insufficient_data():
    result = evaluate_from_history([999])
    assert result["label"] == "INSUFFICIENT_DATA"


def test_history_wrapper_genuine():
    result = evaluate_from_history([1200, 1180, 1150, 900])
    assert result["label"] == "GENUINE_BARGAIN"
