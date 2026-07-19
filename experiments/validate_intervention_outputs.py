"""Validate intervention output JSONL/CSV artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.intervention_metrics import validate_intervention_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=ROOT / "results" / "intervention_outputs" / "pilot_florence_interventions.jsonl",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=ROOT / "results" / "intervention_outputs" / "pilot_florence_interventions.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = validate_intervention_outputs(jsonl_path=args.jsonl, csv_path=args.csv)
    print(f"Validated {len(rows)} intervention output rows from {args.jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
