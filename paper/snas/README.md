# SNAS 2026 FaithBench Submission Package

This folder contains the SNAS-formatted version of the current ConstructionSafety-FaithBench paper.

Primary files:

- `SNAS_2026_FaithBench_short_paper.tex`
- `SNAS_2026_FaithBench_abstract_blind.tex`
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
Pop-Location
```

The review-safe abstract intentionally omits the GitHub URL because SNAS uses double-blind review.
