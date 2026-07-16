# SNAS Paper Analysis

This directory owns the paper-specific protocol, matched-control experiment,
statistics, tables, and figures. The construction-safety XAI repository is read
only; new outputs are written under `analysis/outputs/` and `figures/` here.

## Environment

Use the XAI pilot virtual environment because it contains the validated CUDA
build and the installed `xai_pilot` dependencies.

## Run

```powershell
$python = '..\Explainable-AI-Mustafa-Abdallah\pilot\.venv\Scripts\python.exe'
& $python .\analysis\run_matched_random_occlusion.py
& $python .\analysis\generate_paper_results.py
```

The intervention runner is resumable. Pass `--force` only when intentionally
discarding and recomputing its paper-owned outputs.

## Protocol

`protocol.json` freezes the analysis unit, thresholds, seeds, statistical tests,
claim boundaries, and matched-control construction used in the paper.
