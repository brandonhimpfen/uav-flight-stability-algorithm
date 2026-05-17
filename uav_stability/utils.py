"""Utility functions for scoring and normalization."""

from __future__ import annotations

import math
from typing import Dict


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Clamp a numeric value to a range."""
    if math.isnan(value) or math.isinf(value):
        return low
    return max(low, min(high, value))


def normalize(value: float, high_value: float) -> float:
    """Normalize a positive metric to a 0-100 anomaly score.

    Values at or above high_value map to 100. Values near zero map to 0.
    """
    if high_value <= 0:
        return 0.0
    return clamp((abs(value) / high_value) * 100.0)


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Normalize a dictionary of weights so values sum to 1."""
    cleaned = {key: max(0.0, float(value)) for key, value in weights.items()}
    total = sum(cleaned.values())
    if total <= 0:
        count = len(cleaned) or 1
        return {key: 1.0 / count for key in cleaned}
    return {key: value / total for key, value in cleaned.items()}


def severity_level(score: float, mild: float = 26.0, moderate: float = 51.0, severe: float = 76.0) -> str:
    """Return a human-readable severity level for a 0-100 score."""
    if score >= severe:
        return "Severe anomaly"
    if score >= moderate:
        return "Moderate anomaly"
    if score >= mild:
        return "Mild instability"
    return "Normal"
