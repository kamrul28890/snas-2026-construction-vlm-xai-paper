"""Metrics for comparing baseline and visually intervened model outputs."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from faithbench.metrics import best_box_match, parse_boxes
from faithbench.scoring import normalize_answer
from faithbench.statistics import paired_bootstrap_difference

INTERVENTION_OUTPUT_FIELDS = [
    "intervention_id",
    "image_id",
    "rule_id",
    "intervention_type",
    "seed",
    "target_box_xyxy",
    "mask_box_xyxy",
    "mask_target_iou",
    "model_id",
    "prompt_id",
    "answer",
    "evidence_regions_xyxy",
    "worker_boxes_xyxy",
    "object_boxes_xyxy",
    "confidence",
    "graded_score",
    "raw_response",
    "provenance",
]


def read_jsonl(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_rows(rows: list[dict[str, str]], *, jsonl_path: Path, csv_path: Path) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INTERVENTION_OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def validate_intervention_row(row: dict[str, str]) -> None:
    missing = [field for field in INTERVENTION_OUTPUT_FIELDS if field not in row]
    if missing:
        raise ValueError(f"Missing intervention output fields: {missing}")
    if normalize_answer(row["answer"]) == "invalid":
        raise ValueError(f"Invalid answer for {row['intervention_id']}: {row['answer']}")
    json.loads(row["target_box_xyxy"]) if row["target_box_xyxy"] else None
    json.loads(row["mask_box_xyxy"])
    json.loads(row["evidence_regions_xyxy"])
    json.loads(row["worker_boxes_xyxy"])
    json.loads(row["object_boxes_xyxy"])
    json.loads(row["raw_response"])


def validate_intervention_outputs(*, jsonl_path: Path, csv_path: Path) -> list[dict[str, str]]:
    rows = read_jsonl(jsonl_path)
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(rows) != len(csv_rows):
        raise RuntimeError(f"JSONL/CSV row mismatch: {len(rows)} != {len(csv_rows)}")
    seen: set[str] = set()
    for row in rows:
        validate_intervention_row(row)
        intervention_id = row["intervention_id"]
        if intervention_id in seen:
            raise RuntimeError(f"Duplicate intervention_id: {intervention_id}")
        seen.add(intervention_id)
    return rows


def summarize_intervention_outputs(
    *,
    intervention_rows: list[dict[str, str]],
    baseline_rows: list[dict[str, str]],
    manifest_by_key: dict[tuple[str, str], dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    baseline_by_key = {(row["image_id"], row["rule_id"]): row for row in baseline_rows}
    per_intervention: list[dict[str, str]] = []
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)

    for row in intervention_rows:
        key = (row["image_id"], row["rule_id"])
        baseline = baseline_by_key[key]
        manifest = manifest_by_key[key]
        image_size = (int(manifest["image_width"]), int(manifest["image_height"]))
        baseline_answer = normalize_answer(baseline["answer"])
        intervention_answer = normalize_answer(row["answer"])
        baseline_boxes = parse_boxes(baseline["evidence_regions_xyxy"])
        intervention_boxes = parse_boxes(row["evidence_regions_xyxy"])
        best_iou, centroid_drift = best_box_match(
            intervention_boxes,
            baseline_boxes,
            image_size=image_size,
        )
        detail = {
            "intervention_id": row["intervention_id"],
            "image_id": row["image_id"],
            "rule_id": row["rule_id"],
            "intervention_type": row["intervention_type"],
            "seed": row["seed"],
            "baseline_answer": baseline_answer,
            "intervention_answer": intervention_answer,
            "answer_changed": str(baseline_answer != intervention_answer).lower(),
            "baseline_evidence_present": str(bool(baseline_boxes)).lower(),
            "intervention_evidence_present": str(bool(intervention_boxes)).lower(),
            "evidence_disappeared": str(bool(baseline_boxes) and not bool(intervention_boxes)).lower(),
            "best_baseline_intervention_iou": "" if math.isnan(best_iou) else str(best_iou),
            "baseline_intervention_centroid_drift": "" if math.isnan(centroid_drift) else str(centroid_drift),
        }
        per_intervention.append(detail)
        grouped[key].append(detail)

    summary_rows = _summary_rows(per_intervention, grouped)
    return summary_rows, per_intervention


def _summary_rows(
    rows: list[dict[str, str]],
    grouped: dict[tuple[str, str], list[dict[str, str]]],
) -> list[dict[str, str]]:
    targeted = [row for row in rows if row["intervention_type"] == "targeted_occlusion"]
    random_rows = [row for row in rows if row["intervention_type"] == "matched_random_occlusion"]
    paired_target_flips: list[float] = []
    paired_random_flips: list[float] = []
    paired_target_drift: list[float] = []
    paired_random_drift: list[float] = []
    for group in grouped.values():
        group_targeted = [row for row in group if row["intervention_type"] == "targeted_occlusion"]
        group_random = [row for row in group if row["intervention_type"] == "matched_random_occlusion"]
        if not group_targeted or not group_random:
            continue
        target = group_targeted[0]
        paired_target_flips.append(_as_float_bool(target["answer_changed"]))
        paired_random_flips.append(_mean(_as_float_bool(row["answer_changed"]) for row in group_random))
        target_drift = _maybe_float(target["baseline_intervention_centroid_drift"])
        random_drifts = [_maybe_float(row["baseline_intervention_centroid_drift"]) for row in group_random]
        random_drifts = [value for value in random_drifts if math.isfinite(value)]
        if math.isfinite(target_drift) and random_drifts:
            paired_target_drift.append(target_drift)
            paired_random_drift.append(_mean(random_drifts))

    rows_out = [
        _metric("targeted_answer_flip_rate", _rate(targeted, "answer_changed"), len(targeted), "targeted occlusion rows"),
        _metric("matched_random_answer_flip_rate", _rate(random_rows, "answer_changed"), len(random_rows), "matched-random occlusion rows"),
        _metric("targeted_evidence_disappearance_rate", _rate(targeted, "evidence_disappeared"), len(targeted), "targeted rows with baseline evidence but no post-mask evidence"),
        _metric("matched_random_evidence_disappearance_rate", _rate(random_rows, "evidence_disappeared"), len(random_rows), "matched-random rows with baseline evidence but no post-mask evidence"),
        _metric("targeted_mean_centroid_drift", _numeric_mean(targeted, "baseline_intervention_centroid_drift"), _numeric_n(targeted, "baseline_intervention_centroid_drift"), "baseline-to-intervention evidence drift"),
        _metric("matched_random_mean_centroid_drift", _numeric_mean(random_rows, "baseline_intervention_centroid_drift"), _numeric_n(random_rows, "baseline_intervention_centroid_drift"), "baseline-to-intervention evidence drift"),
        _metric("targeted_mean_iou", _numeric_mean(targeted, "best_baseline_intervention_iou"), _numeric_n(targeted, "best_baseline_intervention_iou"), "best evidence IoU versus baseline"),
        _metric("matched_random_mean_iou", _numeric_mean(random_rows, "best_baseline_intervention_iou"), _numeric_n(random_rows, "best_baseline_intervention_iou"), "best evidence IoU versus baseline"),
    ]
    flip_diff = paired_bootstrap_difference(paired_target_flips, paired_random_flips)
    drift_diff = paired_bootstrap_difference(paired_target_drift, paired_random_drift)
    rows_out.extend(
        [
            _ci_metric("paired_answer_flip_rate_difference", flip_diff, "targeted minus per-image matched-random mean"),
            _ci_metric("paired_centroid_drift_difference", drift_diff, "targeted minus per-image matched-random mean"),
        ]
    )
    return rows_out


def _metric(metric_id: str, value: float, n: int, notes: str) -> dict[str, str]:
    return {
        "metric_id": metric_id,
        "value": "" if math.isnan(value) else str(float(value)),
        "n": str(n),
        "ci_low": "",
        "ci_high": "",
        "notes": notes,
    }


def _ci_metric(metric_id: str, ci_result: dict[str, float | int], notes: str) -> dict[str, str]:
    point = float(ci_result["point"])
    lo = float(ci_result["lo"])
    hi = float(ci_result["hi"])
    return {
        "metric_id": metric_id,
        "value": "" if math.isnan(point) else str(point),
        "n": str(ci_result["n"]),
        "ci_low": "" if math.isnan(lo) else str(lo),
        "ci_high": "" if math.isnan(hi) else str(hi),
        "notes": notes,
    }


def _rate(rows: list[dict[str, str]], field: str) -> float:
    return _mean(_as_float_bool(row[field]) for row in rows) if rows else math.nan


def _numeric_mean(rows: list[dict[str, str]], field: str) -> float:
    values = [_maybe_float(row[field]) for row in rows]
    values = [value for value in values if math.isfinite(value)]
    return _mean(values) if values else math.nan


def _numeric_n(rows: list[dict[str, str]], field: str) -> int:
    return sum(1 for row in rows if math.isfinite(_maybe_float(row[field])))


def _mean(values: object) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else math.nan


def _as_float_bool(value: str) -> float:
    return 1.0 if value == "true" else 0.0


def _maybe_float(value: str) -> float:
    if value == "":
        return math.nan
    return float(value)


def write_summary_rows(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric_id", "value", "n", "ci_low", "ci_high", "notes"])
        writer.writeheader()
        writer.writerows(rows)


def write_detail_rows(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
