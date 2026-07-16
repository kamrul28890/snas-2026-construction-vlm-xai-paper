# SNAS 2026 Reproducibility Bundle

This bundle supports the double-blind submission candidate. It does not contain
raw ConstructionSite 10k images or model weights.

## Frozen Inputs

- Dataset: LouisChen15/ConstructionSite
- Dataset revision: ca3d9b885b45cbec956817edc42253664c7faf3f
- Dataset license: CC BY-NC 4.0
- Model: microsoft/Florence-2-base-ft
- Model revision: f6c1a25888ffc1d945ee8a1a77ac833c7303d46e
- XAI source commit: 84ec95177fab618f7168f4139b06138c700eabab

The artifact manifest records SHA-256 hashes for every source CSV and code input.
Because the source working tree contained local changes, its exact used files
are identified by hashes rather than commit alone.

## Primary Experiment

- Analysis unit: image
- Targeted images: 158
- Same-size controls: five per image
- Total intervention rows: 948
- Exact target/control mask-area equality: verified
- Bootstrap resamples: 10,000
- Paired tests: two-sided Wilcoxon with Holm adjustment

## Headline Results

- Targeted answer change: 39.2%
- Matched-random answer change: 9.2%
- Paired difference: 30.0 percentage points, 95% CI [22.3, 37.7]
- Targeted centroid drift: 0.196
- Matched-random centroid drift: 0.031
- Paired difference: 0.166, 95% CI [0.140, 0.193]

## Commands

Run from the paper workspace with the validated XAI virtual environment:

    $python = '..\Explainable-AI-Mustafa-Abdallah\pilot\.venv\Scripts\python.exe'
    & $python -m pytest .\analysis\tests -q
    & $python .\analysis\run_matched_random_occlusion.py
    & $python .\analysis\generate_paper_results.py
    powershell -ExecutionPolicy Bypass -File .\build_latex.ps1

The intervention runner is resumable. Do not use --force unless intentionally
discarding and recomputing its paper-owned output.
