# Input Schema

The analyzer expects a CSV telemetry log. Each row represents one timestamped telemetry point.

## Required columns

| Column | Type | Description |
|---|---:|---|
| `timestamp` | string | Timestamp for the telemetry sample. ISO 8601 is recommended. |
| `latitude` | float | Latitude in decimal degrees. |
| `longitude` | float | Longitude in decimal degrees. |
| `altitude_m` | float | Altitude in meters. |
| `ground_speed_mps` | float | Ground speed in meters per second. |
| `vertical_speed_mps` | float | Vertical speed in meters per second. Positive values indicate climb, negative values indicate descent. |
| `roll_deg` | float | Roll angle in degrees. |
| `pitch_deg` | float | Pitch angle in degrees. |
| `yaw_deg` | float | Yaw angle in degrees. |
| `accel_x` | float | Acceleration on X axis. |
| `accel_y` | float | Acceleration on Y axis. |
| `accel_z` | float | Acceleration on Z axis. |
| `gyro_x` | float | Gyroscope X axis value. |
| `gyro_y` | float | Gyroscope Y axis value. |
| `gyro_z` | float | Gyroscope Z axis value. |
| `gps_accuracy_m` | float | Estimated GPS accuracy in meters. |
| `satellite_count` | integer | Number of GPS satellites used or visible. |
| `battery_voltage_v` | float | Battery voltage. |
| `battery_current_a` | float | Battery current draw in amps. |
| `battery_percent` | float | Battery percentage remaining. |
| `flight_mode` | string | Flight mode or autopilot state. |

## Optional columns

| Column | Type | Description |
|---|---:|---|
| `wind_speed_mps` | float | Estimated wind speed in meters per second. Used for adaptive weighting. |
| `payload_kg` | float | Estimated payload weight in kilograms. Used for adaptive weighting. |
| `aircraft_model` | string | Aircraft model or platform name. Reserved for future calibration. |
| `position_jump_m` | float | Explicit position jump distance in meters. If omitted, the analyzer estimates jump distance from latitude and longitude changes. |

## Recommended timestamp format

Use ISO 8601 when possible:

```text
2026-05-16T14:32:18Z
```

## Data quality recommendations

For better results:

- keep telemetry intervals consistent
- avoid mixing flights in one file
- avoid missing timestamps
- include GPS accuracy and satellite count when available
- include current draw and voltage when available
- use the same unit system throughout the file

## Minimal example

```csv
timestamp,latitude,longitude,altitude_m,ground_speed_mps,vertical_speed_mps,roll_deg,pitch_deg,yaw_deg,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,gps_accuracy_m,satellite_count,battery_voltage_v,battery_current_a,battery_percent,flight_mode
2026-05-16T14:32:00Z,43.6532,-79.3832,30,4.2,0.1,1.2,2.1,85,0.1,0.2,9.8,0.01,0.02,0.03,2.5,12,16.4,8.2,94,AUTO
```
