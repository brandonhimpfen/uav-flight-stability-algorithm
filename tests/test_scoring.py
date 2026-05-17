from pathlib import Path

from uav_stability import analyze_flight_log


def test_sample_flight_scores():
    result = analyze_flight_log(Path("examples/data/sample_flight.csv"))
    assert result.overall_score > 25
    assert result.highest_risk_timestamp is not None
    assert len(result.timeline) == 40
    assert set(result.top_contributors.keys()) == {"velocity", "gps", "imu", "battery"}


def test_reason_codes_present_for_anomaly():
    result = analyze_flight_log(Path("examples/data/sample_flight.csv"))
    reason_codes = {code for point in result.timeline for code in point.reason_codes}
    assert "imu_attitude_change" in reason_codes or "imu_high_gyro" in reason_codes
    assert "gps_low_satellite_count" in reason_codes
    assert "battery_high_current_draw" in reason_codes
