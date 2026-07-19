"""Benchmark scoring metrics for normalized model outputs."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from faithbench.geometry import box_iou, normalized_centroid_drift
from faithbench.scoring import normalize_answer


@dataclass(frozen=True)
class ScoreSummary:
    """Aggregate score table and per-example rows."""

    summary_rows: list[dict[str, str]]
    example_rows: list[dict[str, str]]


def load_jsonl(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_annotations(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows = load_jsonl(path)
    return {(row["image_id"], row["rule_id"]): row for row in rows}


def parse_boxes(value: str) -> list[list[float]]:
    if not value:
        return []
    return json.loads(value)


def best_box_match(
    predicted_boxes: list[list[float]],
    reference_boxes: list[list[float]],
    *,
    image_size: tuple[int, int],
) -> tuple[float, float]:
    """Return max IoU and min centroid drift across predicted/reference boxes."""
    if not predicted_boxes or not reference_boxes:
        return math.nan, math.nan
    best_iou = 0.0
    best_drift = math.inf
    for pred in predicted_boxes:
        pbox = tuple(float(v) for v in pred)
        for ref in reference_boxes:
            rbox = tuple(float(v) for v in ref)
            best_iou = max(best_iou, box_iou(pbox, rbox))
            drift = normalized_centroid_drift(pbox, rbox, image_size)
            if math.isfinite(drift):
                best_drift = min(best_drift, drift)
    return best_iou, best_drift if math.isfinite(best_drift) else math.nan


def binary_f1(tp: int, fp: int, fn: int) -> float:
    denom = 2 * tp + fp + fn
    return (2 * tp / denom) if denom else 0.0


def macro_f1(y_true: list[str], y_pred: list[str], labels: tuple[str, ...] = ("compliant", "violation")) -> float:
    scores = []
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        scores.append(binary_f1(tp, fp, fn))
    return sum(scores) / len(scores)


def score_model_outputs(
    *,
    model_output_rows: list[dict[str, str]],
    annotations_by_key: dict[tuple[str, str], dict[str, str]],
    manifest_by_key: dict[tuple[str, str], dict[str, str]],
) -> ScoreSummary:
    """Score normalized model outputs against annotation rows."""
    example_rows: list[dict[str, str]] = []
    y_true: list[str] = []
    y_pred: list[str] = []
    for row in model_output_rows:
        key = (row["image_id"], row["rule_id"])
        annotation = annotations_by_key[key]
        manifest = manifest_by_key[key]
        truth = normalize_answer(annotation["answer_label"])
        pred = normalize_answer(row["answer"])
        y_true.append(truth)
        y_pred.append(pred)
        pred_boxes = parse_boxes(row["evidence_regions_xyxy"])
        ref_boxes = parse_boxes(annotation["evidence_regions_xyxy"])
        best_iou, best_drift = best_box_match(
            pred_boxes,
            ref_boxes,
            image_size=(int(manifest["image_width"]), int(manifest["image_height"])),
        )
        example_rows.append(
            {
                "image_id": row["image_id"],
                "rule_id": row["rule_id"],
                "model_id": row["model_id"],
                "prompt_id": row["prompt_id"],
                "truth_answer": truth,
                "predicted_answer": pred,
                "answer_correct": str(truth == pred).lower(),
                "invalid_output": str(pred == "invalid").lower(),
                "has_predicted_evidence": str(bool(pred_boxes)).lower(),
                "has_reference_evidence": str(bool(ref_boxes)).lower(),
                "best_evidence_iou": "" if math.isnan(best_iou) else str(best_iou),
                "best_evidence_centroid_drift": "" if math.isnan(best_drift) else str(best_drift),
                "annotation_ambiguous": annotation["ambiguous"],
                "annotation_applies_to_image": annotation["applies_to_image"],
            }
        )

    total = len(example_rows)
    correct = sum(1 for row in example_rows if row["answer_correct"] == "true")
    invalid = sum(1 for row in example_rows if row["invalid_output"] == "true")
    evidence_present = sum(1 for row in example_rows if row["has_predicted_evidence"] == "true")
    nonambiguous_rows = [row for row in example_rows if row["annotation_ambiguous"] == "no"]
    nonambig_correct = sum(1 for row in nonambiguous_rows if row["answer_correct"] == "true")
    ious = [
        float(row["best_evidence_iou"])
        for row in example_rows
        if row["best_evidence_iou"]
    ]
    summary_rows = [
        _metric("accuracy", correct / total if total else math.nan, total, "all annotated rows"),
        _metric("macro_f1", macro_f1(y_true, y_pred), total, "compliant and violation labels"),
        _metric("invalid_rate", invalid / total if total else math.nan, total, "normalized invalid answer rows"),
        _metric("evidence_presence_rate", evidence_present / total if total else math.nan, total, "rows with at least one predicted evidence box"),
        _metric(
            "nonambiguous_accuracy",
            nonambig_correct / len(nonambiguous_rows) if nonambiguous_rows else math.nan,
            len(nonambiguous_rows),
            "rows where bootstrap annotation ambiguous=no",
        ),
        _metric(
            "mean_best_evidence_iou",
            sum(ious) / len(ious) if ious else math.nan,
            len(ious),
            "rows with predicted and reference evidence boxes",
        ),
    ]
    return ScoreSummary(summary_rows=summary_rows, example_rows=example_rows)


def _metric(metric_id: str, value: float, n: int, notes: str) -> dict[str, str]:
    return {
        "metric_id": metric_id,
        "value": "" if math.isnan(value) else str(float(value)),
        "n": str(n),
        "notes": notes,
    }


def load_manifest_by_key(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {(row["image_id"], row["rule_id"]): row for row in rows}


def write_score_outputs(summary: ScoreSummary, *, summary_path: Path, examples_path: Path) -> None:
    """Write summary metrics and per-example scores."""
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    examples_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric_id", "value", "n", "notes"])
        writer.writeheader()
        writer.writerows(summary.summary_rows)
    fields = list(summary.example_rows[0].keys()) if summary.example_rows else []
    with examples_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary.example_rows)
