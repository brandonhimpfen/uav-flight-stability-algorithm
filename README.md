# UAV Flight Stability Algorithm

A lightweight, explainable Python package for detecting abnormal UAV flight stability patterns from telemetry logs.

Version 1 is designed as an offline flight-log analysis tool. It does not control aircraft, replace an autopilot, or provide certified aviation safety decisions. It produces an interpretable anomaly score from telemetry so engineers, researchers, students, and maintainers can inspect flight behavior after a flight or during simulation.

## What the project does

The algorithm reads UAV telemetry data and produces:

- a stability anomaly score from 0 to 100
- a human-readable severity level
- four component scores: velocity instability, GPS deviation, IMU inconsistency, and battery stress
- adaptive score weighting based on flight context
- smoothed anomaly scores over time
- reason codes explaining why high-risk moments were flagged
- CSV and JSON reports

## Why this exists

Many UAV monitoring systems rely on static thresholds. For example, they may warn when voltage drops below a fixed value or when GPS accuracy exceeds a fixed limit. Static thresholds are useful, but they do not always account for context.

A voltage drop may mean something different during a climb than during level flight. GPS drift may be more concerning when satellite count is low. IMU instability may matter more in high wind or during aggressive motion.

This project introduces a simple adaptive anomaly scoring approach that adjusts the importance of different signals based on context.

## Core algorithm

At each timestamp, the algorithm computes a total anomaly score:

```text
A_t = w_v(t) * V_t + w_g(t) * G_t + w_i(t) * I_t + w_b(t) * B_t
```

Where:

- `A_t` is the total anomaly score at time `t`
- `V_t` is the velocity instability score
- `G_t` is the GPS deviation score
- `I_t` is the IMU inconsistency score
- `B_t` is the battery stress score
- `w_v(t)`, `w_g(t)`, `w_i(t)`, and `w_b(t)` are adaptive weights that can change over time

The score is normalized to a 0 to 100 scale.

## Severity levels

| Score | Level |
|---:|---|
| 0-25 | Normal |
| 26-50 | Mild instability |
| 51-75 | Moderate anomaly |
| 76-100 | Severe anomaly |

## Installation

Clone or download this repository, then install it locally:

```bash
pip install -e .
```

For development and tests:

```bash
pip install -e .[dev]
pytest
```

## Quick start

Analyze the included sample flight log:

```bash
uav-stability analyze examples/data/sample_flight.csv --output reports/sample_report.json --csv-output reports/sample_timeline.csv
```

Or run the example script:

```bash
python examples/analyze_log.py examples/data/sample_flight.csv
```

## Input CSV format

The analyzer expects a CSV file with at least the following columns:

```text
timestamp,latitude,longitude,altitude_m,ground_speed_mps,vertical_speed_mps,roll_deg,pitch_deg,yaw_deg,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,gps_accuracy_m,satellite_count,battery_voltage_v,battery_current_a,battery_percent,flight_mode
```

Optional contextual columns can improve adaptive weighting:

```text
wind_speed_mps,payload_kg,aircraft_model
```

See `docs/input-schema.md` for the full schema.

## Example output

```json
{
  "overall_score": 57.42,
  "overall_level": "Moderate anomaly",
  "top_contributors": {
    "imu": 0.36,
    "battery": 0.27,
    "gps": 0.22,
    "velocity": 0.15
  },
  "highest_risk_timestamp": "2026-05-16T14:32:18Z"
}
```

## Documentation

- `docs/algorithm.md` explains the algorithm, scoring model, adaptive weighting, smoothing, and limitations.
- `docs/input-schema.md` describes the telemetry input format.
- `docs/evaluation.md` explains how to evaluate the algorithm using synthetic anomaly injection and scenario testing.
- `docs/safety-and-limitations.md` explains intended use and safety boundaries.
- `docs/roadmap.md` outlines possible future versions.

## Project status

This is version 1.0.0. It is intentionally simple, explainable, and easy to inspect. The goal is to provide a credible foundation for future research, testing, and model-assisted improvement.

## Safety notice

This software is for research, simulation, education, and offline analysis. It is not certified aviation software. It must not be used as the sole basis for flight control, collision avoidance, mission approval, aircraft certification, or safety-critical decisions.

## License

MIT License. See `LICENSE`.
