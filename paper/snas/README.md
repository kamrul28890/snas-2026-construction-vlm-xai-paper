# SNAS 2026 FaithBench Submission Package

This folder contains the SNAS-formatted version of the current ConstructionSafety-FaithBench paper.

Primary files:

- `SNAS_2026_FaithBench_short_paper.tex` (SNAS format: Times New Roman, 12 pt,
  double-spaced, APA references; build with XeLaTeX). **This is the source of
  truth for all prose.**
- `SNAS_2026_FaithBench_camera_ready_ieee.tex` (IEEE two-column camera-ready
  variant, same content and numbers; build with pdfLaTeX). **Generated file.**
  Edit the SNAS manuscript and run `python experiments/build_ieee_variant.py`;
  direct edits here are overwritten.
- `SNAS_2026_FaithBench_abstract_blind.tex` (standalone abstract; text must stay
  identical to the abstract in both manuscripts)
- `SUBMISSION_TEXTS.md`
- `SUBMISSION_RISKS_AND_FIXES.md`
- `figures/`

Build command from the repository root:

```powershell
$out = (Resolve-Path .\tmp\snas).Path
Push-Location .\paper\snas
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_short_paper.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_short_paper.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_abstract_blind.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_abstract_blind.tex
pdflatex -interaction=nonstopmode -output-directory $out .\SNAS_2026_FaithBench_camera_ready_ieee.tex
pdflatex -interaction=nonstopmode -output-directory $out .\SNAS_2026_FaithBench_camera_ready_ieee.tex
pdflatex -interaction=nonstopmode -output-directory $out .\SNAS_2026_FaithBench_camera_ready_ieee.tex
Pop-Location
```

The review-safe abstract intentionally omits the GitHub URL because SNAS uses double-blind review.
