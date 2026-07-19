"""Validate the generated scale-up candidate manifest."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    manifest_path = ROOT / "benchmark" / "splits" / "scaleup_candidate_manifest.csv"
    summary_path = ROOT / "benchmark" / "splits" / "scaleup_candidate_manifest_summary.json"
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    if len(rows) != summary["row_count"]:
        raise RuntimeError("Scale-up row count mismatch")
    if not rows:
        raise RuntimeError("Scale-up manifest is empty")
    required = {
        "image_id",
        "rule_id",
        "expected_answer_seed",
        "image_width",
        "image_height",
        "source_violation_boxes_xyxy",
        "needs_human_label",
    }
    for row in rows:
        missing = [field for field in required if field not in row]
        if missing:
            raise RuntimeError(f"Missing fields: {missing}")
        if row["expected_answer_seed"] not in {"compliant", "violation"}:
            raise RuntimeError(f"Unexpected seed answer: {row['expected_answer_seed']}")
        json.loads(row["source_violation_boxes_xyxy"])
    print(f"Validated {len(rows)} scale-up candidate rows.")
    print(f"Class counts: {summary['class_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

