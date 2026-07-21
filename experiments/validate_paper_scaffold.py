"""Validate the NeurIPS paper scaffold."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    paper_root = ROOT / "paper" / "neurips"
    required = [
        paper_root / "README.md",
        paper_root / "main.tex",
        paper_root / "references.bib",
        paper_root / "sections" / "01_introduction.tex",
        paper_root / "sections" / "02_related_work.tex",
        paper_root / "sections" / "03_benchmark.tex",
        paper_root / "sections" / "04_metrics.tex",
        paper_root / "sections" / "05_experiments.tex",
        paper_root / "sections" / "06_results.tex",
        paper_root / "sections" / "07_limitations_ethics.tex",
        paper_root / "appendix.tex",
        paper_root / "tables" / "pilot_baseline_scores.tex",
        paper_root / "tables" / "pilot_intervention_counts.tex",
        paper_root / "tables" / "scaleup_baseline_scores.tex",
        paper_root / "tables" / "scaleup_candidate_counts.tex",
        paper_root / "tables" / "pilot_intervention_effects.tex",
        paper_root / "tables" / "scaleup_florence_rule_slices.tex",
        paper_root / "tables" / "human_audit_final_scores.tex",
        paper_root / "figures" / "pipeline_architecture.pdf",
        paper_root / "figures" / "audit_result_dashboard.pdf",
        paper_root / "figures" / "intervention_effects_chart.pdf",
        paper_root / "figures" / "scaleup_rule_slice_chart.pdf",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing paper scaffold files: {missing}")
    main_text = (paper_root / "main.tex").read_text(encoding="utf-8")
    if "human ground truth" not in main_text:
        raise RuntimeError("main.tex must explicitly distinguish bootstrap annotations from human ground truth")
    if "ConstructionSafety-FaithBench" not in main_text:
        raise RuntimeError("main.tex missing benchmark name")
    print("Validated NeurIPS paper scaffold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
