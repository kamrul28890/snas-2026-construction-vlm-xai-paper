"""Build the pilot benchmark manifest and annotation templates."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.manifest import build_pilot_manifest
from faithbench.schema import load_rules


def main() -> int:
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    result = build_pilot_manifest(
        sample_audit_path=ROOT / "analysis" / "outputs" / "sample_audit.csv",
        dataset_summary_path=ROOT / "analysis" / "outputs" / "dataset_summary.csv",
        rules=rules,
        manifest_path=ROOT / "benchmark" / "splits" / "pilot_manifest.csv",
        annotation_jsonl_path=ROOT / "benchmark" / "annotations" / "pilot_annotation_template.jsonl",
        annotation_csv_path=ROOT / "benchmark" / "annotations" / "pilot_annotation_template.csv",
        summary_path=ROOT / "benchmark" / "splits" / "pilot_manifest_summary.json",
    )
    print(f"Wrote {result.row_count} manifest rows to {result.manifest_path}")
    print(f"Wrote {result.annotation_count} annotation rows to {result.annotation_jsonl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

