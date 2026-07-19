"""Score normalized model outputs against model-assisted annotations."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.metrics import (
    load_annotations,
    load_jsonl,
    load_manifest_by_key,
    score_model_outputs,
    write_score_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model-output",
        type=Path,
        default=ROOT / "results" / "frozen_model_outputs" / "pilot_annotation_bootstrap.jsonl",
    )
    parser.add_argument(
        "--name",
        default="pilot_annotation_bootstrap",
        help="Output stem for score files.",
    )
    parser.add_argument(
        "--annotations",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "benchmark" / "splits" / "pilot_manifest.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = score_model_outputs(
        model_output_rows=load_jsonl(args.model_output),
        annotations_by_key=load_annotations(args.annotations),
        manifest_by_key=load_manifest_by_key(args.manifest),
    )
    out_dir = ROOT / "results" / "tables"
    write_score_outputs(
        summary,
        summary_path=out_dir / f"{args.name}_scores.csv",
        examples_path=out_dir / f"{args.name}_per_example_scores.csv",
    )
    print(f"Wrote {len(summary.summary_rows)} summary metrics for {args.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
