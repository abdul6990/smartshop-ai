"""
Deal signal engine.

This module provides deterministic deal classification so the project can run
without affiliate APIs or external model dependencies.
"""

from __future__ import annotations

from typing import Dict, List


def _safe_float(value: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def evaluate_deal_signal(
    *,
    current_price: float,
    previous_day_price: float,
    average_30_day_price: float,
    min_30_day_price: float,
) -> Dict:
    """
    Classify the current price using simple and explainable business rules.

    Rules:
    - GENUINE_BARGAIN
      current_price < 0.9 * average_30_day_price
      and current_price <= min_30_day_price

    - FAKE_DISCOUNT
      current_price < 0.9 * previous_day_price
      and previous_day_price > 1.2 * average_30_day_price
    """
    current = _safe_float(current_price)
    previous = _safe_float(previous_day_price)
    avg_30 = _safe_float(average_30_day_price)
    min_30 = _safe_float(min_30_day_price)

    if current <= 0 or avg_30 <= 0:
        return {
            "label": "INSUFFICIENT_DATA",
            "score": 0.0,
            "message": "Need more historical data to classify this deal.",
            "metrics": {
                "current_price": current,
                "previous_day_price": previous,
                "average_30_day_price": avg_30,
                "min_30_day_price": min_30,
            },
        }

    if current < (0.9 * avg_30) and current <= min_30:
        return {
            "label": "GENUINE_BARGAIN",
            "score": 0.95,
            "message": "Current price is a real 30-day low and well below average.",
            "metrics": {
                "current_price": current,
                "previous_day_price": previous,
                "average_30_day_price": avg_30,
                "min_30_day_price": min_30,
            },
        }

    if previous > 0 and current < (0.9 * previous) and previous > (1.2 * avg_30):
        return {
            "label": "FAKE_DISCOUNT",
            "score": 0.1,
            "message": "Previous-day price looks inflated versus the 30-day average.",
            "metrics": {
                "current_price": current,
                "previous_day_price": previous,
                "average_30_day_price": avg_30,
                "min_30_day_price": min_30,
            },
        }

    return {
        "label": "NORMAL",
        "score": 0.5,
        "message": "Price is in normal range based on recent history.",
        "metrics": {
            "current_price": current,
            "previous_day_price": previous,
            "average_30_day_price": avg_30,
            "min_30_day_price": min_30,
        },
    }


def evaluate_from_history(prices: List[float]) -> Dict:
    """
    Convenience wrapper that computes required values from a price list.
    Expects prices in chronological order.
    """
    valid_prices = [float(p) for p in prices if p is not None]
    if len(valid_prices) < 2:
        return {
            "label": "INSUFFICIENT_DATA",
            "score": 0.0,
            "message": "Need at least 2 historical price points.",
            "metrics": {
                "current_price": valid_prices[-1] if valid_prices else 0.0,
                "previous_day_price": 0.0,
                "average_30_day_price": 0.0,
                "min_30_day_price": 0.0,
            },
        }

    current = valid_prices[-1]
    previous = valid_prices[-2]
    avg_30 = sum(valid_prices) / len(valid_prices)
    min_30 = min(valid_prices)

    return evaluate_deal_signal(
        current_price=current,
        previous_day_price=previous,
        average_30_day_price=avg_30,
        min_30_day_price=min_30,
    )
