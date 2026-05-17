# Evaluation Guide

Version 1 is an explainable scoring algorithm. Evaluation should focus on whether the score behaves reasonably across known scenarios.

## Evaluation goals

A good evaluation should answer:

- Does the algorithm keep normal flights mostly low scoring?
- Does it increase scores during injected anomalies?
- Are the reason codes useful?
- Are component scores aligned with the anomaly type?
- Does smoothing reduce one-sample noise?
- Do adaptive weights change in expected ways?

## Suggested test scenarios

### 1. Normal flight

Create a flight with stable GPS, smooth velocity, normal attitude, and gradual battery drain.

Expected result:

- mostly `Normal`
- low component scores
- few or no reason codes

### 2. GPS drift

Inject sudden position jumps, poor GPS accuracy, or low satellite count.

Expected result:

- GPS component score rises
- reason codes include GPS-related flags
- total score rises depending on adaptive weights

### 3. IMU instability

Inject sudden roll, pitch, yaw, or gyro spikes.

Expected result:

- IMU component score rises
- reason codes include IMU-related flags
- score becomes more severe if wind speed is also high

### 4. Battery stress

Inject voltage sag, high current draw, or rapid battery percentage drop.

Expected result:

- battery component score rises
- reason codes include battery-related flags
- score becomes more severe if payload or altitude is high

### 5. Unsafe descent pattern

Inject rapid changes in vertical speed or unstable descent behavior.

Expected result:

- velocity component score rises
- IMU may rise if attitude also changes
- total score should increase around the event window

## Synthetic anomaly injection

A practical evaluation method is to start with a clean sample log and inject controlled anomalies.

Examples:

- add 0.0005 degrees to latitude for one row to simulate a GPS jump
- reduce satellite count to 4 for several rows
- increase gyro values for an instability event
- drop voltage by 1.0 V in one row
- increase current draw during climb

## Metrics

Because version 1 may not have labelled real-world data, start with scenario-based metrics:

| Metric | Meaning |
|---|---|
| Normal score range | Typical score range during clean flight. |
| Anomaly score lift | Difference between normal and injected anomaly periods. |
| Reason-code accuracy | Whether the right reason codes appear for each scenario. |
| False-positive count | Number of high scores during normal segments. |
| Peak localization | Whether the highest score appears near the injected anomaly. |

## Recommended acceptance criteria for version 1

A reasonable version 1 acceptance test could be:

- normal segments remain mostly below 25
- injected anomalies produce visible score increases
- moderate injected anomalies reach at least 51
- severe injected anomalies reach at least 76 after smoothing if sustained
- reason codes match the injected anomaly type

## Important note

These tests do not prove the algorithm is operationally safe. They only show that the scoring system behaves consistently under controlled inputs.
