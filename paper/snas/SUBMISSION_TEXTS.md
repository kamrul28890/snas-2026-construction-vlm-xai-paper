# SNAS 2026 Submission Texts

## Title

ConstructionSafety-FaithBench: Evaluating Visual-Evidence Sensitivity in Construction-Safety Vision-Language Systems

## Camera-Ready Abstract (current, 227 words)

This matches the abstract in `SNAS_2026_FaithBench_short_paper.tex` and
`SNAS_2026_FaithBench_abstract_blind.tex`. Update all three together.

Construction safety depends on small, rule-specific visual details: a hard hat on a particular worker, a barrier at a particular edge. Vision-language models (VLMs) are increasingly proposed to check such details automatically, but can give the right safety answer for the wrong visual reason, judging a scene unsafe because construction sites look hazardous while ignoring the cue the rule concerns. Existing evaluations report answer accuracy and are silent on this failure. We introduce ConstructionSafety-FaithBench, a model-agnostic audit benchmark separating three properties usually merged into one score: whether the answer is correct, whether the cited evidence is rule-relevant, and whether the answer changes when that evidence is removed, the last probed by occluding the rule-relevant region and comparing against size-matched occlusions elsewhere, so any difference reflects location rather than amount. Validated on an open-vocabulary grounding pipeline built on Florence-2 across four construction rule families, the three come apart: 18.3% accuracy on 120 adjudicated hard cases, an evidence region on 98.8% of images yet overlapping the rule-relevant one at mean intersection-over-union 0.058, and answers flipping 39.2% of the time under targeted occlusion against 9.2% under matched controls, with "uncertain" never once returned. These findings characterize one pipeline rather than VLMs in general, but indicate that answer accuracy is insufficient evidence of trustworthiness for safety-critical screening, and that a system's willingness to abstain deserves scrutiny alongside its accuracy. Artifacts: https://github.com/kamrul28890/snas-2026-construction-safety-faithbench.

## Repository Link

https://github.com/kamrul28890/snas-2026-construction-safety-faithbench

Now stated in the paper's Reproducibility Statement, so it no longer needs to be
appended to the abstract.

## Keywords

trustworthy AI; explainable AI; vision-language models; construction safety; evidence faithfulness; AI risk assessment

## EasyChair Topic Fit

Trustworthy AI and responsible innovation; transparency, explainability, and accountability in intelligent systems; AI risk assessment, safety, and resilience; human-centered intelligent systems.

## Suggested Short Submission Note

This double-blind short paper reports a compact reproducible audit study of evidence faithfulness in construction-safety vision-language models. The paper is formatted as a 4-8 page SNAS short paper, excluding references, and all identifying author information has been removed from the review PDF metadata.
