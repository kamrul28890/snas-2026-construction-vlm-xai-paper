"""Validate normalized model-output files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.model_harness import validate_output_row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=ROOT / "results" / "frozen_model_outputs" / "pilot_annotation_bootstrap.jsonl",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=ROOT / "results" / "frozen_model_outputs" / "pilot_annotation_bootstrap.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with args.jsonl.open("r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    with args.csv.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(rows) != len(csv_rows):
        raise RuntimeError(f"JSONL/CSV row mismatch: {len(rows)} != {len(csv_rows)}")
    for row in rows:
        validate_output_row(row)
    print(f"Validated {len(rows)} model-output rows from {args.jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

