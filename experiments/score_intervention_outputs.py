"""Score intervention outputs against an unmasked baseline output file."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.intervention_metrics import (
    read_jsonl,
    summarize_intervention_outputs,
    validate_intervention_outputs,
    write_detail_rows,
    write_summary_rows,
)
from faithbench.metrics import load_jsonl, load_manifest_by_key


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--intervention-output",
        type=Path,
        default=ROOT / "results" / "intervention_outputs" / "pilot_florence_interventions.jsonl",
    )
    parser.add_argument(
        "--intervention-csv",
        type=Path,
        default=ROOT / "results" / "intervention_outputs" / "pilot_florence_interventions.csv",
    )
    parser.add_argument(
        "--baseline-output",
        type=Path,
        default=ROOT / "results" / "frozen_model_outputs" / "pilot_florence_grounding.jsonl",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "benchmark" / "splits" / "pilot_manifest.csv",
    )
    parser.add_argument("--name", default="pilot_florence_interventions")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    intervention_rows = validate_intervention_outputs(
        jsonl_path=args.intervention_output,
        csv_path=args.intervention_csv,
    )
    summary_rows, detail_rows = summarize_intervention_outputs(
        intervention_rows=intervention_rows,
        baseline_rows=load_jsonl(args.baseline_output),
        manifest_by_key=load_manifest_by_key(args.manifest),
    )
    out_dir = ROOT / "results" / "tables"
    write_summary_rows(summary_rows, out_dir / f"{args.name}_summary.csv")
    write_detail_rows(detail_rows, out_dir / f"{args.name}_per_intervention.csv")
    print(f"Wrote {len(summary_rows)} intervention summary metrics for {args.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
