# Safety and Limitations

## Intended use

This project is intended for:

- offline UAV telemetry analysis
- simulation analysis
- research and education
- anomaly-scoring experiments
- post-flight diagnostics
- algorithm development

## Not intended for

This project is not intended for:

- live flight control
- autonomous safety decisions
- collision avoidance
- aircraft certification
- mission approval
- regulatory compliance decisions
- emergency response decisions

## Why the distinction matters

A flight stability score can help identify suspicious telemetry patterns. It cannot determine the complete operational safety of a UAV flight.

Real-world UAV safety depends on many factors that are outside the scope of this package, including:

- airframe condition
- pilot training
- firmware behavior
- environmental conditions
- airspace rules
- payload configuration
- maintenance history
- sensor calibration
- local regulations

## Calibration required

The default thresholds are general-purpose starting values. They are not calibrated to a specific aircraft, firmware, payload, mission type, or environment.

Before using this project with real telemetry, users should calibrate thresholds using known normal logs and known abnormal logs for their specific aircraft and mission profile.

## Sensor quality

The algorithm depends on telemetry quality. Missing, delayed, noisy, or incorrectly scaled telemetry can produce misleading scores.

## False positives and false negatives

The algorithm may flag normal behavior as abnormal. It may also miss abnormal behavior.

This is especially likely when:

- the aircraft is operating in unusual conditions
- telemetry sampling intervals are inconsistent
- GPS data is poor
- battery telemetry is incomplete
- payload and weather context are missing
- thresholds are not calibrated

## Version 1 philosophy

Version 1 favors explainability over complexity. It is a foundation for experimentation, not a final operational system.
