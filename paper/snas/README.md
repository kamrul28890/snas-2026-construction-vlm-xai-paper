# SNAS 2026 FaithBench Submission Package

This folder contains the camera-ready version of the ConstructionSafety-FaithBench
paper, formatted with the official SNAS 2026 LaTeX template (`SNAS_main.tex`,
distributed by the program committee on 2026-09-15).

Primary files:

- `SNAS_2026_FaithBench_short_paper.tex` (official SNAS template: single column,
  12 pt, letter, 1 in margins, `newtxtext`, `\onehalfspacing`, APA via
  `apacite`; build with pdfLaTeX plus a BibTeX pass). **This is the source of
  truth for all prose.**
- `references.bib` (APA reference list consumed by `apacite`)
- `SNAS_2026_FaithBench_abstract_blind.tex` (standalone abstract; text must stay
  identical to the abstract in the manuscript. The `_blind` name is historical
  and this file still uses fontspec, so it alone needs XeLaTeX.)
- `SUBMISSION_TEXTS.md`
- `SUBMISSION_RISKS_AND_FIXES.md`
- `figures/`

Build both PDFs with `build_latex.ps1` from the repository root, or by hand:

```powershell
$out = (Resolve-Path .\tmp\snas).Path
Push-Location .\paper\snas
$env:BIBINPUTS = "$((Get-Location).Path);"
pdflatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_short_paper.tex
bibtex (Join-Path $out 'SNAS_2026_FaithBench_short_paper')
pdflatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_short_paper.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_short_paper.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_abstract_blind.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_abstract_blind.tex
Pop-Location
```

The BibTeX pass is what resolves the `\citep` keys and builds the reference list;
skipping it leaves question marks in place of every citation.

The standalone abstract omits the GitHub URL, which dates from double-blind
review. The paper itself is non-blind and carries the link deliberately.
