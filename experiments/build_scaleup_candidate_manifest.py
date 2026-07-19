"""Build a larger candidate manifest from the ConstructionSite test split."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.scaleup import CLASS_PRIORITY, select_scaleup_candidates, write_scaleup_manifest
from faithbench.schema import load_rules


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-class", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20_260_719)
    parser.add_argument("--max-scan", type=int, default=10_000)
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=ROOT.parent / "Explainable-AI-Mustafa-Abdallah",
    )
    return parser.parse_args()


def load_candidate_source_rows(source_repo: Path, *, per_class: int, max_scan: int) -> tuple[list[dict], int]:
    source_module = source_repo / "pilot" / "src"
    if not source_module.is_dir():
        raise FileNotFoundError(f"XAI pilot source not found: {source_module}")
    sys.path.insert(0, str(source_module))
    from xai_pilot.data import classify_image, load_construction_site

    rows = []
    counts = {label: 0 for label in CLASS_PRIORITY}
    scanned = 0
    for row in load_construction_site(split="test", streaming=True):
        scanned += 1
        primary_class, _ = classify_image(row)
        if counts.get(primary_class, 0) < per_class:
            rows.append(row)
            counts[primary_class] = counts.get(primary_class, 0) + 1
        if all(counts[label] >= per_class for label in CLASS_PRIORITY):
            break
        if scanned >= max_scan:
            break
    return rows, scanned


def main() -> int:
    args = parse_args()
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    source_rows, scanned = load_candidate_source_rows(
        args.source_repo.resolve(),
        per_class=args.per_class,
        max_scan=args.max_scan,
    )
    manifest_rows = select_scaleup_candidates(
        source_rows,
        rules=rules,
        per_class=args.per_class,
        seed=args.seed,
    )
    result = write_scaleup_manifest(
        manifest_rows,
        manifest_path=ROOT / "benchmark" / "splits" / "scaleup_candidate_manifest.csv",
        summary_path=ROOT / "benchmark" / "splits" / "scaleup_candidate_manifest_summary.json",
        source_rows_scanned=scanned,
        per_class=args.per_class,
        seed=args.seed,
    )
    print(f"Wrote {result.row_count} scale-up candidate rows to {result.manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

