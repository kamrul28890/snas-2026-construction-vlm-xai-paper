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

    score_files = {
        "Annotation bootstrap": ROOT / "results" / "tables" / "pilot_annotation_bootstrap_scores.csv",
        "Manifest seed": ROOT / "results" / "tables" / "pilot_manifest_seed_scores.csv",
        "Majority violation": ROOT / "results" / "tables" / "pilot_majority_violation_scores.csv",
    }
    lines = [
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Adapter & Accuracy & Macro-F1 & Evidence present & Nonambig. acc. \\\\",
        "\\midrule",
    ]
    for label, path in score_files.items():
        scores = read_score(path)
        lines.append(
            f"{label} & {pct(scores['accuracy'])} & {pct(scores['macro_f1'])} & "
            f"{pct(scores['evidence_presence_rate'])} & {pct(scores['nonambiguous_accuracy'])} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    (out_dir / "pilot_baseline_scores.tex").write_text("\n".join(lines), encoding="utf-8")

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
    (out_dir / "pilot_intervention_counts.tex").write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote generated paper tables to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

