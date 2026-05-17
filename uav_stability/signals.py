"""Telemetry signal scoring functions.

Each function returns a component anomaly score from 0 to 100.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from .models import ScoreConfig
from .utils import clamp, normalize


def _get(row: Dict[str, Any], key: str, default: float = 0.0) -> float:
    value = row.get(key, default)
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def velocity_instability(row: Dict[str, Any], prev: Dict[str, Any] | None, config: ScoreConfig) -> Tuple[float, List[str]]:
    """Score speed, acceleration, and climb/descent instability."""
    reasons: List[str] = []
    speed = _get(row, "ground_speed_mps")
    vertical = _get(row, "vertical_speed_mps")
    accel_mag = math.sqrt(_get(row, "accel_x") ** 2 + _get(row, "accel_y") ** 2 + _get(row, "accel_z") ** 2)

    speed_delta = 0.0
    vertical_delta = 0.0
    if prev:
        speed_delta = speed - _get(prev, "ground_speed_mps")
        vertical_delta = vertical - _get(prev, "vertical_speed_mps")

    score = (
        0.45 * normalize(speed_delta, config.high_speed_delta_mps)
        + 0.35 * normalize(vertical_delta, config.high_vertical_speed_change_mps)
        + 0.20 * normalize(accel_mag, config.high_acceleration_magnitude)
    )

    if abs(speed_delta) > config.high_speed_delta_mps * 0.65:
        reasons.append("velocity_speed_delta")
    if abs(vertical_delta) > config.high_vertical_speed_change_mps * 0.65:
        reasons.append("velocity_vertical_speed_change")
    if accel_mag > config.high_acceleration_magnitude * 0.70:
        reasons.append("velocity_high_acceleration")

    return clamp(score), reasons


def gps_deviation(row: Dict[str, Any], prev: Dict[str, Any] | None, config: ScoreConfig) -> Tuple[float, List[str]]:
    """Score GPS quality, satellite count, and position jumps."""
    reasons: List[str] = []
    gps_accuracy = _get(row, "gps_accuracy_m")
    satellites = _get(row, "satellite_count")
    position_jump = _get(row, "position_jump_m")

    if position_jump == 0.0 and prev:
        lat_delta = abs(_get(row, "latitude") - _get(prev, "latitude"))
        lon_delta = abs(_get(row, "longitude") - _get(prev, "longitude"))
        # Approximate conversion for small movements. Good enough for anomaly hints.
        position_jump = math.sqrt(lat_delta**2 + lon_delta**2) * 111_000

    satellite_penalty = 0.0
    if satellites < config.low_satellite_count:
        satellite_penalty = ((config.low_satellite_count - satellites) / config.low_satellite_count) * 100.0

    score = (
        0.45 * normalize(gps_accuracy, config.poor_gps_accuracy_m)
        + 0.35 * normalize(position_jump, config.high_position_jump_m)
        + 0.20 * clamp(satellite_penalty)
    )

    if gps_accuracy > config.poor_gps_accuracy_m * 0.70:
        reasons.append("gps_poor_accuracy")
    if position_jump > config.high_position_jump_m * 0.60:
        reasons.append("gps_position_jump")
    if satellites < config.low_satellite_count:
        reasons.append("gps_low_satellite_count")

    return clamp(score), reasons


def imu_inconsistency(row: Dict[str, Any], prev: Dict[str, Any] | None, config: ScoreConfig) -> Tuple[float, List[str]]:
    """Score attitude changes and gyroscope instability."""
    reasons: List[str] = []
    roll = _get(row, "roll_deg")
    pitch = _get(row, "pitch_deg")
    yaw = _get(row, "yaw_deg")
    gyro_mag = math.sqrt(_get(row, "gyro_x") ** 2 + _get(row, "gyro_y") ** 2 + _get(row, "gyro_z") ** 2)

    attitude_change = 0.0
    if prev:
        attitude_change = max(
            abs(roll - _get(prev, "roll_deg")),
            abs(pitch - _get(prev, "pitch_deg")),
            abs(yaw - _get(prev, "yaw_deg")),
        )

    attitude_magnitude = max(abs(roll), abs(pitch))

    score = (
        0.45 * normalize(attitude_change, config.high_attitude_change_deg)
        + 0.35 * normalize(gyro_mag, config.high_gyro_magnitude)
        + 0.20 * normalize(attitude_magnitude, 35.0)
    )

    if attitude_change > config.high_attitude_change_deg * 0.65:
        reasons.append("imu_attitude_change")
    if gyro_mag > config.high_gyro_magnitude * 0.70:
        reasons.append("imu_high_gyro")
    if attitude_magnitude > 24.0:
        reasons.append("imu_high_attitude_magnitude")

    return clamp(score), reasons


def battery_stress(row: Dict[str, Any], prev: Dict[str, Any] | None, config: ScoreConfig) -> Tuple[float, List[str]]:
    """Score battery voltage sag, current draw, and rapid percentage drop."""
    reasons: List[str] = []
    voltage = _get(row, "battery_voltage_v")
    current = _get(row, "battery_current_a")
    percent = _get(row, "battery_percent")

    voltage_sag = 0.0
    battery_drop = 0.0
    if prev:
        voltage_sag = max(0.0, _get(prev, "battery_voltage_v") - voltage)
        battery_drop = max(0.0, _get(prev, "battery_percent") - percent)

    score = (
        0.45 * normalize(voltage_sag, config.high_voltage_sag_v)
        + 0.35 * normalize(current, config.high_current_draw_a)
        + 0.20 * normalize(battery_drop, config.high_battery_drop_percent)
    )

    if voltage_sag > config.high_voltage_sag_v * 0.60:
        reasons.append("battery_voltage_sag")
    if current > config.high_current_draw_a * 0.75:
        reasons.append("battery_high_current_draw")
    if battery_drop > config.high_battery_drop_percent * 0.70:
        reasons.append("battery_rapid_percent_drop")

    return clamp(score), reasons
