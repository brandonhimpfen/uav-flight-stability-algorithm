# Algorithm Design

## Overview

The UAV Flight Stability Algorithm is an explainable adaptive anomaly scoring system for UAV telemetry logs.

It is designed to answer one narrow question:

> Does this recent flight behavior look unusually unstable compared with expected telemetry patterns?

Version 1 does this through a transparent scoring pipeline rather than a black-box model. It calculates component anomaly scores, adjusts their importance based on context, smooths the result over time, and produces a final score from 0 to 100.

## Design goals

The version 1 algorithm is built around five goals:

1. **Explainability**: every high score should have a reason code.
2. **Simplicity**: the algorithm should be understandable from the code and documentation.
3. **Adaptability**: signal weights should change based on flight context.
4. **Reproducibility**: the same input log should produce the same output report.
5. **Safety boundary**: the algorithm should analyze telemetry, not control aircraft.

## Core formula

At each timestamp, the total anomaly score is calculated as:

```text
A_t = w_v(t) * V_t + w_g(t) * G_t + w_i(t) * I_t + w_b(t) * B_t
```

Where:

- `A_t` is the anomaly score at time `t`
- `V_t` is the velocity instability score
- `G_t` is the GPS deviation score
- `I_t` is the IMU inconsistency score
- `B_t` is the battery stress score
- `w_v(t)`, `w_g(t)`, `w_i(t)`, and `w_b(t)` are adaptive weights

Each component score is normalized to a 0 to 100 scale.

## Component 1: Velocity instability

Velocity instability captures sudden changes in speed, climb/descent behavior, and acceleration magnitude.

The component uses:

- ground speed change
- vertical speed change
- accelerometer magnitude

A high velocity score can indicate abrupt movement, unstable descent, sudden braking, or aggressive maneuvering.

Reason codes include:

- `velocity_speed_delta`
- `velocity_vertical_speed_change`
- `velocity_high_acceleration`

## Component 2: GPS deviation

GPS deviation captures poor GPS quality and unusual position movement.

The component uses:

- GPS accuracy estimate
- satellite count
- position jump between consecutive rows

A high GPS score can indicate drift, poor signal quality, or a sudden location jump inconsistent with normal movement.

Reason codes include:

- `gps_poor_accuracy`
- `gps_position_jump`
- `gps_low_satellite_count`

## Component 3: IMU inconsistency

IMU inconsistency captures unstable attitude changes, rotation, and unusual orientation.

The component uses:

- roll change
- pitch change
- yaw change
- gyroscope magnitude
- roll and pitch magnitude

A high IMU score can indicate vibration, instability, sudden attitude changes, or sensor disagreement.

Reason codes include:

- `imu_attitude_change`
- `imu_high_gyro`
- `imu_high_attitude_magnitude`

## Component 4: Battery stress

Battery stress captures signs of electrical load and rapid battery deterioration.

The component uses:

- voltage sag
- current draw
- battery percentage drop

A high battery score can indicate abnormal load, voltage instability, high power demand, or rapid battery depletion.

Reason codes include:

- `battery_voltage_sag`
- `battery_high_current_draw`
- `battery_rapid_percent_drop`

## Normalization

Each metric is converted to a 0 to 100 scale using configurable threshold values.

For example, if a speed change reaches the configured high-speed-change threshold, it receives a score near 100 for that submetric. Lower changes receive proportionally lower scores.

This approach makes different units comparable. GPS accuracy in meters, current draw in amps, and roll changes in degrees can all contribute to a single anomaly score.

## Adaptive weights

The main differentiator in the algorithm is adaptive weighting.

A static model might always use:

```text
velocity = 0.25
gps = 0.25
imu = 0.30
battery = 0.20
```

This project begins with those defaults but adjusts them based on context.

### High wind

When wind speed is high, velocity and IMU scores receive more weight because flight motion and attitude instability become more important.

### Heavy payload

When payload is higher, battery and velocity scores receive more weight because power demand and climb/descent behavior become more important.

### High altitude

At higher altitude, battery and IMU sensitivity increase because instability and power stress may carry greater operational significance.

### Low satellite count

When satellite count is low, GPS receives more attention, but the interpretation should remain cautious because GPS quality itself may be degraded.

## Temporal smoothing

The algorithm applies exponential smoothing to reduce false positives caused by single-sample noise:

```text
S_t = alpha * A_t + (1 - alpha) * S_{t-1}
```

Where:

- `S_t` is the smoothed score at time `t`
- `A_t` is the raw anomaly score at time `t`
- `alpha` controls how quickly the score reacts to new data

The default `alpha` is `0.30`.

A lower alpha produces smoother scores. A higher alpha reacts more quickly to sudden events.

## Severity levels

The smoothed score is mapped to a severity label:

| Score | Level |
|---:|---|
| 0-25 | Normal |
| 26-50 | Mild instability |
| 51-75 | Moderate anomaly |
| 76-100 | Severe anomaly |

These thresholds are configurable.

## Explainability

Each timeline point includes:

- raw total score
- smoothed score
- severity label
- component scores
- adaptive weights
- reason codes

This allows users to understand not only that a moment was flagged, but why it was flagged.

## What makes this algorithm different from static thresholding

Static threshold systems ask:

> Did this value exceed a fixed limit?

This algorithm asks:

> How unusual is this behavior across multiple telemetry signals, and how should those signals be weighted under the current flight context?

That makes the system more flexible while still remaining transparent.

## What version 1 does not do

Version 1 does not:

- control a UAV
- replace a flight controller
- perform collision avoidance
- certify safe or unsafe flight
- learn aircraft-specific baselines automatically
- use deep learning or black-box prediction
- guarantee operational correctness

## Future machine learning extensions

Machine learning could later improve:

- aircraft-specific baseline learning
- adaptive threshold tuning
- false-positive reduction
- anomaly pattern classification
- weight optimization from labelled logs
- forecasting of instability before it occurs

However, version 1 intentionally keeps the algorithm explainable and deterministic.
