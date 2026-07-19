"""Validate the prioritized human-audit batch artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_COLUMNS = {
    "audit_id",
    "image_id",
    "rule_id",
    "question",
    "model_assisted_answer_label",
    "florence_predicted_answer",
    "priority_score",
    "priority_reason",
    "annotator_1_answer_label",
    "annotator_2_answer_label",
    "adjudicated_answer_label",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001.csv")
    parser.add_argument(
        "--jsonl", type=Path, default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001.jsonl"
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001_summary.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with args.csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        csv_rows = list(reader)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
    if missing:
        raise RuntimeError(f"Audit CSV missing columns: {sorted(missing)}")
    with args.jsonl.open("r", encoding="utf-8") as handle:
        jsonl_rows = [json.loads(line) for line in handle if line.strip()]
    if len(csv_rows) != len(jsonl_rows):
        raise RuntimeError(f"Audit JSONL/CSV row mismatch: {len(jsonl_rows)} != {len(csv_rows)}")
    with args.summary.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    if len(csv_rows) != summary["row_count"]:
        raise RuntimeError("Audit summary row count mismatch")
    audit_ids = [row["audit_id"] for row in csv_rows]
    if len(audit_ids) != len(set(audit_ids)):
        raise RuntimeError("Audit IDs must be unique")
    rule_counts: dict[str, int] = {}
    for row in csv_rows:
        if row["model_assisted_answer_label"] not in {"compliant", "violation", "uncertain"}:
            raise RuntimeError(f"Unexpected model-assisted label: {row['model_assisted_answer_label']}")
        if row["florence_predicted_answer"] not in {"compliant", "violation", "uncertain"}:
            raise RuntimeError(f"Unexpected Florence label: {row['florence_predicted_answer']}")
        if int(row["priority_score"]) < 0:
            raise RuntimeError(f"Negative priority score for {row['audit_id']}")
        rule_counts[row["rule_id"]] = rule_counts.get(row["rule_id"], 0) + 1
    if rule_counts != summary["rule_counts"]:
        raise RuntimeError(f"Audit rule-count mismatch: {rule_counts} != {summary['rule_counts']}")
    print(f"Validated {len(csv_rows)} human-audit rows from {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
