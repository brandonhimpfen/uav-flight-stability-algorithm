"""Command-line interface for UAV flight stability analysis."""

from __future__ import annotations

import argparse
from dataclasses import asdict

from .scoring import analyze_flight_log, write_json_report, write_timeline_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="uav-stability",
        description="Analyze UAV telemetry logs with an adaptive flight stability anomaly algorithm.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a telemetry CSV file.")
    analyze.add_argument("csv_file", help="Path to input telemetry CSV file.")
    analyze.add_argument("--output", "-o", help="Path to write JSON report.")
    analyze.add_argument("--csv-output", help="Path to write scored timeline CSV.")

    args = parser.parse_args()

    if args.command == "analyze":
        result = analyze_flight_log(args.csv_file)
        print(f"Overall Stability Risk: {result.overall_score} / 100")
        print(f"Level: {result.overall_level}")
        print(f"Highest-risk timestamp: {result.highest_risk_timestamp}")
        print("Top contributors:")
        for name, share in result.top_contributors.items():
            print(f"  - {name}: {share:.1%}")

        if args.output:
            write_json_report(result, args.output)
            print(f"JSON report written to: {args.output}")
        if args.csv_output:
            write_timeline_csv(result, args.csv_output)
            print(f"Timeline CSV written to: {args.csv_output}")
