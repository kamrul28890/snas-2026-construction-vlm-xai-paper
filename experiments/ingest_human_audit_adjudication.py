"""Ingest returned adjudication decisions for human_audit_batch_001."""

from __future__ import annotations

import argparse
import csv
import hashlib
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
        default=Path(
            r"D:\My Projects\human-audit-batch-001-annotation\adjudication"
            r"\human_audit_batch_001_adjudication_package"
        ),
        help="Returned adjudication package containing adjudication_form.csv.",
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
        "--disagreements",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001_ai_disagreements.csv",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001_summary.json",
    )
    return parser.parse_args()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized(value: str) -> str:
    return value.strip().lower()


def ensure_field(fieldnames: list[str], field: str, before: str | None = None) -> list[str]:
    if field in fieldnames:
        return fieldnames
    output = list(fieldnames)
    if before and before in output:
        output.insert(output.index(before), field)
    else:
        output.append(field)
    return output


def validate_rows(
    *,
    adjudication_rows: list[dict[str, str]],
    batch_rows: list[dict[str, str]],
    disagreement_rows: list[dict[str, str]],
) -> None:
    if len(adjudication_rows) != len(disagreement_rows):
        raise RuntimeError(f"Adjudication row count mismatch: {len(adjudication_rows)} != {len(disagreement_rows)}")
    batch_by_id = {row["audit_id"]: row for row in batch_rows}
    disagreement_ids = [row["audit_id"] for row in disagreement_rows]
    adjudication_ids = [row["audit_id"] for row in adjudication_rows]
    if adjudication_ids != disagreement_ids:
        raise RuntimeError("Adjudication rows must match disagreement rows in order and identity")
    for index, row in enumerate(adjudication_rows, start=2):
        batch_row = batch_by_id.get(row["audit_id"])
        if not batch_row:
            raise RuntimeError(f"Row {index} audit_id not found in batch: {row['audit_id']}")
        for column in [
            "image_id",
            "rule_id",
            "question",
            "image_width",
            "image_height",
            "annotator_1_answer_label",
            "annotator_2_answer_label",
        ]:
            if str(batch_row[column]) != str(row.get(column, "")):
                raise RuntimeError(
                    f"Row {index} {column} mismatch: {batch_row[column]!r} != {row.get(column)!r}"
                )
        label = normalized(row["adjudicated_answer_label"])
        ambiguous = normalized(row["adjudicated_ambiguous"])
        if label not in VALID_LABELS:
            raise RuntimeError(f"Row {index} invalid adjudicated_answer_label: {label!r}")
        if ambiguous not in VALID_AMBIGUOUS:
            raise RuntimeError(f"Row {index} invalid adjudicated_ambiguous: {ambiguous!r}")
        boxes = json.loads(row["adjudicated_evidence_regions_xyxy"])
        if not isinstance(boxes, list):
            raise RuntimeError(f"Row {index} adjudicated_evidence_regions_xyxy must be a JSON list")
        width = int(row["image_width"])
        height = int(row["image_height"])
        for box in boxes:
            if not (isinstance(box, list) and len(box) == 4 and all(isinstance(value, (int, float)) for value in box)):
                raise RuntimeError(f"Row {index} malformed box: {box!r}")
            x_min, y_min, x_max, y_max = box
            if not (x_max > x_min and y_max > y_min):
                raise RuntimeError(f"Row {index} non-positive box: {box!r}")
            if min(x_min, y_min) < 0 or x_max > width or y_max > height:
                raise RuntimeError(f"Row {index} box out of image bounds: {box!r}")


def merge_adjudication(
    *,
    batch_rows: list[dict[str, str]],
    jsonl_rows: list[dict[str, str]],
    adjudication_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    adjudication_by_id = {row["audit_id"]: row for row in adjudication_rows}
    merged_csv: list[dict[str, str]] = []
    merged_jsonl: list[dict[str, str]] = []
    for batch_row, jsonl_row in zip(batch_rows, jsonl_rows):
        row_update = {}
        adjudicated = adjudication_by_id.get(batch_row["audit_id"])
        if adjudicated:
            row_update = {
                "adjudicated_answer_label": normalized(adjudicated["adjudicated_answer_label"]),
                "adjudicated_evidence_regions_xyxy": adjudicated["adjudicated_evidence_regions_xyxy"].strip(),
                "adjudicated_ambiguous": normalized(adjudicated["adjudicated_ambiguous"]),
                "adjudication_notes": adjudicated["adjudication_notes"].strip(),
            }
        elif "adjudicated_ambiguous" not in batch_row:
            row_update = {"adjudicated_ambiguous": ""}
        merged_csv.append({**batch_row, **row_update})
        merged_jsonl.append({**jsonl_row, **row_update})
    return merged_csv, merged_jsonl


def build_adjudication_archive_rows(adjudication_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "audit_id": row["audit_id"],
            "image_id": row["image_id"],
            "rule_id": row["rule_id"],
            "adjudicated_answer_label": normalized(row["adjudicated_answer_label"]),
            "adjudicated_evidence_regions_xyxy": row["adjudicated_evidence_regions_xyxy"].strip(),
            "adjudicated_ambiguous": normalized(row["adjudicated_ambiguous"]),
            "adjudication_notes": row["adjudication_notes"].strip(),
        }
        for row in adjudication_rows
    ]


def build_final_label_rows(batch_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    final_rows = []
    for row in batch_rows:
        adjudicated_label = normalized(row.get("adjudicated_answer_label", ""))
        if adjudicated_label in VALID_LABELS:
            final_label = adjudicated_label
            final_evidence = row["adjudicated_evidence_regions_xyxy"]
            final_ambiguous = normalized(row.get("adjudicated_ambiguous", ""))
            final_source = "returned_adjudication"
            final_evidence_source = "returned_adjudication"
            final_notes = row["adjudication_notes"]
        elif normalized(row["annotator_1_answer_label"]) == normalized(row["annotator_2_answer_label"]):
            final_label = normalized(row["annotator_1_answer_label"])
            final_evidence = row["annotator_1_evidence_regions_xyxy"]
            final_ambiguous = (
                "yes"
                if "yes" in {normalized(row["annotator_1_ambiguous"]), normalized(row["annotator_2_ambiguous"])}
                else "no"
            )
            final_source = "dual_annotator_agreement"
            final_evidence_source = "annotator_1_boxes_by_convention"
            final_notes = (
                "A/B answer labels agree; conservative ambiguity flag uses either annotator's ambiguity judgment."
            )
        else:
            final_label = ""
            final_evidence = ""
            final_ambiguous = ""
            final_source = "unresolved"
            final_evidence_source = ""
            final_notes = "A/B disagreement remains unresolved."
        final_rows.append(
            {
                "audit_id": row["audit_id"],
                "image_id": row["image_id"],
                "rule_id": row["rule_id"],
                "question": row["question"],
                "final_answer_label": final_label,
                "final_evidence_regions_xyxy": final_evidence,
                "final_ambiguous": final_ambiguous,
                "final_label_source": final_source,
                "final_evidence_source": final_evidence_source,
                "annotator_1_answer_label": row["annotator_1_answer_label"],
                "annotator_2_answer_label": row["annotator_2_answer_label"],
                "adjudicated_answer_label": row.get("adjudicated_answer_label", ""),
                "final_notes": final_notes,
            }
        )
    return final_rows


def update_disagreements(
    *,
    disagreement_rows: list[dict[str, str]],
    adjudication_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[str]]:
    adjudication_by_id = {row["audit_id"]: row for row in adjudication_rows}
    fieldnames = list(disagreement_rows[0].keys())
    for field in [
        "adjudicated_answer_label",
        "adjudicated_evidence_regions_xyxy",
        "adjudicated_ambiguous",
        "adjudication_notes",
    ]:
        fieldnames = ensure_field(fieldnames, field)
    updated = []
    for row in disagreement_rows:
        adjudicated = adjudication_by_id[row["audit_id"]]
        updated.append(
            {
                **row,
                "adjudication_status": "adjudicated",
                "adjudicated_answer_label": normalized(adjudicated["adjudicated_answer_label"]),
                "adjudicated_evidence_regions_xyxy": adjudicated["adjudicated_evidence_regions_xyxy"].strip(),
                "adjudicated_ambiguous": normalized(adjudicated["adjudicated_ambiguous"]),
                "adjudication_notes": adjudicated["adjudication_notes"].strip(),
            }
        )
    return updated, fieldnames


def write_final_summary(rows: list[dict[str, str]], path: Path) -> None:
    label_counts = Counter(row["final_answer_label"] for row in rows)
    source_counts = Counter(row["final_label_source"] for row in rows)
    ambiguous_counts = Counter(row["final_ambiguous"] for row in rows)
    summary = {
        "batch_id": "human_audit_batch_001",
        "row_count": len(rows),
        "final_label_completion_count": sum(1 for row in rows if row["final_answer_label"] in VALID_LABELS),
        "final_label_completion_rate": sum(1 for row in rows if row["final_answer_label"] in VALID_LABELS) / len(rows),
        "final_answer_counts": dict(sorted(label_counts.items())),
        "final_ambiguous_counts": dict(sorted(ambiguous_counts.items())),
        "final_label_source_counts": dict(sorted(source_counts.items())),
        "provenance": (
            "Final audit labels combine two AI-generated annotation passes. "
            "Rows with A/B agreement use the agreed answer label; rows with A/B disagreement use the returned adjudication package."
        ),
    }
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def update_batch_summary(
    *,
    summary_path: Path,
    adjudication_rows: list[dict[str, str]],
    final_rows: list[dict[str, str]],
    package_dir: Path,
) -> None:
    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    summary["adjudication"] = {
        "status": "ingested",
        "source_package": str(package_dir),
        "adjudication_form_sha256": sha256_file(package_dir / "adjudication_form.csv"),
        "disagreement_rows_adjudicated": len(adjudication_rows),
        "adjudicated_answer_counts": dict(
            sorted(Counter(normalized(row["adjudicated_answer_label"]) for row in adjudication_rows).items())
        ),
        "adjudicated_ambiguous_counts": dict(
            sorted(Counter(normalized(row["adjudicated_ambiguous"]) for row in adjudication_rows).items())
        ),
    }
    summary["final_label_layer"] = {
        "status": "available",
        "row_count": len(final_rows),
        "final_label_completion_count": sum(1 for row in final_rows if row["final_answer_label"] in VALID_LABELS),
        "final_label_source_counts": dict(sorted(Counter(row["final_label_source"] for row in final_rows).items())),
        "ground_truth_status": "adjudicated_audit_labels_with_ai_pass_provenance",
    }
    summary["provenance"] = (
        "Prioritized for independent audit from scale-up Florence score diagnostics. "
        "Two AI-generated annotator passes are ingested; A/B disagreements are resolved by the returned adjudication package. "
        "Use the final-label layer with this provenance, not as unqualified human ground truth."
    )
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")


def copy_returned_docs(package_dir: Path, out_dir: Path) -> None:
    mappings = {
        "README_START_HERE.md": "human_audit_batch_001_returned_adjudication_README.md",
        "package_manifest.json": "human_audit_batch_001_returned_adjudication_manifest.json",
    }
    for source_name, target_name in mappings.items():
        source = package_dir / source_name
        if source.exists():
            shutil.copyfile(source, out_dir / target_name)


def main() -> int:
    args = parse_args()
    out_dir = ROOT / "benchmark" / "annotations"
    adjudication_rows, adjudication_fields = read_csv(args.package / "adjudication_form.csv")
    batch_rows, batch_fields = read_csv(args.batch_csv)
    jsonl_rows = read_jsonl(args.batch_jsonl)
    disagreement_rows, disagreement_fields = read_csv(args.disagreements)
    validate_rows(adjudication_rows=adjudication_rows, batch_rows=batch_rows, disagreement_rows=disagreement_rows)

    batch_fields = ensure_field(batch_fields, "adjudicated_ambiguous", before="adjudication_notes")
    merged_csv, merged_jsonl = merge_adjudication(
        batch_rows=batch_rows,
        jsonl_rows=jsonl_rows,
        adjudication_rows=adjudication_rows,
    )
    write_csv(merged_csv, args.batch_csv, batch_fields)
    write_jsonl(merged_jsonl, args.batch_jsonl)

    archive_rows = build_adjudication_archive_rows(adjudication_rows)
    write_csv(
        archive_rows,
        out_dir / "human_audit_batch_001_adjudication.csv",
        list(archive_rows[0].keys()),
    )
    write_jsonl(archive_rows, out_dir / "human_audit_batch_001_adjudication.jsonl")

    updated_disagreements, disagreement_fields = update_disagreements(
        disagreement_rows=disagreement_rows,
        adjudication_rows=adjudication_rows,
    )
    write_csv(updated_disagreements, args.disagreements, disagreement_fields)

    final_rows = build_final_label_rows(merged_csv)
    final_fields = list(final_rows[0].keys())
    write_csv(final_rows, out_dir / "human_audit_batch_001_final_labels.csv", final_fields)
    write_jsonl(final_rows, out_dir / "human_audit_batch_001_final_labels.jsonl")
    write_final_summary(final_rows, out_dir / "human_audit_batch_001_final_labels_summary.json")
    update_batch_summary(
        summary_path=args.summary,
        adjudication_rows=adjudication_rows,
        final_rows=final_rows,
        package_dir=args.package,
    )
    copy_returned_docs(args.package, out_dir)
    print(f"Ingested {len(adjudication_rows)} adjudicated disagreements and wrote {len(final_rows)} final labels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
