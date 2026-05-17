"""Example: analyze a UAV telemetry CSV file."""

from __future__ import annotations

import sys
from pathlib import Path

from uav_stability import analyze_flight_log
from uav_stability.scoring import write_json_report, write_timeline_csv


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data/sample_flight.csv")
    result = analyze_flight_log(path)

    print(f"Overall Stability Risk: {result.overall_score} / 100")
    print(f"Level: {result.overall_level}")
    print(f"Highest-risk timestamp: {result.highest_risk_timestamp}")
    print("Top contributors:")
    for name, share in result.top_contributors.items():
        print(f"  - {name}: {share:.1%}")

    write_json_report(result, "reports/example_report.json")
    write_timeline_csv(result, "reports/example_timeline.csv")
    print("Reports written to reports/.")


if __name__ == "__main__":
    main()
