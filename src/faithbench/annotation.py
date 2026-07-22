"""Model-assisted annotation helpers for automated baseline labels."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from faithbench.manifest import LEGACY_RULE_MAP

ANNOTATOR_ID = "gpt5_model_assisted_metadata_v1"
ANNOTATION_VERSION = "0.1.0-model-assisted"

RULE_TO_SOURCE_FIELD = {
    "ppe_hard_hat": "rule_1_violation",
    "fall_harness": "rule_2_violation",
    "guardrail_edge": "rule_3_violation",
    "struck_by_equipment": "rule_4_violation",
}

RULE_EVIDENCE_OBJECTS = {
    "ppe_hard_hat": ["worker", "head_protection", "hard_hat"],
    "fall_harness": ["worker", "fall_protection", "harness"],
    "guardrail_edge": ["edge_or_opening", "guardrail_or_barrier"],
    "struck_by_equipment": ["worker", "heavy_equipment", "proximity_zone"],
}


@dataclass(frozen=True)
class AnnotationBuildResult:
    """Paths and counts produced by a model-assisted annotation build."""

    jsonl_path: Path
    csv_path: Path
    summary_path: Path
    row_count: int


def normalized_box_to_abs(box: list[float], width: int, height: int) -> list[int]:
    """Convert a normalized xyxy box to clipped absolute-pixel coordinates."""
    x0, y0, x1, y1 = box
    abs_box = [
        int(round(x0 * width)),
        int(round(y0 * height)),
        int(round(x1 * width)),
        int(round(y1 * height)),
    ]
    abs_box[0] = min(max(abs_box[0], 0), max(width - 1, 0))
    abs_box[1] = min(max(abs_box[1], 0), max(height - 1, 0))
    abs_box[2] = min(max(abs_box[2], abs_box[0] + 1), width)
    abs_box[3] = min(max(abs_box[3], abs_box[1] + 1), height)
    return abs_box


def parse_target_box(value: str) -> list[list[int]]:
    """Parse a manifest target box into an annotation-region list."""
    if not value:
        return []
    box = json.loads(value)
    return [[int(v) for v in box]]


def source_violation_boxes(
    violation: dict[str, Any] | None, *, width: int, height: int
) -> list[list[int]]:
    """Return source-rule violation boxes in absolute-pixel coordinates."""
    if not violation:
        return []
    boxes = violation.get("bounding_box") or []
    return [normalized_box_to_abs([float(v) for v in box], width, height) for box in boxes]


def caption_has_worker(caption: str) -> bool:
    lower = caption.lower()
    return "worker" in lower or "workers" in lower or "person" in lower or "people" in lower


def caption_has_equipment(caption: str) -> bool:
    lower = caption.lower()
    return any(term in lower for term in ["excavator", "crane", "equipment", "loader", "truck"])


def infer_applies_to_image(rule_id: str, row: dict[str, Any], manifest_row: dict[str, str]) -> str:
    """Infer whether a rule is visually applicable from metadata and captions."""
    source_field = RULE_TO_SOURCE_FIELD[rule_id]
    if row.get(source_field) is not None:
        return "yes"
    caption = str(row.get("image_caption") or "")
    has_worker = caption_has_worker(caption) or manifest_row["has_worker_box"] == "true"
    has_object_box = manifest_row["has_object_box"] == "true"
    if rule_id == "struck_by_equipment":
        has_equipment = bool(row.get("excavator")) or caption_has_equipment(caption)
        if has_worker and has_equipment:
            return "yes"
        if has_worker or has_equipment:
            return "uncertain"
        return "no"
    if rule_id == "guardrail_edge":
        lower = caption.lower()
        context_terms = ["edge", "opening", "guardrail", "barrier", "rebar", "cage", "elevated"]
        if has_object_box or any(term in lower for term in context_terms):
            return "yes"
        return "uncertain" if has_worker else "no"
    if has_worker:
        return "yes"
    return "uncertain" if has_object_box else "no"


def infer_multi_worker_ambiguity(row: dict[str, Any]) -> str:
    text = f"{row.get('image_caption') or ''} {row.get('rule_1_violation') or ''}".lower()
    markers = ["multiple worker", "multiple workers", "two workers", "three workers", "workers"]
    return "yes" if any(marker in text for marker in markers) else "no"


def model_assisted_annotation(
    manifest_row: dict[str, str],
    dataset_row: dict[str, Any],
) -> dict[str, str]:
    """Create one completed model-assisted annotation row."""
    rule_id = manifest_row["rule_id"]
    width = int(manifest_row["image_width"])
    height = int(manifest_row["image_height"])
    source_field = RULE_TO_SOURCE_FIELD[rule_id]
    violation = dataset_row.get(source_field)
    answer_label = "violation" if violation is not None else "compliant"
    applies_to_image = infer_applies_to_image(rule_id, dataset_row, manifest_row)
    image_quality_issue = "yes" if "poor" in str(dataset_row.get("quality_of_info") or "").lower() else "no"
    multi_worker = infer_multi_worker_ambiguity(dataset_row)
    if violation is not None:
        evidence_regions = source_violation_boxes(violation, width=width, height=height)
    else:
        evidence_regions = parse_target_box(manifest_row["target_box_xyxy"])

    ambiguous = "yes" if (
        applies_to_image != "yes"
        or image_quality_issue == "yes"
        or manifest_row["annotation_priority"] in {"missing_evidence", "underpowered_class"}
    ) else "no"

    source_reason = ""
    if isinstance(violation, dict):
        source_reason = str(violation.get("reason") or "")
    notes = [
        "automated baseline annotation, not human ground truth",
        f"source_quality={dataset_row.get('quality_of_info')}",
    ]
    if source_reason:
        notes.append(f"source_reason={source_reason}")
    if manifest_row.get("notes"):
        notes.append(f"manifest_notes={manifest_row['notes']}")

    return {
        "annotation_version": ANNOTATION_VERSION,
        "image_id": manifest_row["image_id"],
        "rule_id": rule_id,
        "question": manifest_row.get("question", ""),
        "expected_answer_seed": manifest_row["expected_answer_seed"],
        "annotator_id": ANNOTATOR_ID,
        "applies_to_image": applies_to_image,
        "answer_label": answer_label,
        "evidence_objects": ",".join(RULE_EVIDENCE_OBJECTS[rule_id]),
        "evidence_regions_xyxy": json.dumps(evidence_regions, separators=(",", ":")),
        "ambiguous": ambiguous,
        "image_quality_issue": image_quality_issue,
        "multi_worker_ambiguity": multi_worker,
        "model_evidence_acceptable": "not_shown",
        "free_text_notes": "; ".join(notes),
    }


def load_manifest_with_questions(manifest_path: Path, rules_by_id: dict[str, Any]) -> list[dict[str, str]]:
    """Load manifest rows and attach rule questions for annotation outputs."""
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["question"] = rules_by_id[row["rule_id"]].question
    return rows


def build_model_assisted_annotations(
    *,
    manifest_rows: list[dict[str, str]],
    dataset_rows_by_id: dict[str, dict[str, Any]],
    jsonl_path: Path,
    csv_path: Path,
    summary_path: Path,
) -> AnnotationBuildResult:
    """Write completed model-assisted annotation files."""
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    annotations = []
    missing = []
    for row in manifest_rows:
        dataset_row = dataset_rows_by_id.get(row["image_id"])
        if dataset_row is None:
            missing.append(row["image_id"])
            continue
        annotations.append(model_assisted_annotation(row, dataset_row))
    if missing:
        raise RuntimeError(f"Missing dataset rows for {len(missing)} image IDs: {missing[:5]}")

    fields = list(annotations[0].keys()) if annotations else []
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for annotation in annotations:
            handle.write(json.dumps(annotation, separators=(",", ":")) + "\n")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(annotations)

    summary: dict[str, Any] = {
        "annotation_version": ANNOTATION_VERSION,
        "annotator_id": ANNOTATOR_ID,
        "row_count": len(annotations),
        "provenance": "Generated from ConstructionSite metadata, captions, source rule-violation records, and pilot manifest target boxes. This is not human/domain-expert ground truth.",
        "legacy_rule_map": LEGACY_RULE_MAP,
        "answer_counts": {},
        "applies_to_image_counts": {},
        "ambiguous_counts": {},
    }
    for annotation in annotations:
        for key, bucket in (
            ("answer_label", "answer_counts"),
            ("applies_to_image", "applies_to_image_counts"),
            ("ambiguous", "ambiguous_counts"),
        ):
            value = annotation[key]
            summary[bucket][value] = summary[bucket].get(value, 0) + 1
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")

    return AnnotationBuildResult(
        jsonl_path=jsonl_path,
        csv_path=csv_path,
        summary_path=summary_path,
        row_count=len(annotations),
    )
