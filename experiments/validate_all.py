"""Run the lightweight validation suite for the benchmark scaffold."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ["python", ".\\experiments\\validate_benchmark_specs.py"],
    ["python", ".\\experiments\\validate_annotations.py"],
    ["python", ".\\experiments\\validate_model_outputs.py"],
    ["python", ".\\experiments\\validate_phase4_outputs.py"],
    ["python", ".\\experiments\\validate_paper_scaffold.py"],
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

