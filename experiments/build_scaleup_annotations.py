"""Build scale-up annotation templates and automated baseline annotations."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.annotation import ANNOTATION_VERSION, ANNOTATOR_ID, RULE_EVIDENCE_OBJECTS
from faithbench.schema import load_rules

ANNOTATION_FIELDS = [
    "annotation_version",
    "image_id",
    "rule_id",
    "question",
    "expected_answer_seed",
    "annotator_id",
    "applies_to_image",
    "answer_label",
    "evidence_objects",
    "evidence_regions_xyxy",
    "ambiguous",
    "image_quality_issue",
    "multi_worker_ambiguity",
    "model_evidence_acceptable",
    "free_text_notes",
]


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ANNOTATION_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")


def template_row(row: dict[str, str], question: str) -> dict[str, str]:
    return {
        "annotation_version": "0.2.0",
        "image_id": row["image_id"],
        "rule_id": row["rule_id"],
        "question": question,
        "expected_answer_seed": row["expected_answer_seed"],
        "annotator_id": "",
        "applies_to_image": "",
        "answer_label": "",
        "evidence_objects": "",
        "evidence_regions_xyxy": "",
        "ambiguous": "",
        "image_quality_issue": "",
        "multi_worker_ambiguity": "",
        "model_evidence_acceptable": "",
        "free_text_notes": "",
    }


def bootstrap_row(row: dict[str, str], question: str) -> dict[str, str]:
    notes = ["scale-up automated baseline annotation, not human ground truth"]
    if row["source_violation_reason"]:
        notes.append(f"source_reason={row['source_violation_reason']}")
    if row["notes"]:
        notes.append(f"manifest_notes={row['notes']}")
    image_quality_issue = "yes" if "poor" in row["quality_of_info"].lower() else "no"
    ambiguous = "yes" if image_quality_issue == "yes" or "metadata_unconfirmed" in row["notes"] else "no"
    caption_lower = row["image_caption"].lower()
    multi_worker = "yes" if "workers" in caption_lower or "two worker" in caption_lower else "no"
    return {
        "annotation_version": ANNOTATION_VERSION,
        "image_id": row["image_id"],
        "rule_id": row["rule_id"],
        "question": question,
        "expected_answer_seed": row["expected_answer_seed"],
        "annotator_id": ANNOTATOR_ID,
        "applies_to_image": "yes" if row["expected_answer_seed"] == "violation" else "uncertain",
        "answer_label": row["expected_answer_seed"],
        "evidence_objects": ",".join(RULE_EVIDENCE_OBJECTS[row["rule_id"]]),
        "evidence_regions_xyxy": row["source_violation_boxes_xyxy"],
        "ambiguous": ambiguous,
        "image_quality_issue": image_quality_issue,
        "multi_worker_ambiguity": multi_worker,
        "model_evidence_acceptable": "not_shown",
        "free_text_notes": "; ".join(notes),
    }


def main() -> int:
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    rules_by_id = {rule.rule_id: rule for rule in rules.rules}
    manifest_rows = read_manifest(ROOT / "benchmark" / "splits" / "scaleup_candidate_manifest.csv")
    template_rows = [template_row(row, rules_by_id[row["rule_id"]].question) for row in manifest_rows]
    bootstrap_rows = [bootstrap_row(row, rules_by_id[row["rule_id"]].question) for row in manifest_rows]
    write_csv(ROOT / "benchmark" / "annotations" / "scaleup_annotation_template.csv", template_rows)
    write_jsonl(ROOT / "benchmark" / "annotations" / "scaleup_annotation_template.jsonl", template_rows)
    write_csv(ROOT / "benchmark" / "annotations" / "scaleup_model_assisted_annotations.csv", bootstrap_rows)
    write_jsonl(ROOT / "benchmark" / "annotations" / "scaleup_model_assisted_annotations.jsonl", bootstrap_rows)

    summary = {
        "annotation_version": ANNOTATION_VERSION,
        "annotator_id": ANNOTATOR_ID,
        "row_count": len(bootstrap_rows),
        "provenance": "Generated from scale-up candidate manifest metadata. This is not human/domain-expert ground truth.",
        "answer_counts": {},
        "ambiguous_counts": {},
    }
    for row in bootstrap_rows:
        summary["answer_counts"][row["answer_label"]] = summary["answer_counts"].get(row["answer_label"], 0) + 1
        summary["ambiguous_counts"][row["ambiguous"]] = summary["ambiguous_counts"].get(row["ambiguous"], 0) + 1
    with (ROOT / "benchmark" / "annotations" / "scaleup_model_assisted_annotation_summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    print(f"Wrote {len(bootstrap_rows)} scale-up annotation rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
