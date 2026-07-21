# SNAS 2026 Submission Texts

## Title

ConstructionSafety-FaithBench: Auditing Visual-Evidence Faithfulness in Construction-Safety Vision-Language Models

## Double-Blind Abstract for EasyChair

Construction-safety vision-language models (VLMs) are often evaluated by final answers or plausible rationales, but neither shows whether the model used rule-relevant visual evidence. This paper presents ConstructionSafety-FaithBench, a compact audit benchmark for trustworthy construction-safety AI. Each example pairs a site image with a safety rule, answer label, evidence regions, and provenance fields. The current artifact includes 163 pilot image-rule pairs, 588 scale-up candidates, four safety-rule families, deterministic baselines, a Florence-2 grounding adapter, 948 targeted and matched-random occlusion runs, and a 120-row final audit-label layer. The audit set is intentionally difficult: it prioritizes Florence/bootstrap disagreements and weak evidence overlap. On this set, Florence grounding reaches only 18.3% answer accuracy, while a metadata-assisted bootstrap reaches 78.3%, showing that scaffold-level validation can hide visually grounded failures. Targeted evidence occlusion changes Florence answers 39.2% of the time versus 9.2% for matched random masks, with a paired answer-flip gap of 30.0 percentage points. The final audit labels combine 108 role-conditioned A/B consensus rows with 12 returned adjudication decisions, so results are reported with explicit provenance rather than as unqualified human ground truth. The contribution is a reproducible measurement pipeline for evidence faithfulness, not an autonomous inspection system.

## Public/Post-Review Abstract With Repository Link

Construction-safety vision-language models (VLMs) are often evaluated by final answers or plausible rationales, but neither shows whether the model used rule-relevant visual evidence. This paper presents ConstructionSafety-FaithBench, a compact audit benchmark for trustworthy construction-safety AI. Each example pairs a site image with a safety rule, answer label, evidence regions, and provenance fields. The current artifact includes 163 pilot image-rule pairs, 588 scale-up candidates, four safety-rule families, deterministic baselines, a Florence-2 grounding adapter, 948 targeted and matched-random occlusion runs, and a 120-row final audit-label layer. The audit set is intentionally difficult: it prioritizes Florence/bootstrap disagreements and weak evidence overlap. On this set, Florence grounding reaches only 18.3% answer accuracy, while a metadata-assisted bootstrap reaches 78.3%, showing that scaffold-level validation can hide visually grounded failures. Targeted evidence occlusion changes Florence answers 39.2% of the time versus 9.2% for matched random masks, with a paired answer-flip gap of 30.0 percentage points. The final audit labels combine 108 role-conditioned A/B consensus rows with 12 returned adjudication decisions, so results are reported with explicit provenance rather than as unqualified human ground truth. The contribution is a reproducible measurement pipeline for evidence faithfulness, not an autonomous inspection system. Reproducibility repository: https://github.com/kamrul28890/snas-2026-construction-safety-faithbench

## Keywords

trustworthy AI; explainable AI; vision-language models; construction safety; evidence faithfulness; AI risk assessment

## EasyChair Topic Fit

Trustworthy AI and responsible innovation; transparency, explainability, and accountability in intelligent systems; AI risk assessment, safety, and resilience; human-centered intelligent systems.

## Suggested Short Submission Note

This double-blind short paper reports a compact reproducible audit study of evidence faithfulness in construction-safety vision-language models. The paper is formatted as a 4-8 page SNAS short paper, excluding references, and all identifying author information has been removed from the review PDF metadata.
