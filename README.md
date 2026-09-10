# ConstructionSafety-FaithBench

An audit benchmark for measuring whether construction-safety vision-language
models (VLMs) actually use the visual evidence their safety verdicts depend on.

This repository accompanies the SNAS 2026 short paper *ConstructionSafety-FaithBench:
Auditing Visual-Evidence Faithfulness in Construction-Safety Vision-Language Models*.

## Overview

A construction-safety VLM can produce the right answer for the wrong visual
reason: judging a scene unsafe because construction sites look hazardous, while
ignoring the specific hard hat, harness, edge, or machine-proximity cue the
safety rule concerns. Reporting answer accuracy alone cannot detect this.

FaithBench separates three properties that are usually merged into one score:

| Property | Question | How it is measured |
| --- | --- | --- |
| Correctness | Is the verdict right? | Accuracy, macro-F1 against adjudicated audit labels |
| Grounding | Does the cited region match the rule's object? | Evidence presence, IoU with the reference region |
| Faithfulness | Does the verdict depend on that region? | Answer-flip rate under targeted vs. size-matched random occlusion |

The faithfulness test is causal. For every targeted occlusion of a rule-relevant
region, five occlusions of identical width and height are placed elsewhere in the
same image. Because the number of occluded pixels is held constant, any
difference between conditions reflects *where* pixels were removed, not how many.

## Motivation

Safety screening is not ordinary visual question answering. A wrong caption is an
inconvenience; a missed fall-protection violation can precede a fatal fall, and a
confidently reported hazard that is not there erodes the trust that makes the
tool usable. A system that supplies a confident verdict alongside a plausible but
unscored bounding box provides the visual trappings of justification without the
substance, which is the failure mode this benchmark is built to expose.

## Repository layout

```
benchmark/     Manifests, safety-rule schema, annotations, intervention specs
src/faithbench/  Library: manifests, adapters, scoring, interventions, metrics
experiments/   Runnable scripts: build, score, validate, figures, packaging
analysis/      Statistical analysis, protocol.json, generated result artifacts
results/       Frozen model outputs and generated score tables
paper/snas/    LaTeX sources for the manuscript (SNAS and IEEE formats)
figures/       Generated publication figures
tests/         Unit tests for schema and specification invariants
```

## Installation

Requires Python 3.10 or newer.

```bash
git clone https://github.com/kamrul28890/snas-2026-construction-safety-faithbench.git
cd snas-2026-construction-safety-faithbench
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The core scoring and analysis path depends only on the Python standard library
plus `matplotlib` (figures) and `pytest` (tests). Re-running Florence-2 inference
additionally requires `torch` and `transformers`, which are intentionally not
pinned here so that the analysis pipeline can be reproduced without a GPU.

## Data availability

Benchmark **metadata** is included: manifests, rule definitions, evidence-box
coordinates, model outputs, audit labels, and score tables.

Source **images are not redistributed**. They derive from the ConstructionSite
collection (`LouisChen15/ConstructionSite`, revision
`ca3d9b885b45cbec956817edc42253664c7faf3f`), which is licensed **CC BY-NC 4.0**,
so any downstream use must respect that non-commercial term. The scripts load
images only when a local copy of that dataset is already available. Model weights
are likewise not redistributed; the evaluated model is
`microsoft/Florence-2-base-ft` at revision
`f6c1a25888ffc1d945ee8a1a77ac833c7303d46e`.

Every reported number in the paper can be recomputed from the included artifacts
without image access; only re-running inference from scratch requires the images.
Full frozen-input provenance, including SHA-256 hashes for every source file, is
in `SNAS_2026_reproducibility_README.md`.

## Reproducing the results

Verify the shipped artifacts and run the test suites:

```bash
python experiments/validate_all.py
```

Regenerate the statistical analysis, result tables, and publication figures:

```bash
python analysis/generate_paper_results.py
python experiments/make_paper_figures.py --output-dir paper/snas/figures
```

Regenerate the analyses that support the control and error discussion in the
paper:

```bash
# occlusion size match, target overlap, and control degeneracy on large targets;
# also repeats the primary comparison with degenerate-control images excluded
python experiments/analyze_mask_characteristics.py

# confusion matrix over the reference labels, separating missed violations
# from false alarms
python experiments/analyze_error_asymmetry.py
```

These write `results/tables/mask_characteristics.csv`,
`results/tables/control_robustness.csv`, and `results/tables/error_asymmetry.csv`,
which are the sources for the corresponding numbers in the manuscript.

## Manuscript

The SNAS-format manuscript is the single source of truth for prose. The IEEE
two-column variant is generated from it, so edit the former and regenerate:

```bash
python experiments/build_ieee_variant.py
```

Direct edits to `SNAS_2026_FaithBench_camera_ready_ieee.tex` are overwritten. The
title and abstract also appear in the standalone abstract and in
`SUBMISSION_TEXTS.md`; `experiments/validate_manuscript_consistency.py`, part of
`validate_all.py`, fails if those copies drift apart or if the abstract exceeds
the venue word limit.

Build the PDFs with `build_latex.ps1`.

Before publishing or sharing the repository, strip machine-specific paths from
generated summaries:

```bash
python experiments/sanitize_release_paths.py --check   # report only
python experiments/sanitize_release_paths.py           # rewrite in place
```

## What was evaluated

| Adapter | Role | Why included |
| --- | --- | --- |
| `microsoft/Florence-2-base-ft` + grounding adapter | System under audit | Open-vocabulary grounding lets a written rule be queried directly; small enough to re-run for the intervention study |
| Metadata-assisted bootstrap | Reference annotation | Scales labelling and supports triage; partly circular by construction, so not treated as ground truth |
| Manifest seed | Blind reference point | Echoes the stored label, exposing how much of the annotation is circular |
| Majority violation | Blind reference point | Always answers "violation", establishing the class-imbalance floor |
| Caption keyword | Blind reference point | Reads captions only, never pixels, testing whether labels leak from text |

The grounding adapter converts Florence-2's boxes into a verdict using fixed
geometric tests with no learned parameters, so a failure is traceable to either
the grounding step or the rule logic rather than hidden inside a second model.

## Example

A single benchmark row pairs one image with one safety rule:

```
image_id:    0000007
rule_id:     ppe_hard_hat
target_box:  [982, 225, 1199, 406]     # the head region the rule depends on
expected:    violation
```

The audited pipeline returns:

```json
{
  "image_id": "0000007",
  "rule_id": "ppe_hard_hat",
  "answer": "compliant",
  "evidence_regions_xyxy": "[[982,225,1199,406]]",
  "evidence_objects": "[\"worker\",\"head_protection\",\"hard_hat\"]"
}
```

This row illustrates the problem the benchmark exists to measure. The cited
evidence region is *exactly* the rule-relevant box, so any grounding score would
call this a success, yet the verdict is wrong. Correct localization did not
produce a correct rule judgment.

## Headline results

Auditing the Florence-2 grounding pipeline across four rule families:

| Measure | Value |
| --- | --- |
| Accuracy on 120 adjudicated hard cases | 18.3% |
| Macro-F1 on the same set | 12.5% |
| Evidence returned (scale-up split) | 98.8% |
| Mean best evidence IoU (scale-up split) | 0.058 |
| Answer-flip rate, targeted occlusion | 39.2% |
| Answer-flip rate, size-matched random occlusion | 9.2% |
| Paired difference | 30.0 points (95% CI 22.3–37.7) |
| Paired centroid-drift difference | 0.166 (95% CI 0.140–0.193) |
| Rows answered "uncertain" | 0 of 120 |

The three properties dissociate. The pipeline is often wrong, usually points
somewhere unhelpful, and is nonetheless measurably sensitive to the right pixels.
Any one measured alone would misrepresent it.

## Label provenance

The 120-row audit layer was produced by **two independent AI annotation passes
working from a written protocol, plus returned adjudication** of the 12
disagreements. These are *not* human domain-expert labels and must not be cited
as such. Replacing this layer with certified construction-safety professionals is
the most important outstanding improvement to this work.

## Intended use and limitations

This is a research evaluation artifact. It is **not** validated for deployment,
and it must not be used for autonomous safety inspection, disciplinary
monitoring, or surveillance. It does not infer worker identity, intent,
competence, or blame. The documented failure modes fall hardest on missed
violations, so using such a system without human review would shift risk onto
workers while appearing to provide oversight.

Further limitations, including single-model coverage, single-source imagery,
static frames, and synthetic occlusions, are documented in the paper.

## Citation

```bibtex
@inproceedings{kamruzzaman2026faithbench,
  title     = {ConstructionSafety-FaithBench: Auditing Visual-Evidence Faithfulness
               in Construction-Safety Vision-Language Models},
  author    = {Kamruzzaman, Md and Jahan, Eashraque and Abdallah, Mustafa},
  booktitle = {Proceedings of the 5th SNAS Interdisciplinary Research Conference},
  year      = {2026}
}
```
