"""Build a prioritized human-audit annotation batch from scale-up diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.schema import load_rules

OUTPUT_FIELDS = [
    "audit_id",
    "image_id",
    "rule_id",
    "question",
    "image_width",
    "image_height",
    "model_assisted_answer_label",
    "florence_predicted_answer",
    "florence_answer_correct",
    "annotation_ambiguous",
    "annotation_applies_to_image",
    "has_reference_evidence",
    "best_evidence_iou",
    "best_evidence_centroid_drift",
    "priority_score",
    "priority_reason",
    "image_caption",
    "target_box_xyxy",
    "source_violation_boxes_xyxy",
    "model_assisted_evidence_regions_xyxy",
    "annotator_1_answer_label",
    "annotator_1_evidence_regions_xyxy",
    "annotator_1_ambiguous",
    "annotator_1_notes",
    "annotator_2_answer_label",
    "annotator_2_evidence_regions_xyxy",
    "annotator_2_ambiguous",
    "annotator_2_notes",
    "adjudicated_answer_label",
    "adjudicated_evidence_regions_xyxy",
    "adjudicated_ambiguous",
    "adjudication_notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=120)
    parser.add_argument("--per-rule-cap", type=int, default=30)
    parser.add_argument(
        "--scores",
        type=Path,
        default=ROOT / "results" / "tables" / "scaleup_florence_grounding_per_example_scores.csv",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "benchmark" / "splits" / "scaleup_candidate_manifest.csv",
    )
    parser.add_argument(
        "--annotations",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "scaleup_model_assisted_annotations.jsonl",
    )
    parser.add_argument("--output-stem", default="human_audit_batch_001")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def priority_for(row: dict[str, str]) -> tuple[int, str]:
    score = 0
    reasons: list[str] = []
    if row["answer_correct"] == "false":
        score += 100
        reasons.append("florence_disagrees_with_bootstrap")
    if row["annotation_ambiguous"] == "no":
        score += 30
        reasons.append("bootstrap_nonambiguous")
    if row["annotation_applies_to_image"] == "yes":
        score += 20
        reasons.append("rule_applies")
    if row["has_reference_evidence"] == "true" and row["best_evidence_iou"]:
        iou = float(row["best_evidence_iou"])
        if iou < 0.1:
            score += 20
            reasons.append("low_evidence_iou")
    if row["has_predicted_evidence"] == "false":
        score += 10
        reasons.append("missing_predicted_evidence")
    return score, ";".join(reasons) if reasons else "coverage_sample"


def build_batch(
    *,
    scores: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
    annotation_rows: list[dict[str, str]],
    questions_by_rule: dict[str, str],
    batch_size: int,
    per_rule_cap: int,
) -> list[dict[str, str]]:
    manifest_by_key = {(row["image_id"], row["rule_id"]): row for row in manifest_rows}
    annotations_by_key = {(row["image_id"], row["rule_id"]): row for row in annotation_rows}
    candidates = []
    for row in scores:
        score, reason = priority_for(row)
        key = (row["image_id"], row["rule_id"])
        manifest = manifest_by_key[key]
        annotation = annotations_by_key[key]
        candidates.append((score, reason, row, manifest, annotation))
    candidates.sort(key=lambda item: (-item[0], item[2]["rule_id"], item[2]["image_id"]))

    selected: list[tuple[int, str, dict[str, str], dict[str, str], dict[str, str]]] = []
    per_rule_counts: dict[str, int] = defaultdict(int)
    used: set[tuple[str, str]] = set()
    for item in candidates:
        _, _, row, _, _ = item
        key = (row["image_id"], row["rule_id"])
        if per_rule_counts[row["rule_id"]] >= per_rule_cap:
            continue
        selected.append(item)
        used.add(key)
        per_rule_counts[row["rule_id"]] += 1
        if len(selected) >= batch_size:
            break
    if len(selected) < batch_size:
        for item in candidates:
            _, _, row, _, _ = item
            key = (row["image_id"], row["rule_id"])
            if key in used:
                continue
            selected.append(item)
            used.add(key)
            if len(selected) >= batch_size:
                break

    rows_out = []
    for index, (score, reason, row, manifest, annotation) in enumerate(selected, 1):
        rows_out.append(
            {
                "audit_id": f"audit_001_{index:04d}",
                "image_id": row["image_id"],
                "rule_id": row["rule_id"],
                "question": questions_by_rule[row["rule_id"]],
                "image_width": manifest["image_width"],
                "image_height": manifest["image_height"],
                "model_assisted_answer_label": row["truth_answer"],
                "florence_predicted_answer": row["predicted_answer"],
                "florence_answer_correct": row["answer_correct"],
                "annotation_ambiguous": row["annotation_ambiguous"],
                "annotation_applies_to_image": row["annotation_applies_to_image"],
                "has_reference_evidence": row["has_reference_evidence"],
                "best_evidence_iou": row["best_evidence_iou"],
                "best_evidence_centroid_drift": row["best_evidence_centroid_drift"],
                "priority_score": str(score),
                "priority_reason": reason,
                "image_caption": manifest["image_caption"],
                "target_box_xyxy": manifest.get("target_box_xyxy", ""),
                "source_violation_boxes_xyxy": manifest.get("source_violation_boxes_xyxy", ""),
                "model_assisted_evidence_regions_xyxy": annotation["evidence_regions_xyxy"],
                "annotator_1_answer_label": "",
                "annotator_1_evidence_regions_xyxy": "",
                "annotator_1_ambiguous": "",
                "annotator_1_notes": "",
                "annotator_2_answer_label": "",
                "annotator_2_evidence_regions_xyxy": "",
                "annotator_2_ambiguous": "",
                "annotator_2_notes": "",
                "adjudicated_answer_label": "",
                "adjudicated_evidence_regions_xyxy": "",
                "adjudicated_ambiguous": "",
                "adjudication_notes": "",
            }
        )
    return rows_out


def write_csv_jsonl(rows: list[dict[str, str]], *, csv_path: Path, jsonl_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")


def write_summary(rows: list[dict[str, str]], *, path: Path, args: argparse.Namespace) -> None:
    rule_counts: dict[str, int] = defaultdict(int)
    reason_counts: dict[str, int] = defaultdict(int)
    disagreement_count = 0
    for row in rows:
        rule_counts[row["rule_id"]] += 1
        if row["florence_answer_correct"] == "false":
            disagreement_count += 1
        for reason in row["priority_reason"].split(";"):
            reason_counts[reason] += 1
    summary = {
        "batch_id": args.output_stem,
        "row_count": len(rows),
        "batch_size_requested": args.batch_size,
        "per_rule_cap": args.per_rule_cap,
        "source_scores": str(args.scores),
        "source_manifest": str(args.manifest),
        "source_annotations": str(args.annotations),
        "rule_counts": dict(sorted(rule_counts.items())),
        "priority_reason_counts": dict(sorted(reason_counts.items())),
        "florence_bootstrap_disagreement_count": disagreement_count,
        "provenance": "Prioritized for independent human/domain audit from scale-up Florence score diagnostics. Blank annotator fields are intentionally unfilled.",
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")


def main() -> int:
    args = parse_args()
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    rows = build_batch(
        scores=read_csv(args.scores),
        manifest_rows=read_csv(args.manifest),
        annotation_rows=read_jsonl(args.annotations),
        questions_by_rule={rule.rule_id: rule.question for rule in rules.rules},
        batch_size=args.batch_size,
        per_rule_cap=args.per_rule_cap,
    )
    out_dir = ROOT / "benchmark" / "annotations"
    write_csv_jsonl(
        rows,
        csv_path=out_dir / f"{args.output_stem}.csv",
        jsonl_path=out_dir / f"{args.output_stem}.jsonl",
    )
    write_summary(rows, path=out_dir / f"{args.output_stem}_summary.json", args=args)
    print(f"Wrote {len(rows)} human-audit rows to {out_dir / (args.output_stem + '.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
