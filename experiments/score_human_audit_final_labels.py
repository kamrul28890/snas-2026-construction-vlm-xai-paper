"""Score audit predictions against the 120-row final-label layer."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["compliant", "violation", "uncertain"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001.csv",
    )
    parser.add_argument(
        "--final-labels",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001_final_labels.csv",
    )
    parser.add_argument("--name", default="human_audit_batch_001_final_label")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def prediction_sources(row: dict[str, str]) -> dict[str, str]:
    return {
        "model_assisted_bootstrap": row["model_assisted_answer_label"],
        "florence_grounding": row["florence_predicted_answer"],
        "ai_annotator_1": row["annotator_1_answer_label"],
        "ai_annotator_2": row["annotator_2_answer_label"],
    }


def build_per_example(
    *,
    batch_rows: list[dict[str, str]],
    final_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    final_by_id = {row["audit_id"]: row for row in final_rows}
    scored = []
    for row in batch_rows:
        final = final_by_id[row["audit_id"]]
        for model_id, prediction in prediction_sources(row).items():
            prediction = prediction.strip().lower()
            truth = final["final_answer_label"].strip().lower()
            scored.append(
                {
                    "model_id": model_id,
                    "audit_id": row["audit_id"],
                    "image_id": row["image_id"],
                    "rule_id": row["rule_id"],
                    "final_answer_label": truth,
                    "predicted_answer": prediction,
                    "answer_correct": str(prediction == truth).lower(),
                    "final_ambiguous": final["final_ambiguous"],
                    "final_label_source": final["final_label_source"],
                    "florence_bootstrap_disagreement": row["florence_answer_correct"] == "false",
                }
            )
    return scored


def f1_for_label(rows: list[dict[str, str]], label: str) -> float:
    true_positive = sum(
        1 for row in rows if row["final_answer_label"] == label and row["predicted_answer"] == label
    )
    false_positive = sum(
        1 for row in rows if row["final_answer_label"] != label and row["predicted_answer"] == label
    )
    false_negative = sum(
        1 for row in rows if row["final_answer_label"] == label and row["predicted_answer"] != label
    )
    if true_positive == 0 and false_positive == 0 and false_negative == 0:
        return math.nan
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def summarize_slice(rows: list[dict[str, str]], *, model_id: str, slice_id: str) -> dict[str, str]:
    correct = sum(1 for row in rows if row["answer_correct"] == "true")
    truth_counts = Counter(row["final_answer_label"] for row in rows)
    pred_counts = Counter(row["predicted_answer"] for row in rows)
    f1s = {label: f1_for_label(rows, label) for label in LABELS}
    valid_f1s = [value for value in f1s.values() if not math.isnan(value)]
    return {
        "model_id": model_id,
        "slice_id": slice_id,
        "n": str(len(rows)),
        "accuracy": f"{correct / len(rows):.6f}" if rows else "",
        "macro_f1": f"{sum(valid_f1s) / len(valid_f1s):.6f}" if valid_f1s else "",
        "compliant_f1": "" if math.isnan(f1s["compliant"]) else f"{f1s['compliant']:.6f}",
        "violation_f1": "" if math.isnan(f1s["violation"]) else f"{f1s['violation']:.6f}",
        "uncertain_f1": "" if math.isnan(f1s["uncertain"]) else f"{f1s['uncertain']:.6f}",
        "truth_compliant": str(truth_counts["compliant"]),
        "truth_violation": str(truth_counts["violation"]),
        "truth_uncertain": str(truth_counts["uncertain"]),
        "predicted_compliant": str(pred_counts["compliant"]),
        "predicted_violation": str(pred_counts["violation"]),
        "predicted_uncertain": str(pred_counts["uncertain"]),
    }


def summarize(scored_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    model_ids = sorted({row["model_id"] for row in scored_rows})
    for model_id in model_ids:
        model_rows = [row for row in scored_rows if row["model_id"] == model_id]
        rows.append(summarize_slice(model_rows, model_id=model_id, slice_id="overall"))
        for rule_id in sorted({row["rule_id"] for row in model_rows}):
            rule_rows = [row for row in model_rows if row["rule_id"] == rule_id]
            rows.append(summarize_slice(rule_rows, model_id=model_id, slice_id=f"rule:{rule_id}"))
        for source in sorted({row["final_label_source"] for row in model_rows}):
            source_rows = [row for row in model_rows if row["final_label_source"] == source]
            rows.append(summarize_slice(source_rows, model_id=model_id, slice_id=f"source:{source}"))
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    batch_rows = read_csv(args.batch)
    final_rows = read_csv(args.final_labels)
    if [row["audit_id"] for row in batch_rows] != [row["audit_id"] for row in final_rows]:
        raise RuntimeError("Batch and final-label audit IDs must match in order")
    per_example = build_per_example(batch_rows=batch_rows, final_rows=final_rows)
    summary = summarize(per_example)
    out_dir = ROOT / "results" / "tables"
    write_csv(per_example, out_dir / f"{args.name}_per_example_scores.csv")
    write_csv(summary, out_dir / f"{args.name}_scores.csv")
    print(f"Wrote {len(summary)} score rows and {len(per_example)} per-example rows for {args.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
