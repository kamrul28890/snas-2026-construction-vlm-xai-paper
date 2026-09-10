# SNAS 2026 Submission Texts

## Title

ConstructionSafety-FaithBench: Auditing Visual-Evidence Faithfulness in Construction-Safety Vision-Language Models

## Camera-Ready Abstract (current, 259 words)

This matches the abstract in `SNAS_2026_FaithBench_short_paper.tex` and
`SNAS_2026_FaithBench_camera_ready_ieee.tex`. Update all three together.

Construction safety depends on small, rule-specific visual details: a hard hat on a particular worker, a barrier at a particular edge. Vision-language models (VLMs) are increasingly proposed to check such details automatically, but they can produce the right safety answer for the wrong visual reason, judging a scene unsafe because construction sites look hazardous while ignoring the cue the rule actually concerns. Existing evaluations report answer accuracy and are therefore silent on this failure. We introduce ConstructionSafety-FaithBench, an audit benchmark that separates three properties usually merged into one score: whether the answer is correct, whether the cited visual evidence is rule-relevant, and whether the answer actually depends on that evidence. Faithfulness is tested causally, by occluding the rule-relevant region and comparing the effect against occlusions of identical size placed elsewhere in the same image, so that any difference reflects location rather than disruption. Auditing an open-vocabulary grounding pipeline across hard-hat, fall-protection, guardrail, and struck-by rules, we find the three properties come apart. The pipeline reaches 18.3% accuracy on 120 adjudicated hard cases. It returns an evidence region on 98.8% of images, yet those regions overlap the rule-relevant region poorly, with a mean intersection-over-union of 0.058. It nonetheless flips its answer 39.2% of the time under targeted occlusion, against 9.2% under size-matched random occlusion, a paired difference of 30.0 points. It never answers "uncertain," even where a single frame cannot support a decision. These results indicate that answer accuracy is insufficient evidence of trustworthiness for safety-critical visual screening, and that a system's willingness to abstain deserves scrutiny alongside its accuracy.

## Repository Link

https://github.com/kamrul28890/snas-2026-construction-safety-faithbench

Now stated in the paper's Reproducibility Statement, so it no longer needs to be
appended to the abstract. Reproducibility repository: https://github.com/kamrul28890/snas-2026-construction-safety-faithbench

## Keywords

trustworthy AI; explainable AI; vision-language models; construction safety; evidence faithfulness; AI risk assessment

## EasyChair Topic Fit

Trustworthy AI and responsible innovation; transparency, explainability, and accountability in intelligent systems; AI risk assessment, safety, and resilience; human-centered intelligent systems.

## Suggested Short Submission Note

This double-blind short paper reports a compact reproducible audit study of evidence faithfulness in construction-safety vision-language models. The paper is formatted as a 4-8 page SNAS short paper, excluding references, and all identifying author information has been removed from the review PDF metadata.
