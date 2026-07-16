# SNAS 2026 Submission Metadata

Status: Double-blind short-paper submission candidate

## EasyChair Fields

Title:

Beyond Stable Answers: Auditing Explanation Faithfulness in a Construction-Safety Vision-Language Pipeline

Submission type:

Short paper for peer review and proceedings consideration

Keywords:

- Explainable artificial intelligence
- Vision-language models
- Construction safety
- Explanation faithfulness
- Robustness
- Trustworthy AI

## Abstract (250 words)

Vision-language models (VLMs) may support construction-safety review, but answer accuracy alone does not show whether a judgment depends on relevant visual evidence. This feasibility and construct-validity study adapts a six-dimensional explainable artificial intelligence evaluation framework to a VLM-grounded construction-safety pipeline. Florence-2-base-ft grounded workers and rule-relevant objects in 163 held-out ConstructionSite 10k images; deterministic person-relative geometry then produced the safety verdict. The pipeline was not native free-form visual question answering. Explanations were audited through semantic region ranking, safety-object masking, worker-loss correction, and paired targeted-versus-control interventions. The primary control placed five seeded black rectangles per image, each exactly matching the targeted object's clipped width and height. Area ranking selected the worker instead of the safety object in 50.3% of usable cases; rule-aware ranking reduced this to 0.6%. Among 158 images with a valid target, targeted masking changed 39.2% of verdicts versus 9.2% under matched-random masking, a paired difference of 30.0 percentage points (95% CI [22.3, 37.7]). Targeted normalized centroid drift was 0.196 versus 0.031 for the control, a difference of 0.166 (95% CI [0.140, 0.193], Holm-adjusted p < .001, rank-biserial r = .892). In secondary stable-answer analyses, intersection-over-union flagged 22.1% of cases while size-invariant centroid relocation flagged 12.3%; the discrepancy was largest for small boxes. These results show that output stability, evidence movement, and evidence availability must be measured separately. The low-sensitivity pipeline remains a research testbed requiring human oversight, not an autonomous safety system.

## Author Information

Enter these fields only in EasyChair. Do not add them to the double-blind PDF.

- Author 1 name: [complete]
- Author 1 email: [complete]
- Author 1 affiliation: [complete]
- ORCID: [optional]
- Coauthor names, emails, affiliations, and order: [confirm]
- Corresponding author: [confirm]

## Files

- Paper: output/pdf/SNAS_2026_paper_submission_candidate.pdf
- Standalone abstract: output/pdf/SNAS_2026_abstract_submission_candidate.pdf
- Reproducibility bundle: output/submission/SNAS_2026_reproducibility_bundle.zip

## Human Decisions

- Obtain collaborator approval for title, author order, claims, and submission.
- Confirm that the EasyChair portal still accepts a submission after the July 15 abstract deadline.
- If a prior abstract registration is mandatory, email info@snascholars.org immediately.
- Confirm no substantially overlapping manuscript is under review elsewhere.
- Submit the paper PDF and save the EasyChair confirmation.
