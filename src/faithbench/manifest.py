"""Manifest builders for converting pilot artifacts into benchmark records."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from faithbench.schema import BenchmarkRules

SOURCE_DATASET_ID = "LouisChen15/ConstructionSite"
SOURCE_DATASET_REVISION = "ca3d9b885b45cbec956817edc42253664c7faf3f"
SOURCE_SPLIT = "test"

LEGACY_RULE_MAP = {
    "rule_1": "ppe_hard_hat",
    "rule_2": "fall_harness",
    "rule_3": "guardrail_edge",
    "rule_4": "struck_by_equipment",
}

PRIMARY_CLASS_EXPECTED_ANSWER = {
    "compliant": "compliant",
    "ppe_violation": "violation",
    "fall_hazard": "violation",
    "struck_by_risk": "violation",
}


@dataclass(frozen=True)
class ManifestBuildResult:
    """Paths and counts produced by a manifest build."""

    manifest_path: Path
    annotation_jsonl_path: Path
    annotation_csv_path: Path
    summary_path: Path
    row_count: int
    annotation_count: int


def evidence_size_band(area_fraction: str | float | None) -> str:
    """Assign a fixed evidence-size band from image-area fraction."""
    if area_fraction in {None, ""}:
        return "missing"
    area = float(area_fraction)
    if area < 0.001:
        return "tiny"
    if area < 0.01:
        return "small"
    if area < 0.1:
        return "medium"
    return "large"


def audit_priority(primary_class: str, has_worker_box: bool, has_object_box: bool, size_band: str) -> str:
    """Prioritize examples for human/domain annotation."""
    if not has_worker_box or not has_object_box:
        return "missing_evidence"
    if primary_class == "struck_by_risk":
        return "underpowered_class"
    if size_band in {"tiny", "large"}:
        return "metric_validity_edge_case"
    return "standard"


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_dataset_status(summary_path: Path) -> dict[str, str]:
    """Map legacy primary classes to stability/exploratory status."""
    with summary_path.open("r", encoding="utf-8", newline="") as handle:
        return {row["primary_class"]: row["status"] for row in csv.DictReader(handle)}


def build_pilot_manifest(
    *,
    sample_audit_path: Path,
    dataset_summary_path: Path,
    rules: BenchmarkRules,
    manifest_path: Path,
    annotation_jsonl_path: Path,
    annotation_csv_path: Path,
    summary_path: Path,
) -> ManifestBuildResult:
    """Build benchmark pilot manifest and annotation templates from audit CSVs."""
    status_by_class = read_dataset_status(dataset_summary_path)
    rule_by_id = {rule.rule_id: rule for rule in rules.rules}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    annotation_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    annotation_csv_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_fields = [
        "benchmark_version",
        "image_id",
        "source_dataset_id",
        "source_dataset_revision",
        "source_split",
        "legacy_primary_class",
        "legacy_rule_id",
        "rule_id",
        "rule_family",
        "expected_answer_seed",
        "image_width",
        "image_height",
        "has_worker_box",
        "has_object_box",
        "target_box_xyxy",
        "target_area_fraction",
        "evidence_size_band",
        "subgroup_status",
        "annotation_priority",
        "needs_human_label",
        "notes",
    ]
    annotation_fields = [
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

    manifest_rows: list[dict[str, str]] = []
    annotation_rows: list[dict[str, str]] = []
    class_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}

    with sample_audit_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            legacy_rule_id = row["assigned_rule_id"]
            rule_id = LEGACY_RULE_MAP[legacy_rule_id]
            rule = rule_by_id[rule_id]
            primary_class = row["primary_class"]
            has_worker_box = parse_bool(row["has_worker_box"])
            has_object_box = parse_bool(row["has_object_box"])
            size_band = evidence_size_band(row["target_area_fraction"])
            priority = audit_priority(primary_class, has_worker_box, has_object_box, size_band)
            expected_answer = PRIMARY_CLASS_EXPECTED_ANSWER[primary_class]
            class_counts[primary_class] = class_counts.get(primary_class, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            notes = []
            if status_by_class.get(primary_class) == "Exploratory":
                notes.append("exploratory_subgroup")
            if not has_worker_box:
                notes.append("missing_worker_box")
            if not has_object_box:
                notes.append("missing_object_box")
            manifest_rows.append(
                {
                    "benchmark_version": "0.1.0-pilot",
                    "image_id": row["image_id"],
                    "source_dataset_id": SOURCE_DATASET_ID,
                    "source_dataset_revision": SOURCE_DATASET_REVISION,
                    "source_split": SOURCE_SPLIT,
                    "legacy_primary_class": primary_class,
                    "legacy_rule_id": legacy_rule_id,
                    "rule_id": rule_id,
                    "rule_family": rule.rule_family,
                    "expected_answer_seed": expected_answer,
                    "image_width": row["image_width"],
                    "image_height": row["image_height"],
                    "has_worker_box": str(has_worker_box).lower(),
                    "has_object_box": str(has_object_box).lower(),
                    "target_box_xyxy": row["target_box"],
                    "target_area_fraction": row["target_area_fraction"],
                    "evidence_size_band": size_band,
                    "subgroup_status": status_by_class.get(primary_class, "Unknown"),
                    "annotation_priority": priority,
                    "needs_human_label": "true",
                    "notes": ";".join(notes),
                }
            )
            annotation_rows.append(
                {
                    "annotation_version": "0.1.0",
                    "image_id": row["image_id"],
                    "rule_id": rule_id,
                    "question": rule.question,
                    "expected_answer_seed": expected_answer,
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
            )

    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(manifest_rows)

    with annotation_jsonl_path.open("w", encoding="utf-8", newline="") as handle:
        for row in annotation_rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")

    with annotation_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=annotation_fields)
        writer.writeheader()
        writer.writerows(annotation_rows)

    summary = {
        "benchmark_version": "0.1.0-pilot",
        "source_sample_audit": str(sample_audit_path),
        "source_dataset_summary": str(dataset_summary_path),
        "row_count": len(manifest_rows),
        "annotation_template_count": len(annotation_rows),
        "class_counts": class_counts,
        "priority_counts": priority_counts,
        "legacy_rule_map": LEGACY_RULE_MAP,
    }
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")

    return ManifestBuildResult(
        manifest_path=manifest_path,
        annotation_jsonl_path=annotation_jsonl_path,
        annotation_csv_path=annotation_csv_path,
        summary_path=summary_path,
        row_count=len(manifest_rows),
        annotation_count=len(annotation_rows),
    )

