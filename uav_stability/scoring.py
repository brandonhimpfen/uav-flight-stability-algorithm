"""Main scoring pipeline for the UAV Flight Stability Algorithm."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from .adaptive_weights import adaptive_weights
from .models import AnalysisResult, ScoreConfig, TimelinePoint
from .signals import battery_stress, gps_deviation, imu_inconsistency, velocity_instability
from .smoothing import exponential_smooth
from .utils import severity_level

REQUIRED_COLUMNS = [
    "timestamp",
    "latitude",
    "longitude",
    "altitude_m",
    "ground_speed_mps",
    "vertical_speed_mps",
    "roll_deg",
    "pitch_deg",
    "yaw_deg",
    "accel_x",
    "accel_y",
    "accel_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "gps_accuracy_m",
    "satellite_count",
    "battery_voltage_v",
    "battery_current_a",
    "battery_percent",
    "flight_mode",
]


def analyze_flight_log(path: str | Path, config: Optional[ScoreConfig] = None) -> AnalysisResult:
    """Read a CSV flight log and return a complete analysis result."""
    df = pd.read_csv(path)
    return score_dataframe(df, config=config)


def score_dataframe(df: pd.DataFrame, config: Optional[ScoreConfig] = None) -> AnalysisResult:
    """Score a telemetry dataframe.

    Parameters
    ----------
    df:
        Telemetry data with the required input columns.
    config:
        Optional scoring configuration.
    """
    config = config or ScoreConfig()
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    rows = df.to_dict(orient="records")
    timeline = []
    previous_row = None
    previous_smoothed = None

    contributor_totals = {"velocity": 0.0, "gps": 0.0, "imu": 0.0, "battery": 0.0}

    for row in rows:
        velocity_score, velocity_reasons = velocity_instability(row, previous_row, config)
        gps_score, gps_reasons = gps_deviation(row, previous_row, config)
        imu_score, imu_reasons = imu_inconsistency(row, previous_row, config)
        battery_score, battery_reasons = battery_stress(row, previous_row, config)

        component_scores = {
            "velocity": velocity_score,
            "gps": gps_score,
            "imu": imu_score,
            "battery": battery_score,
        }
        weights = adaptive_weights(row, config)
        total_score = sum(component_scores[key] * weights[key] for key in component_scores)
        smoothed = exponential_smooth(total_score, previous_smoothed, config.smoothing_alpha)
        level = severity_level(
            smoothed,
            mild=config.mild_score_threshold,
            moderate=config.moderate_score_threshold,
            severe=config.severe_score_threshold,
        )

        for key in contributor_totals:
            contributor_totals[key] += component_scores[key] * weights[key]

        timeline.append(
            TimelinePoint(
                timestamp=str(row["timestamp"]),
                total_score=round(float(total_score), 2),
                smoothed_score=round(float(smoothed), 2),
                level=level,
                component_scores={key: round(float(value), 2) for key, value in component_scores.items()},
                weights={key: round(float(value), 4) for key, value in weights.items()},
                reason_codes=velocity_reasons + gps_reasons + imu_reasons + battery_reasons,
            )
        )
        previous_row = row
        previous_smoothed = smoothed

    if not timeline:
        return AnalysisResult(0.0, "Normal", None, {}, [])

    highest = max(timeline, key=lambda point: point.smoothed_score)
    overall_score = round(max(point.smoothed_score for point in timeline), 2)
    overall_level = severity_level(
        overall_score,
        mild=config.mild_score_threshold,
        moderate=config.moderate_score_threshold,
        severe=config.severe_score_threshold,
    )

    total_contribution = sum(contributor_totals.values()) or 1.0
    top_contributors = {
        key: round(value / total_contribution, 4)
        for key, value in sorted(contributor_totals.items(), key=lambda item: item[1], reverse=True)
    }

    return AnalysisResult(
        overall_score=overall_score,
        overall_level=overall_level,
        highest_risk_timestamp=highest.timestamp,
        top_contributors=top_contributors,
        timeline=timeline,
    )


def write_json_report(result: AnalysisResult, path: str | Path) -> None:
    """Write an analysis result as JSON."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(asdict(result), file, indent=2)


def write_timeline_csv(result: AnalysisResult, path: str | Path) -> None:
    """Write the timeline portion of an analysis result as CSV."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    records = []
    for point in result.timeline:
        record: Dict[str, object] = {
            "timestamp": point.timestamp,
            "total_score": point.total_score,
            "smoothed_score": point.smoothed_score,
            "level": point.level,
            "reason_codes": ";".join(point.reason_codes),
        }
        for key, value in point.component_scores.items():
            record[f"score_{key}"] = value
        for key, value in point.weights.items():
            record[f"weight_{key}"] = value
        records.append(record)
    pd.DataFrame(records).to_csv(path, index=False)
