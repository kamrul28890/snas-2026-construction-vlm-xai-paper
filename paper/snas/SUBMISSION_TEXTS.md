# SNAS 2026 Submission Texts

## Title

ConstructionSafety-FaithBench: Auditing Visual-Evidence Faithfulness in Construction-Safety Vision-Language Models

## Double-Blind Abstract for EasyChair

Construction-safety vision-language models (VLMs) can produce the right safety answer for the wrong visual reason. A model may classify a scene as unsafe because construction context looks hazardous, while ignoring the specific worker, protective equipment, edge, or machine-proximity cue that the safety rule actually depends on. We introduce ConstructionSafety-FaithBench to audit this right-answer/wrong-evidence gap. The benchmark separates three questions that are usually merged: whether the answer is correct, whether the cited visual evidence is rule-relevant, and whether the answer changes when that evidence is removed. We evaluate automated baseline annotations and a Florence-2 grounding adapter on hard-hat, fall-protection, guardrail, and struck-by rules, then apply targeted occlusions to rule-relevant boxes and compare them with same-size random masks. On a prioritized audit set where Florence-2 often disagrees with the automated baseline, Florence reaches 18.3% accuracy and 12.5% macro-F1, while the baseline reaches 78.3% accuracy. More importantly, masking rule-relevant evidence changes Florence answers 39.2% of the time, compared with 9.2% for matched random masks. These results show that construction-safety VLM evaluation needs evidence-faithfulness tests, not answer scoring alone.

## Public/Post-Review Abstract With Repository Link

Construction-safety vision-language models (VLMs) can produce the right safety answer for the wrong visual reason. A model may classify a scene as unsafe because construction context looks hazardous, while ignoring the specific worker, protective equipment, edge, or machine-proximity cue that the safety rule actually depends on. We introduce ConstructionSafety-FaithBench to audit this right-answer/wrong-evidence gap. The benchmark separates three questions that are usually merged: whether the answer is correct, whether the cited visual evidence is rule-relevant, and whether the answer changes when that evidence is removed. We evaluate automated baseline annotations and a Florence-2 grounding adapter on hard-hat, fall-protection, guardrail, and struck-by rules, then apply targeted occlusions to rule-relevant boxes and compare them with same-size random masks. On a prioritized audit set where Florence-2 often disagrees with the automated baseline, Florence reaches 18.3% accuracy and 12.5% macro-F1, while the baseline reaches 78.3% accuracy. More importantly, masking rule-relevant evidence changes Florence answers 39.2% of the time, compared with 9.2% for matched random masks. These results show that construction-safety VLM evaluation needs evidence-faithfulness tests, not answer scoring alone. Reproducibility repository: https://github.com/kamrul28890/snas-2026-construction-safety-faithbench

## Keywords

trustworthy AI; explainable AI; vision-language models; construction safety; evidence faithfulness; AI risk assessment

## EasyChair Topic Fit

Trustworthy AI and responsible innovation; transparency, explainability, and accountability in intelligent systems; AI risk assessment, safety, and resilience; human-centered intelligent systems.

## Suggested Short Submission Note

This double-blind short paper reports a compact reproducible audit study of evidence faithfulness in construction-safety vision-language models. The paper is formatted as a 4-8 page SNAS short paper, excluding references, and all identifying author information has been removed from the review PDF metadata.
