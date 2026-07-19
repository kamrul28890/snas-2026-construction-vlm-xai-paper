"""Build frozen pilot intervention specifications from the benchmark manifest."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.interventions import (
    build_intervention_specs_from_manifest,
    load_manifest_rows,
    write_intervention_specs,
)


def main() -> int:
    manifest_path = ROOT / "benchmark" / "splits" / "pilot_manifest.csv"
    specs = build_intervention_specs_from_manifest(
        load_manifest_rows(manifest_path),
        random_seeds=[42, 43, 44, 45, 46],
    )
    jsonl_path = ROOT / "benchmark" / "interventions" / "pilot_interventions.jsonl"
    csv_path = ROOT / "benchmark" / "interventions" / "pilot_interventions.csv"
    write_intervention_specs(specs, jsonl_path=jsonl_path, csv_path=csv_path)
    counts: dict[str, int] = {}
    for spec in specs:
        counts[spec.intervention_type] = counts.get(spec.intervention_type, 0) + 1
    summary = {
        "intervention_spec_version": "0.1.0-pilot",
        "source_manifest": str(manifest_path),
        "row_count": len(specs),
        "counts": counts,
        "random_seeds": [42, 43, 44, 45, 46],
        "max_target_iou": 0.05,
    }
    summary_path = ROOT / "benchmark" / "interventions" / "pilot_interventions_summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    print(f"Wrote {len(specs)} intervention specs to {jsonl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

