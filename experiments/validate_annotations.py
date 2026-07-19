"""Validate generated model-assisted annotation files."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    annotation_path = ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl"
    csv_path = ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.csv"
    summary_path = ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotation_summary.json"
    with annotation_path.open("r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    if len(rows) != len(csv_rows):
        raise RuntimeError(f"JSONL/CSV row mismatch: {len(rows)} != {len(csv_rows)}")
    if len(rows) != summary["row_count"]:
        raise RuntimeError(f"Summary row mismatch: {len(rows)} != {summary['row_count']}")
    required = [
        "annotation_version",
        "image_id",
        "rule_id",
        "question",
        "annotator_id",
        "applies_to_image",
        "answer_label",
        "evidence_objects",
        "evidence_regions_xyxy",
        "ambiguous",
    ]
    for index, row in enumerate(rows, 1):
        missing = [field for field in required if not row.get(field)]
        if missing:
            raise RuntimeError(f"Row {index} missing required fields: {missing}")
        json.loads(row["evidence_regions_xyxy"])
    print(f"Validated {len(rows)} model-assisted annotation rows.")
    print(f"Answer counts: {summary['answer_counts']}")
    print(f"Ambiguous counts: {summary['ambiguous_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
