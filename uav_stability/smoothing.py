"""Temporal smoothing helpers."""

from __future__ import annotations


def exponential_smooth(current: float, previous_smoothed: float | None, alpha: float) -> float:
    """Apply exponential smoothing to reduce one-sample noise."""
    if previous_smoothed is None:
        return current
    alpha = max(0.0, min(1.0, alpha))
    return alpha * current + (1.0 - alpha) * previous_smoothed
