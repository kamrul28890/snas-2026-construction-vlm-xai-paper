"""Generate slice metrics from per-example model score rows."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SLICE_COLUMNS = ["rule_id", "annotation_ambiguous", "annotation_applies_to_image"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--per-example",
        type=Path,
        default=ROOT / "results" / "tables" / "scaleup_florence_grounding_per_example_scores.csv",
    )
    parser.add_argument("--name", default="scaleup_florence_grounding")
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def bool_rate(rows: list[dict[str, str]], field: str) -> float:
    if not rows:
        return math.nan
    return sum(1 for row in rows if row[field] == "true") / len(rows)


def numeric_mean(rows: list[dict[str, str]], field: str) -> tuple[float, int]:
    values = [float(row[field]) for row in rows if row[field]]
    if not values:
        return math.nan, 0
    return sum(values) / len(values), len(values)


def summarize_slice(rows: list[dict[str, str]], *, slice_type: str, slice_value: str) -> dict[str, str]:
    mean_iou, iou_n = numeric_mean(rows, "best_evidence_iou")
    mean_drift, drift_n = numeric_mean(rows, "best_evidence_centroid_drift")
    return {
        "slice_type": slice_type,
        "slice_value": slice_value,
        "n": str(len(rows)),
        "accuracy": _fmt(bool_rate(rows, "answer_correct")),
        "invalid_rate": _fmt(bool_rate(rows, "invalid_output")),
        "evidence_presence_rate": _fmt(bool_rate(rows, "has_predicted_evidence")),
        "reference_evidence_rate": _fmt(bool_rate(rows, "has_reference_evidence")),
        "mean_best_evidence_iou": _fmt(mean_iou),
        "mean_best_evidence_iou_n": str(iou_n),
        "mean_best_evidence_centroid_drift": _fmt(mean_drift),
        "mean_best_evidence_centroid_drift_n": str(drift_n),
    }


def build_slices(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output = [summarize_slice(rows, slice_type="overall", slice_value="all")]
    for column in SLICE_COLUMNS:
        groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            groups[row[column]].append(row)
        for value in sorted(groups):
            output.append(summarize_slice(groups[value], slice_type=column, slice_value=value))
    return output


def _fmt(value: float) -> str:
    return "" if math.isnan(value) else str(float(value))


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    rows = read_rows(args.per_example)
    output = build_slices(rows)
    out_path = ROOT / "results" / "tables" / f"{args.name}_slices.csv"
    write_rows(output, out_path)
    print(f"Wrote {len(output)} slice rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
