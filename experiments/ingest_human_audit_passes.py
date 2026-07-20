"""Ingest independent annotation passes for the first human-audit batch.

The returned package used here may contain AI-generated annotator personas.
This script preserves that provenance explicitly and does not adjudicate
disagreements into human ground truth.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VALID_LABELS = {"compliant", "violation", "uncertain"}
VALID_AMBIGUOUS = {"yes", "no"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package",
        type=Path,
        default=Path(r"D:\My Projects\human-audit-batch-001-annotation\final_package"),
        help="Returned annotation package containing annotator_A_pass.csv and annotator_B_pass.csv.",
    )
    parser.add_argument(
        "--batch-csv",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001.csv",
    )
    parser.add_argument(
        "--batch-jsonl",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001.jsonl",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001_summary.json",
    )
    parser.add_argument("--annotator-1-id", default="ai_annotator_A_compliance_officer")
    parser.add_argument("--annotator-2-id", default="ai_annotator_B_site_superintendent")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_csv(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")


def validate_pass(
    *,
    name: str,
    rows: list[dict[str, str]],
    batch_rows: list[dict[str, str]],
) -> None:
    if len(rows) != len(batch_rows):
        raise RuntimeError(f"{name} row count mismatch: {len(rows)} != {len(batch_rows)}")
    for index, (batch_row, row) in enumerate(zip(batch_rows, rows), start=2):
        for column in ["audit_id", "image_id", "rule_id", "question", "image_width", "image_height"]:
            if str(batch_row[column]) != str(row.get(column, "")):
                raise RuntimeError(
                    f"{name} row {index} {column} mismatch: {batch_row[column]!r} != {row.get(column)!r}"
                )
        label = row["answer_label"].strip().lower()
        ambiguous = row["ambiguous"].strip().lower()
        if label not in VALID_LABELS:
            raise RuntimeError(f"{name} row {index} invalid answer_label: {label!r}")
        if ambiguous not in VALID_AMBIGUOUS:
            raise RuntimeError(f"{name} row {index} invalid ambiguous: {ambiguous!r}")
        boxes = json.loads(row["evidence_regions_xyxy"])
        if not isinstance(boxes, list):
            raise RuntimeError(f"{name} row {index} evidence_regions_xyxy must be a JSON list")
        width = int(row["image_width"])
        height = int(row["image_height"])
        for box in boxes:
            if not (isinstance(box, list) and len(box) == 4 and all(isinstance(value, (int, float)) for value in box)):
                raise RuntimeError(f"{name} row {index} malformed box: {box!r}")
            x_min, y_min, x_max, y_max = box
            if not (x_max > x_min and y_max > y_min):
                raise RuntimeError(f"{name} row {index} non-positive box: {box!r}")
            if min(x_min, y_min) < 0 or x_max > width or y_max > height:
                raise RuntimeError(f"{name} row {index} box out of image bounds: {box!r}")


def compact_pass_rows(rows: list[dict[str, str]], annotator_id: str) -> list[dict[str, str]]:
    return [
        {
            "annotator_id": annotator_id,
            "audit_id": row["audit_id"],
            "image_id": row["image_id"],
            "rule_id": row["rule_id"],
            "answer_label": row["answer_label"].strip().lower(),
            "evidence_regions_xyxy": row["evidence_regions_xyxy"].strip(),
            "ambiguous": row["ambiguous"].strip().lower(),
            "notes": row["notes"].strip(),
        }
        for row in rows
    ]


def merge_passes(
    *,
    batch_rows: list[dict[str, str]],
    jsonl_rows: list[dict[str, str]],
    annotator_1_rows: list[dict[str, str]],
    annotator_2_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    merged_csv: list[dict[str, str]] = []
    merged_jsonl: list[dict[str, str]] = []
    for batch_row, jsonl_row, row_1, row_2 in zip(batch_rows, jsonl_rows, annotator_1_rows, annotator_2_rows):
        updates = {
            "annotator_1_answer_label": row_1["answer_label"].strip().lower(),
            "annotator_1_evidence_regions_xyxy": row_1["evidence_regions_xyxy"].strip(),
            "annotator_1_ambiguous": row_1["ambiguous"].strip().lower(),
            "annotator_1_notes": row_1["notes"].strip(),
            "annotator_2_answer_label": row_2["answer_label"].strip().lower(),
            "annotator_2_evidence_regions_xyxy": row_2["evidence_regions_xyxy"].strip(),
            "annotator_2_ambiguous": row_2["ambiguous"].strip().lower(),
            "annotator_2_notes": row_2["notes"].strip(),
        }
        merged_csv.append({**batch_row, **updates})
        merged_jsonl.append({**jsonl_row, **updates})
    return merged_csv, merged_jsonl


def disagreement_rows(
    *,
    annotator_1_rows: list[dict[str, str]],
    annotator_2_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row_1, row_2 in zip(annotator_1_rows, annotator_2_rows):
        if row_1["answer_label"].strip().lower() == row_2["answer_label"].strip().lower():
            continue
        rows.append(
            {
                "audit_id": row_1["audit_id"],
                "image_id": row_1["image_id"],
                "rule_id": row_1["rule_id"],
                "annotator_1_answer_label": row_1["answer_label"].strip().lower(),
                "annotator_1_ambiguous": row_1["ambiguous"].strip().lower(),
                "annotator_1_notes": row_1["notes"].strip(),
                "annotator_2_answer_label": row_2["answer_label"].strip().lower(),
                "annotator_2_ambiguous": row_2["ambiguous"].strip().lower(),
                "annotator_2_notes": row_2["notes"].strip(),
                "adjudication_status": "needs_review",
            }
        )
    return rows


def write_agreement_table(rows: list[dict[str, str]], path: Path) -> None:
    label_pairs = Counter((row["annotator_1_answer_label"], row["annotator_2_answer_label"]) for row in rows)
    rule_counts: Counter[str] = Counter()
    rule_agree: Counter[str] = Counter()
    for row in rows:
        rule = row["rule_id"]
        rule_counts[rule] += 1
        if row["annotator_1_answer_label"] == row["annotator_2_answer_label"]:
            rule_agree[rule] += 1
    out_rows = [
        {
            "metric_id": "overall_answer_agreement",
            "value": f"{sum(1 for row in rows if row['annotator_1_answer_label'] == row['annotator_2_answer_label']) / len(rows):.6f}",
            "n": str(len(rows)),
            "notes": "Exact answer-label agreement between the two independent AI-generated audit passes.",
        }
    ]
    for rule in sorted(rule_counts):
        out_rows.append(
            {
                "metric_id": f"{rule}_answer_agreement",
                "value": f"{rule_agree[rule] / rule_counts[rule]:.6f}",
                "n": str(rule_counts[rule]),
                "notes": f"Exact answer-label agreement for {rule}.",
            }
        )
    for (label_1, label_2), count in sorted(label_pairs.items()):
        out_rows.append(
            {
                "metric_id": f"label_pair_{label_1}_vs_{label_2}",
                "value": str(count),
                "n": str(len(rows)),
                "notes": "Count of answer-label pairings across annotator 1 and annotator 2.",
            }
        )
    write_csv(out_rows, path, ["metric_id", "value", "n", "notes"])


def update_summary(
    *,
    path: Path,
    merged_rows: list[dict[str, str]],
    disagreements: list[dict[str, str]],
    args: argparse.Namespace,
) -> None:
    with path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    summary["annotation_passes"] = {
        "status": "ingested",
        "ground_truth_status": "not_human_ground_truth",
        "provenance": "Two independent AI-generated passes from the returned final_package. Both are useful for pipeline/adjudication analysis but require human/domain adjudication before ground-truth claims.",
        "source_package": str(args.package),
        "annotator_1_id": args.annotator_1_id,
        "annotator_2_id": args.annotator_2_id,
        "annotator_1_completion_count": len(merged_rows),
        "annotator_2_completion_count": len(merged_rows),
        "answer_agreement_count": len(merged_rows) - len(disagreements),
        "answer_disagreement_count": len(disagreements),
        "answer_agreement_rate": (len(merged_rows) - len(disagreements)) / len(merged_rows),
        "disagreement_rule_counts": dict(sorted(Counter(row["rule_id"] for row in disagreements).items())),
    }
    summary["provenance"] = (
        "Prioritized for independent audit from scale-up Florence score diagnostics. "
        "Annotator fields are currently populated by two independent AI-generated passes and must not be described as human ground truth."
    )
    with path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")


def copy_optional_docs(package_dir: Path, out_dir: Path) -> None:
    mappings = {
        "README.md": "human_audit_batch_001_ai_returned_package_README.md",
        "PERSONAS.md": "human_audit_batch_001_ai_personas.md",
        "DISAGREEMENT_ANALYSIS.md": "human_audit_batch_001_ai_disagreement_analysis.md",
    }
    for source_name, target_name in mappings.items():
        source = package_dir / source_name
        if source.exists():
            shutil.copyfile(source, out_dir / target_name)


def main() -> int:
    args = parse_args()
    out_dir = ROOT / "benchmark" / "annotations"
    annotator_1_raw = read_csv(args.package / "annotator_A_pass.csv")
    annotator_2_raw = read_csv(args.package / "annotator_B_pass.csv")
    batch_rows = read_csv(args.batch_csv)
    jsonl_rows = read_jsonl(args.batch_jsonl)
    validate_pass(name="annotator_A_pass.csv", rows=annotator_1_raw, batch_rows=batch_rows)
    validate_pass(name="annotator_B_pass.csv", rows=annotator_2_raw, batch_rows=batch_rows)

    annotator_1_rows = compact_pass_rows(annotator_1_raw, args.annotator_1_id)
    annotator_2_rows = compact_pass_rows(annotator_2_raw, args.annotator_2_id)
    merged_csv, merged_jsonl = merge_passes(
        batch_rows=batch_rows,
        jsonl_rows=jsonl_rows,
        annotator_1_rows=annotator_1_raw,
        annotator_2_rows=annotator_2_raw,
    )
    disagreements = disagreement_rows(annotator_1_rows=annotator_1_raw, annotator_2_rows=annotator_2_raw)

    write_csv(merged_csv, args.batch_csv, list(batch_rows[0].keys()))
    write_jsonl(merged_jsonl, args.batch_jsonl)
    write_csv(
        annotator_1_rows,
        out_dir / "human_audit_batch_001_annotator_A_ai.csv",
        list(annotator_1_rows[0].keys()),
    )
    write_csv(
        annotator_2_rows,
        out_dir / "human_audit_batch_001_annotator_B_ai.csv",
        list(annotator_2_rows[0].keys()),
    )
    write_csv(
        disagreements,
        out_dir / "human_audit_batch_001_ai_disagreements.csv",
        [
            "audit_id",
            "image_id",
            "rule_id",
            "annotator_1_answer_label",
            "annotator_1_ambiguous",
            "annotator_1_notes",
            "annotator_2_answer_label",
            "annotator_2_ambiguous",
            "annotator_2_notes",
            "adjudication_status",
        ],
    )
    write_agreement_table(merged_csv, ROOT / "results" / "tables" / "human_audit_batch_001_ai_agreement.csv")
    update_summary(path=args.summary, merged_rows=merged_csv, disagreements=disagreements, args=args)
    copy_optional_docs(args.package, out_dir)

    print(
        "Ingested two annotation passes: "
        f"{len(merged_csv)} rows, {len(merged_csv) - len(disagreements)} agreements, "
        f"{len(disagreements)} disagreements."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
