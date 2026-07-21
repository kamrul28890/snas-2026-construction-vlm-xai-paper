"""Summarize human-audit completion and answer-label agreement."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VALID_LABELS = {"compliant", "violation", "uncertain"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001.csv")
    parser.add_argument("--name", default="human_audit_batch_001")
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def label_present(value: str) -> bool:
    return value in VALID_LABELS


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    annotator_1 = [row for row in rows if label_present(row["annotator_1_answer_label"])]
    annotator_2 = [row for row in rows if label_present(row["annotator_2_answer_label"])]
    both = [
        row
        for row in rows
        if label_present(row["annotator_1_answer_label"]) and label_present(row["annotator_2_answer_label"])
    ]
    adjudicated = [row for row in rows if label_present(row["adjudicated_answer_label"])]
    disagreements = [row for row in both if row["annotator_1_answer_label"] != row["annotator_2_answer_label"]]
    adjudicated_disagreements = [row for row in disagreements if label_present(row["adjudicated_answer_label"])]
    final_labeled = [
        row
        for row in rows
        if (
            label_present(row["adjudicated_answer_label"])
            or (
                label_present(row["annotator_1_answer_label"])
                and row["annotator_1_answer_label"] == row["annotator_2_answer_label"]
            )
        )
    ]
    agreement = (
        sum(1 for row in both if row["annotator_1_answer_label"] == row["annotator_2_answer_label"]) / len(both)
        if both
        else math.nan
    )
    return [
        _metric("row_count", len(rows), len(rows), "audit rows in batch"),
        _metric("annotator_1_completion_rate", len(annotator_1) / len(rows) if rows else math.nan, len(rows), "rows with annotator 1 answer label"),
        _metric("annotator_2_completion_rate", len(annotator_2) / len(rows) if rows else math.nan, len(rows), "rows with annotator 2 answer label"),
        _metric("dual_annotation_completion_rate", len(both) / len(rows) if rows else math.nan, len(rows), "rows with both answer labels"),
        _metric("adjudication_completion_rate", len(adjudicated) / len(rows) if rows else math.nan, len(rows), "rows with adjudicated answer label"),
        _metric(
            "disagreement_adjudication_completion_rate",
            len(adjudicated_disagreements) / len(disagreements) if disagreements else math.nan,
            len(disagreements),
            "A/B disagreement rows with returned adjudication",
        ),
        _metric(
            "final_label_completion_rate",
            len(final_labeled) / len(rows) if rows else math.nan,
            len(rows),
            "rows with either A/B consensus label or returned adjudication",
        ),
        _metric("raw_answer_agreement", agreement, len(both), "exact annotator 1/2 answer-label agreement"),
    ]


def _metric(metric_id: str, value: float | int, n: int, notes: str) -> dict[str, str]:
    numeric = float(value)
    return {
        "metric_id": metric_id,
        "value": "" if math.isnan(numeric) else str(numeric),
        "n": str(n),
        "notes": notes,
    }


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric_id", "value", "n", "notes"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    rows = summarize(read_rows(args.batch))
    out_path = ROOT / "results" / "tables" / f"{args.name}_status.csv"
    write_rows(rows, out_path)
    print(f"Wrote {len(rows)} human-audit status metrics to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
