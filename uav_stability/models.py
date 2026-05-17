"""Data models and configuration objects for UAV stability scoring."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScoreConfig:
    """Configuration for the adaptive UAV stability algorithm.

    The defaults are intentionally conservative and explainable. They are not
    calibrated to a specific aircraft and should be tuned before use with real
    operational data.
    """

    smoothing_alpha: float = 0.30
    severe_score_threshold: float = 76.0
    moderate_score_threshold: float = 51.0
    mild_score_threshold: float = 26.0
    default_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "velocity": 0.25,
            "gps": 0.25,
            "imu": 0.30,
            "battery": 0.20,
        }
    )

    # Normalization thresholds. Scores are clipped to 0-100.
    high_speed_delta_mps: float = 5.0
    high_vertical_speed_change_mps: float = 3.0
    high_acceleration_magnitude: float = 18.0
    high_position_jump_m: float = 30.0
    poor_gps_accuracy_m: float = 12.0
    low_satellite_count: int = 7
    high_attitude_change_deg: float = 18.0
    high_gyro_magnitude: float = 2.5
    high_voltage_sag_v: float = 1.2
    high_current_draw_a: float = 28.0
    high_battery_drop_percent: float = 3.0


@dataclass
class TimelinePoint:
    """A scored telemetry point."""

    timestamp: str
    total_score: float
    smoothed_score: float
    level: str
    component_scores: Dict[str, float]
    weights: Dict[str, float]
    reason_codes: List[str]


@dataclass
class AnalysisResult:
    """Summary of a complete flight-log analysis."""

    overall_score: float
    overall_level: str
    highest_risk_timestamp: Optional[str]
    top_contributors: Dict[str, float]
    timeline: List[TimelinePoint]
