"""Adaptive weighting rules for UAV stability scoring.

The weighting system is intentionally transparent. It uses context modifiers
rather than a hidden model so users can inspect and tune the behavior.
"""

from __future__ import annotations

from typing import Any, Dict

from .models import ScoreConfig
from .utils import normalize_weights


def adaptive_weights(row: Dict[str, Any], config: ScoreConfig) -> Dict[str, float]:
    """Return adaptive component weights for a telemetry row.

    Context rules:
    - high wind increases velocity and IMU importance
    - heavy payload increases battery and vertical-motion importance
    - low satellite count increases GPS risk attention but poor satellite count
      also means GPS readings should be interpreted cautiously
    - high altitude increases battery and stability sensitivity
    """
    weights = dict(config.default_weights)

    wind_speed = _float(row.get("wind_speed_mps"), 0.0)
    payload = _float(row.get("payload_kg"), 0.0)
    altitude = _float(row.get("altitude_m"), 0.0)
    satellites = _float(row.get("satellite_count"), 10.0)

    if wind_speed >= 8.0:
        weights["velocity"] *= 1.20
        weights["imu"] *= 1.25

    if payload >= 1.0:
        weights["battery"] *= 1.25
        weights["velocity"] *= 1.10

    if altitude >= 120.0:
        weights["battery"] *= 1.15
        weights["imu"] *= 1.10

    if satellites < config.low_satellite_count:
        weights["gps"] *= 1.15
        weights["imu"] *= 1.05

    return normalize_weights(weights)


def _float(value: Any, default: float) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default
