"""Run the lightweight validation suite for the benchmark scaffold."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ["python", ".\\experiments\\validate_benchmark_specs.py"],
    ["python", ".\\experiments\\validate_annotations.py"],
    [
        "python",
        ".\\experiments\\validate_annotations.py",
        "--jsonl",
        ".\\benchmark\\annotations\\scaleup_model_assisted_annotations.jsonl",
        "--csv",
        ".\\benchmark\\annotations\\scaleup_model_assisted_annotations.csv",
        "--summary",
        ".\\benchmark\\annotations\\scaleup_model_assisted_annotation_summary.json",
    ],
    ["python", ".\\experiments\\validate_human_audit_batch.py"],
    ["python", ".\\experiments\\validate_model_outputs.py"],
    [
        "python",
        ".\\experiments\\validate_model_outputs.py",
        "--jsonl",
        ".\\results\\frozen_model_outputs\\pilot_florence_grounding.jsonl",
        "--csv",
        ".\\results\\frozen_model_outputs\\pilot_florence_grounding.csv",
    ],
    [
        "python",
        ".\\experiments\\validate_model_outputs.py",
        "--jsonl",
        ".\\results\\frozen_model_outputs\\scaleup_florence_grounding.jsonl",
        "--csv",
        ".\\results\\frozen_model_outputs\\scaleup_florence_grounding.csv",
    ],
    [
        "python",
        ".\\experiments\\validate_model_outputs.py",
        "--jsonl",
        ".\\results\\frozen_model_outputs\\scaleup_caption_keyword.jsonl",
        "--csv",
        ".\\results\\frozen_model_outputs\\scaleup_caption_keyword.csv",
    ],
    [
        "python",
        ".\\experiments\\validate_model_outputs.py",
        "--jsonl",
        ".\\results\\frozen_model_outputs\\scaleup_annotation_bootstrap.jsonl",
        "--csv",
        ".\\results\\frozen_model_outputs\\scaleup_annotation_bootstrap.csv",
    ],
    [
        "python",
        ".\\experiments\\validate_model_outputs.py",
        "--jsonl",
        ".\\results\\frozen_model_outputs\\scaleup_manifest_seed.jsonl",
        "--csv",
        ".\\results\\frozen_model_outputs\\scaleup_manifest_seed.csv",
    ],
    [
        "python",
        ".\\experiments\\validate_model_outputs.py",
        "--jsonl",
        ".\\results\\frozen_model_outputs\\scaleup_majority_violation.jsonl",
        "--csv",
        ".\\results\\frozen_model_outputs\\scaleup_majority_violation.csv",
    ],
    ["python", ".\\experiments\\validate_intervention_outputs.py"],
    ["python", ".\\experiments\\validate_phase4_outputs.py"],
    ["python", ".\\experiments\\validate_paper_scaffold.py"],
    ["python", ".\\experiments\\validate_scaleup_manifest.py"],
    ["python", "-m", "pytest", ".\\analysis\\tests", ".\\tests", "-q"],
]


def main() -> int:
    for command in COMMANDS:
        print(f"> {' '.join(command)}")
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode
    print("All lightweight validations passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
