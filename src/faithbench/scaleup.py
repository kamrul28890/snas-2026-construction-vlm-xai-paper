"""Build larger candidate manifests from ConstructionSite metadata."""

from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from faithbench.annotation import normalized_box_to_abs
from faithbench.manifest import SOURCE_DATASET_ID, SOURCE_DATASET_REVISION, SOURCE_SPLIT
from faithbench.schema import BenchmarkRules

RULE_FIELDS = ["rule_1_violation", "rule_2_violation", "rule_3_violation", "rule_4_violation"]
RULE_FIELD_TO_ID = {
    "rule_1_violation": "ppe_hard_hat",
    "rule_2_violation": "fall_harness",
    "rule_3_violation": "guardrail_edge",
    "rule_4_violation": "struck_by_equipment",
}
RULE_TO_CLASS = {
    "rule_1_violation": "ppe_violation",
    "rule_2_violation": "fall_hazard",
    "rule_3_violation": "fall_hazard",
    "rule_4_violation": "struck_by_risk",
}
CLASS_PRIORITY = ["ppe_violation", "fall_hazard", "struck_by_risk", "compliant"]
COMPLIANT_NON_EQUIPMENT_RULES = ["ppe_hard_hat", "fall_harness", "guardrail_edge"]


@dataclass(frozen=True)
class ScaleupBuildResult:
    manifest_path: Path
    summary_path: Path
    row_count: int


def classify_source_row(row: dict[str, Any]) -> tuple[str, list[str]]:
    """Return primary class and violated source rule fields."""
    violated = [field for field in RULE_FIELDS if row.get(field) is not None]
    if not violated:
        return "compliant", []
    classes = {RULE_TO_CLASS[field] for field in violated}
    for candidate in CLASS_PRIORITY:
        if candidate in classes:
            return candidate, violated
    return "compliant", []


def choose_rule_for_row(
    *,
    primary_class: str,
    violated_fields: list[str],
    compliant_index: int,
    has_excavator: bool,
) -> tuple[str, str]:
    """Choose one normalized benchmark rule and return a provenance note."""
    if primary_class != "compliant":
        for field in RULE_FIELDS:
            if field in violated_fields and RULE_TO_CLASS[field] == primary_class:
                return RULE_FIELD_TO_ID[field], ""
        raise ValueError(f"No violated field matches class {primary_class}")
    if has_excavator:
        return "struck_by_equipment", "compliant_equipment_context"
    return (
        COMPLIANT_NON_EQUIPMENT_RULES[compliant_index % len(COMPLIANT_NON_EQUIPMENT_RULES)],
        "compliant_context_metadata_unconfirmed",
    )


def source_violation_reason_and_boxes(
    row: dict[str, Any],
    rule_id: str,
    *,
    width: int,
    height: int,
) -> tuple[str, list[list[int]]]:
    """Extract source violation reason and absolute boxes for the selected rule."""
    source_field = next(field for field, mapped in RULE_FIELD_TO_ID.items() if mapped == rule_id)
    violation = row.get(source_field)
    if not violation:
        return "", []
    boxes = violation.get("bounding_box") or []
    abs_boxes = [normalized_box_to_abs([float(v) for v in box], width, height) for box in boxes]
    return str(violation.get("reason") or ""), abs_boxes


def row_to_scaleup_record(
    row: dict[str, Any],
    *,
    rules: BenchmarkRules,
    compliant_index: int,
) -> dict[str, str]:
    """Convert one dataset row to a candidate benchmark manifest row."""
    primary_class, violated_fields = classify_source_row(row)
    image = row["image"]
    width, height = image.size
    has_excavator = bool(row.get("excavator"))
    rule_id, rule_note = choose_rule_for_row(
        primary_class=primary_class,
        violated_fields=violated_fields,
        compliant_index=compliant_index,
        has_excavator=has_excavator,
    )
    rule = rules.by_id(rule_id)
    reason, boxes = source_violation_reason_and_boxes(row, rule_id, width=width, height=height)
    expected_answer = "compliant" if primary_class == "compliant" else "violation"
    notes = [rule_note] if rule_note else []
    if str(row.get("quality_of_info") or "").lower().startswith("poor"):
        notes.append("source_quality_poor")
    if not boxes and expected_answer == "violation":
        notes.append("violation_without_source_box")
    return {
        "benchmark_version": "0.2.0-scaleup-candidate",
        "image_id": str(row["image_id"]).zfill(7),
        "source_dataset_id": SOURCE_DATASET_ID,
        "source_dataset_revision": SOURCE_DATASET_REVISION,
        "source_split": SOURCE_SPLIT,
        "primary_class": primary_class,
        "violated_source_fields": json.dumps(violated_fields, separators=(",", ":")),
        "rule_id": rule_id,
        "rule_family": rule.rule_family,
        "expected_answer_seed": expected_answer,
        "image_width": str(width),
        "image_height": str(height),
        "image_caption": str(row.get("image_caption") or ""),
        "illumination": str(row.get("illumination") or ""),
        "camera_distance": str(row.get("camera_distance") or ""),
        "view": str(row.get("view") or ""),
        "quality_of_info": str(row.get("quality_of_info") or ""),
        "source_violation_reason": reason,
        "source_violation_boxes_xyxy": json.dumps(boxes, separators=(",", ":")),
        "needs_human_label": "true",
        "notes": ";".join(notes),
    }


def select_scaleup_candidates(
    rows: list[dict[str, Any]],
    *,
    rules: BenchmarkRules,
    per_class: int,
    seed: int,
) -> list[dict[str, str]]:
    """Select a deterministic class-balanced candidate manifest from dataset rows."""
    buckets: dict[str, list[dict[str, Any]]] = {label: [] for label in CLASS_PRIORITY}
    for row in rows:
        primary_class, _ = classify_source_row(row)
        buckets[primary_class].append(row)
    rng = random.Random(seed)
    output: list[dict[str, str]] = []
    compliant_index = 0
    for label in CLASS_PRIORITY:
        bucket = list(buckets[label])
        rng.shuffle(bucket)
        for row in bucket[:per_class]:
            output.append(row_to_scaleup_record(row, rules=rules, compliant_index=compliant_index))
            if label == "compliant":
                compliant_index += 1
    return sorted(output, key=lambda item: (item["primary_class"], item["image_id"], item["rule_id"]))


def write_scaleup_manifest(
    rows: list[dict[str, str]],
    *,
    manifest_path: Path,
    summary_path: Path,
    source_rows_scanned: int,
    per_class: int,
    seed: int,
) -> ScaleupBuildResult:
    """Write scale-up candidate manifest and summary."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    class_counts: dict[str, int] = {}
    rule_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["primary_class"]] = class_counts.get(row["primary_class"], 0) + 1
        rule_counts[row["rule_id"]] = rule_counts.get(row["rule_id"], 0) + 1
    summary = {
        "benchmark_version": "0.2.0-scaleup-candidate",
        "row_count": len(rows),
        "source_rows_scanned": source_rows_scanned,
        "per_class_target": per_class,
        "seed": seed,
        "class_counts": class_counts,
        "rule_counts": rule_counts,
        "provenance": "Generated from ConstructionSite test-split metadata and image dimensions; raw images are not redistributed.",
    }
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    return ScaleupBuildResult(manifest_path=manifest_path, summary_path=summary_path, row_count=len(rows))

