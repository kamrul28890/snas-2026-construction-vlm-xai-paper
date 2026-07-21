"""Generate NeurIPS-scaffold tables from benchmark artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_score(path: Path) -> dict[str, str]:
    rows = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows[row["metric_id"]] = row["value"]
    return rows


def pct(value: str) -> str:
    if value == "":
        return "--"
    return f"{float(value) * 100:.1f}\\%"


def main() -> int:
    out_dir = ROOT / "paper" / "neurips" / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    pilot_score_files = {
        "Annotation bootstrap": ROOT / "results" / "tables" / "pilot_annotation_bootstrap_scores.csv",
        "Florence grounding": ROOT / "results" / "tables" / "pilot_florence_grounding_scores.csv",
        "Manifest seed": ROOT / "results" / "tables" / "pilot_manifest_seed_scores.csv",
        "Majority violation": ROOT / "results" / "tables" / "pilot_majority_violation_scores.csv",
    }
    write_score_table(out_dir / "pilot_baseline_scores.tex", pilot_score_files)

    scaleup_score_files = {
        "Annotation bootstrap": ROOT / "results" / "tables" / "scaleup_annotation_bootstrap_scores.csv",
        "Florence grounding": ROOT / "results" / "tables" / "scaleup_florence_grounding_scores.csv",
        "Manifest seed": ROOT / "results" / "tables" / "scaleup_manifest_seed_scores.csv",
        "Majority violation": ROOT / "results" / "tables" / "scaleup_majority_violation_scores.csv",
        "Caption keyword": ROOT / "results" / "tables" / "scaleup_caption_keyword_scores.csv",
    }
    write_score_table(out_dir / "scaleup_baseline_scores.tex", scaleup_score_files)

    with (ROOT / "benchmark" / "splits" / "scaleup_candidate_manifest_summary.json").open(
        "r", encoding="utf-8"
    ) as handle:
        scaleup_summary = json.load(handle)
    lines = [
        "\\begin{tabular}{lr}",
        "\\toprule",
        "Class & Count \\\\",
        "\\midrule",
    ]
    for label, count in scaleup_summary["class_counts"].items():
        pretty = label.replace("_", " ").title()
        lines.append(f"{pretty} & {count} \\\\")
    lines.extend(["\\midrule", f"Total & {scaleup_summary['row_count']} \\\\", "\\bottomrule", "\\end{tabular}", ""])
    (out_dir / "scaleup_candidate_counts.tex").write_text("\n".join(lines), encoding="utf-8")

    write_intervention_table(out_dir / "pilot_intervention_counts.tex")
    write_intervention_effects_table(out_dir / "pilot_intervention_effects.tex")
    write_rule_slice_table(out_dir / "scaleup_florence_rule_slices.tex")
    write_audit_final_score_table(out_dir / "human_audit_final_scores.tex")

    print(f"Wrote generated paper tables to {out_dir}")
    return 0


def write_score_table(output_path: Path, score_files: dict[str, Path]) -> None:
    lines = [
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Adapter & Accuracy & Macro-F1 & Evidence present & Nonambig. acc. \\\\",
        "\\midrule",
    ]
    for label, score_path in score_files.items():
        scores = read_score(score_path)
        lines.append(
            f"{label} & {pct(scores['accuracy'])} & {pct(scores['macro_f1'])} & "
            f"{pct(scores['evidence_presence_rate'])} & {pct(scores['nonambiguous_accuracy'])} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_intervention_table(path: Path) -> None:
    with (ROOT / "benchmark" / "interventions" / "pilot_interventions_summary.json").open(
        "r", encoding="utf-8"
    ) as handle:
        intervention_summary = json.load(handle)
    lines = [
        "\\begin{tabular}{lr}",
        "\\toprule",
        "Intervention type & Count \\\\",
        "\\midrule",
    ]
    for label, count in intervention_summary["counts"].items():
        pretty = label.replace("_", " ").title()
        lines.append(f"{pretty} & {count} \\\\")
    lines.extend(
        [
            "\\midrule",
            f"Total & {intervention_summary['row_count']} \\\\",
            "\\bottomrule",
            "\\end{tabular}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_intervention_effects_table(path: Path) -> None:
    scores = read_score(ROOT / "results" / "tables" / "pilot_florence_interventions_summary.csv")
    lines = [
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "Metric & Targeted & Matched random & Paired diff. \\\\",
        "\\midrule",
        (
            f"Answer flip rate & {pct(scores['targeted_answer_flip_rate'])} & "
            f"{pct(scores['matched_random_answer_flip_rate'])} & "
            f"{pct(scores['paired_answer_flip_rate_difference'])} \\\\"
        ),
        (
            f"Centroid drift & {float(scores['targeted_mean_centroid_drift']):.3f} & "
            f"{float(scores['matched_random_mean_centroid_drift']):.3f} & "
            f"{float(scores['paired_centroid_drift_difference']):.3f} \\\\"
        ),
        (
            f"Evidence disappearance & {pct(scores['targeted_evidence_disappearance_rate'])} & "
            f"{pct(scores['matched_random_evidence_disappearance_rate'])} & -- \\\\"
        ),
        "\\bottomrule",
        "\\end{tabular}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_rule_slice_table(path: Path) -> None:
    rows = []
    with (ROOT / "results" / "tables" / "scaleup_florence_grounding_slices.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            if row["slice_type"] == "rule_id":
                rows.append(row)
    lines = [
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Rule & N & Accuracy & Evidence present & Mean IoU \\\\",
        "\\midrule",
    ]
    for row in rows:
        pretty = pretty_label(row["slice_value"])
        lines.append(
            f"{pretty} & {row['n']} & {pct(row['accuracy'])} & "
            f"{pct(row['evidence_presence_rate'])} & {float(row['mean_best_evidence_iou']):.3f} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_audit_final_score_table(path: Path) -> None:
    rows = []
    with (ROOT / "results" / "tables" / "human_audit_batch_001_final_label_scores.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            if row["slice_id"] == "overall":
                rows.append(row)
    order = {
        "model_assisted_bootstrap": "Annotation bootstrap",
        "florence_grounding": "Florence grounding",
        "ai_annotator_1": "AI annotator 1",
        "ai_annotator_2": "AI annotator 2",
    }
    rows.sort(key=lambda row: list(order).index(row["model_id"]))
    lines = [
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "Source & N & Accuracy & Macro-F1 \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{order[row['model_id']]} & {row['n']} & {pct(row['accuracy'])} & {pct(row['macro_f1'])} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def pretty_label(value: str) -> str:
    labels = {
        "fall_harness": "Fall harness",
        "guardrail_edge": "Guardrail edge",
        "ppe_hard_hat": "PPE hard hat",
        "struck_by_equipment": "Struck-by equipment",
    }
    return labels.get(value, value.replace("_", " ").title())


if __name__ == "__main__":
    raise SystemExit(main())
