# ConstructionSafety-FaithBench SNAS 2026 Package

This repository contains the working materials for the SNAS 2026 short-paper
submission:

**ConstructionSafety-FaithBench: Auditing Visual-Evidence Faithfulness in
Construction-Safety Vision-Language Models**

The paper studies whether a construction-safety vision-language pipeline uses
rule-relevant visual evidence, rather than only producing plausible final
answers. It includes manifests, safety-rule prompts, model-output schemas,
Florence-2 grounding outputs, targeted and matched-random visual interventions,
audit labels with explicit provenance, scoring scripts, result tables, generated
figures, and SNAS-ready manuscript files.

## Submission Files

- Blind short-paper PDF:
  `output/snas_submission_ready/SNAS_2026_FaithBench_short_paper_blind.pdf`
- Blind standalone abstract PDF:
  `output/snas_submission_ready/SNAS_2026_FaithBench_abstract_blind.pdf`
- Copy-paste submission text:
  `paper/snas/SUBMISSION_TEXTS.md`
- Submission risks and final checks:
  `paper/snas/SUBMISSION_RISKS_AND_FIXES.md`
- Clean reproducibility export:
  `output/snas_submission_ready/reproducibility_repo/`
- Zip package:
  `output/snas_submission_ready/SNAS_2026_FaithBench_submission_package.zip`

The review PDFs are double-blind. Author names, affiliations, and a public
repository link should be entered only where SNAS/EasyChair allows them.

## Current Results

- 163 pilot image-rule pairs and 588 scale-up candidate pairs.
- Four safety-rule families: PPE hard-hat compliance, fall harness protection,
  guardrail/edge protection, and struck-by/equipment proximity.
- 120-row final audit-label layer: 108 A/B consensus rows plus 12 returned
  adjudication decisions.
- Florence grounding accuracy on the audit layer: 18.3%.
- Metadata-assisted bootstrap accuracy on the audit layer: 78.3%.
- Targeted evidence occlusion answer flip rate: 39.2%.
- Matched-random answer flip rate: 9.2%.
- Paired answer-flip difference: 30.0 percentage points.

These numbers support a measurement claim about visual-evidence faithfulness.
They do not establish deployment readiness or recover a model's internal
reasoning.

## Annotation Provenance

The final audit labels must not be described as unqualified human ground truth.
The safe submission wording is:

`two independent role-conditioned audit passes plus returned adjudication`

or:

`adjudicated audit labels with AI-pass provenance`

The stronger claim that two actual human annotators labeled all rows would
require a new independent human/domain audit and replacement labels.

## Rebuild

From the repository root:

```powershell
python .\experiments\make_paper_figures.py --output-dir .\paper\snas\figures
$out = (Resolve-Path .\tmp\snas).Path
Push-Location .\paper\snas
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_short_paper.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_short_paper.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_abstract_blind.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory $out .\SNAS_2026_FaithBench_abstract_blind.tex
Pop-Location
python .\experiments\create_snas_submission_package.py
```

Run the lightweight checks:

```powershell
python .\experiments\validate_all.py
```

Raw dataset images and model weights are not redistributed in this repository.
