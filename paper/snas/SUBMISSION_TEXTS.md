# SNAS 2026 Submission Texts

## Title

ConstructionSafety-FaithBench: Auditing Visual-Evidence Faithfulness in Construction-Safety Vision-Language Models

## Double-Blind Abstract for EasyChair

Construction-safety vision-language models (VLMs) are being explored as tools for reviewing site imagery, but standard evaluation usually asks only whether the final answer or rationale sounds correct. This leaves a critical gap: a model may predict a safety violation while grounding on irrelevant scene context, or keep the same answer after the rule-relevant worker, protective equipment, or hazard region is removed. We address this gap with ConstructionSafety-FaithBench, a reproducible audit pipeline that separates answer correctness, visual evidence localization, and counterfactual sensitivity. The artifact contains 163 pilot image-rule pairs, 588 scale-up candidates, four safety-rule families, deterministic baselines, a Florence-2 grounding adapter, 948 targeted and matched-random occlusion runs, and a 120-row final audit-label layer. The audit set prioritizes Florence/bootstrap disagreements and weak evidence overlap. Against final audit labels, Florence grounding reaches 18.3% accuracy and 12.5% macro-F1, while a metadata-assisted bootstrap reaches 78.3% accuracy, showing that scaffold-level labels can mask visually grounded failure. Targeted evidence occlusion changes Florence answers 39.2% of the time versus 9.2% for matched random masks, a paired gap of 30.0 percentage points. The final audit labels combine 108 role-conditioned A/B consensus rows with 12 returned adjudication decisions, so results are reported with explicit provenance rather than as unqualified human ground truth.

## Public/Post-Review Abstract With Repository Link

Construction-safety vision-language models (VLMs) are being explored as tools for reviewing site imagery, but standard evaluation usually asks only whether the final answer or rationale sounds correct. This leaves a critical gap: a model may predict a safety violation while grounding on irrelevant scene context, or keep the same answer after the rule-relevant worker, protective equipment, or hazard region is removed. We address this gap with ConstructionSafety-FaithBench, a reproducible audit pipeline that separates answer correctness, visual evidence localization, and counterfactual sensitivity. The artifact contains 163 pilot image-rule pairs, 588 scale-up candidates, four safety-rule families, deterministic baselines, a Florence-2 grounding adapter, 948 targeted and matched-random occlusion runs, and a 120-row final audit-label layer. The audit set prioritizes Florence/bootstrap disagreements and weak evidence overlap. Against final audit labels, Florence grounding reaches 18.3% accuracy and 12.5% macro-F1, while a metadata-assisted bootstrap reaches 78.3% accuracy, showing that scaffold-level labels can mask visually grounded failure. Targeted evidence occlusion changes Florence answers 39.2% of the time versus 9.2% for matched random masks, a paired gap of 30.0 percentage points. The final audit labels combine 108 role-conditioned A/B consensus rows with 12 returned adjudication decisions, so results are reported with explicit provenance rather than as unqualified human ground truth. Reproducibility repository: https://github.com/kamrul28890/snas-2026-construction-safety-faithbench

## Keywords

trustworthy AI; explainable AI; vision-language models; construction safety; evidence faithfulness; AI risk assessment

## EasyChair Topic Fit

Trustworthy AI and responsible innovation; transparency, explainability, and accountability in intelligent systems; AI risk assessment, safety, and resilience; human-centered intelligent systems.

## Suggested Short Submission Note

This double-blind short paper reports a compact reproducible audit study of evidence faithfulness in construction-safety vision-language models. The paper is formatted as a 4-8 page SNAS short paper, excluding references, and all identifying author information has been removed from the review PDF metadata.
