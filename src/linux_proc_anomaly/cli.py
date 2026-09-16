"""Command-line entry point: sample /proc metrics to a CSV file."""

from __future__ import annotations

import argparse
import csv
import os

from .collector import FIELDNAMES, collect


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", type=float, default=10.0, help="Collection duration in seconds")
    parser.add_argument("--interval", type=float, default=0.5, help="Sampling interval in seconds")
    parser.add_argument("--out", type=str, default="collector_run.csv", help="Output CSV path")
    args = parser.parse_args()

    result = collect(args.duration, args.interval)

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(result.rows)

    print(f"Samples collected : {len(result.rows)}")
    print(f"Wall time elapsed : {result.wall_elapsed_s:.3f} s")
    print(f"Collector CPU time: {result.proc_elapsed_s:.6f} s")
    print(f"Measured overhead : {result.overhead_pct:.4f}% of wall-clock time")
    print(f"Output written to : {args.out}")


if __name__ == "__main__":
    main()
