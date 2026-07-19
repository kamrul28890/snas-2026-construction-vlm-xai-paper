"""Validate Phase 4 intervention specs and score tables."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    interventions = ROOT / "benchmark" / "interventions" / "pilot_interventions.jsonl"
    intervention_summary = ROOT / "benchmark" / "interventions" / "pilot_interventions_summary.json"
    with interventions.open("r", encoding="utf-8") as handle:
        intervention_rows = [json.loads(line) for line in handle if line.strip()]
    with intervention_summary.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    if len(intervention_rows) != summary["row_count"]:
        raise RuntimeError("Intervention row count mismatch")
    if summary["counts"] != {"targeted_occlusion": 158, "matched_random_occlusion": 790}:
        raise RuntimeError(f"Unexpected intervention counts: {summary['counts']}")
    for row in intervention_rows:
        if not row["mask_box_xyxy"]:
            raise RuntimeError(f"Missing mask box for intervention {row['intervention_id']}")
        json.loads(row["mask_box_xyxy"])

    expected_score_files = [
        "pilot_annotation_bootstrap_scores.csv",
        "pilot_florence_grounding_scores.csv",
        "pilot_manifest_seed_scores.csv",
        "pilot_majority_violation_scores.csv",
        "scaleup_annotation_bootstrap_scores.csv",
        "scaleup_caption_keyword_scores.csv",
        "scaleup_florence_grounding_scores.csv",
        "scaleup_manifest_seed_scores.csv",
        "scaleup_majority_violation_scores.csv",
    ]
    for filename in expected_score_files:
        rows = _read_csv(ROOT / "results" / "tables" / filename)
        metric_ids = {row["metric_id"] for row in rows}
        required = {"accuracy", "macro_f1", "invalid_rate", "evidence_presence_rate"}
        missing = required - metric_ids
        if missing:
            raise RuntimeError(f"{filename} missing metrics: {sorted(missing)}")
    intervention_summary = _read_csv(ROOT / "results" / "tables" / "pilot_florence_interventions_summary.csv")
    intervention_metrics = {row["metric_id"] for row in intervention_summary}
    expected_intervention_metrics = {
        "targeted_answer_flip_rate",
        "matched_random_answer_flip_rate",
        "paired_answer_flip_rate_difference",
        "paired_centroid_drift_difference",
    }
    missing = expected_intervention_metrics - intervention_metrics
    if missing:
        raise RuntimeError(f"pilot_florence_interventions_summary.csv missing metrics: {sorted(missing)}")
    for filename in ["pilot_florence_grounding_slices.csv", "scaleup_florence_grounding_slices.csv"]:
        rows = _read_csv(ROOT / "results" / "tables" / filename)
        slice_keys = {(row["slice_type"], row["slice_value"]) for row in rows}
        if ("overall", "all") not in slice_keys:
            raise RuntimeError(f"{filename} missing overall slice")
        if not any(slice_type == "rule_id" for slice_type, _ in slice_keys):
            raise RuntimeError(f"{filename} missing rule_id slices")
    print("Validated Phase 4 intervention specs and score tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
