"""Generate completed model-assisted annotations for the pilot manifest."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.annotation import build_model_assisted_annotations, load_manifest_with_questions
from faithbench.schema import load_rules


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=ROOT.parent / "Explainable-AI-Mustafa-Abdallah",
        help="Sibling XAI source repository with the ConstructionSite dataset loader.",
    )
    return parser.parse_args()


def load_dataset_rows(source_repo: Path, image_ids: set[str]) -> dict[str, dict]:
    source_module = source_repo / "pilot" / "src"
    if not source_module.is_dir():
        raise FileNotFoundError(f"XAI pilot source not found: {source_module}")
    sys.path.insert(0, str(source_module))
    from xai_pilot.data import load_construction_site

    rows = {}
    for row in load_construction_site(split="test", streaming=True):
        image_id = str(row["image_id"]).zfill(7)
        if image_id in image_ids:
            rows[image_id] = {key: value for key, value in row.items() if key != "image"}
            if len(rows) == len(image_ids):
                break
    return rows


def main() -> int:
    args = parse_args()
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    rules_by_id = {rule.rule_id: rule for rule in rules.rules}
    manifest_rows = load_manifest_with_questions(
        ROOT / "benchmark" / "splits" / "pilot_manifest.csv",
        rules_by_id,
    )
    dataset_rows_by_id = load_dataset_rows(
        args.source_repo.resolve(),
        {row["image_id"] for row in manifest_rows},
    )
    result = build_model_assisted_annotations(
        manifest_rows=manifest_rows,
        dataset_rows_by_id=dataset_rows_by_id,
        jsonl_path=ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl",
        csv_path=ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.csv",
        summary_path=ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotation_summary.json",
    )
    print(f"Wrote {result.row_count} model-assisted annotation rows to {result.jsonl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

