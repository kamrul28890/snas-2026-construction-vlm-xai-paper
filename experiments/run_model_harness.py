"""Run a built-in model adapter over the pilot benchmark manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.model_harness import adapter_by_name, load_model_inputs, run_adapter, write_model_outputs
from faithbench.schema import load_rules


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--adapter",
        choices=["majority_violation", "manifest_seed", "annotation_bootstrap", "caption_keyword"],
        default="annotation_bootstrap",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "frozen_model_outputs",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "benchmark" / "splits" / "pilot_manifest.csv",
    )
    parser.add_argument(
        "--annotations",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl",
    )
    parser.add_argument("--output-stem", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    rules_by_id = {rule.rule_id: rule for rule in rules.rules}
    items = load_model_inputs(args.manifest, rules_by_id)
    adapter = adapter_by_name(
        args.adapter,
        annotations_path=args.annotations,
    )
    rows = run_adapter(adapter, items)
    stem = args.output_stem or f"pilot_{args.adapter}"
    jsonl_path = args.output_dir / f"{stem}.jsonl"
    csv_path = args.output_dir / f"{stem}.csv"
    write_model_outputs(rows, jsonl_path=jsonl_path, csv_path=csv_path)
    summary = {
        "adapter": args.adapter,
        "model_id": rows[0]["model_id"] if rows else "",
        "prompt_id": rows[0]["prompt_id"] if rows else "",
        "row_count": len(rows),
        "jsonl_path": str(jsonl_path),
        "csv_path": str(csv_path),
        "answer_counts": {},
        "provenance": rows[0]["provenance"] if rows else "",
    }
    for row in rows:
        answer = row["answer"]
        summary["answer_counts"][answer] = summary["answer_counts"].get(answer, 0) + 1
    summary_path = args.output_dir / f"{stem}_summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    print(f"Wrote {len(rows)} model-output rows to {jsonl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
