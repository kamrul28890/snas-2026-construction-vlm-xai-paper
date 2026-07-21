# Evaluation Card: ConstructionSafety-FaithBench

Prepared: 2026-07-19

## Evaluation Purpose

ConstructionSafety-FaithBench evaluates visual-evidence faithfulness in
construction-safety VLMs and VLM-grounded pipelines. It is designed to show when
final answers, generated rationales, or grounding boxes overstate whether the
model is using the right visual evidence.

The evaluation does not certify deployment readiness.

## Recommended Paper Framing

The strongest current framing is a compact empirical audit study:

- evaluation protocol;
- benchmark artifact;
- metric-validity analysis;
- use-case-inspired audit;
- failure taxonomy;
- reproducible scoring suite.

Stronger model-ranking or deployment claims require additional independent
model runs and human/domain annotation.

## Model Types

A credible top-tier evaluation should include:

- grounding-oriented open VLM;
- native VQA/instruction VLMs;
- multimodal reasoning VLMs;
- at least one closed model if budget and policy permit;
- detector-only baseline;
- image-blind/text-only baseline;
- random or majority-class baseline.

Model names, versions, prompts, access dates, decoding parameters, seeds, and
hardware must be recorded in a model manifest.

## Metrics

Primary answer metrics:

- answer accuracy;
- macro F1 by safety rule;
- invalid-output rate;
- abstention/uncertain rate.

Primary faithfulness metrics:

- targeted answer-change rate;
- matched-random answer-change rate;
- paired targeted-minus-control effect;
- evidence IoU;
- normalized centroid drift;
- evidence disappearance;
- stable-answer evidence drift;
- rationale-evidence consistency.

Validity and sanity metrics:

- no-op consistency;
- shuffled-evidence sensitivity;
- image-blind baseline performance;
- prompt-paraphrase sensitivity;
- object-size-band sensitivity;
- worker/object fallback failure rate.

## Intervention Requirements

Every intervention must define the expected causal behavior. Initial
intervention families:

- targeted object occlusion;
- same-size random occlusion;
- segmentation-aware object removal;
- inpainting-based removal;
- prompt-only bias;
- image/text conflict;
- no-op transformation.

Same-size random controls are required because unconstrained random controls can
confound object relevance with mask size.

## Statistical Reporting

Report:

- image-level paired comparisons;
- bootstrap confidence intervals;
- effect sizes;
- multiplicity adjustment for primary tests;
- subgroup results only when sample size is adequate;
- exploratory labels for underpowered subgroups.

Do not rely on p-values alone.

## Failure Taxonomy

Use the following failure labels:

- `answer_evidence_dissociation`: answer stable but evidence changes or
  disappears.
- `right_answer_wrong_evidence`: final answer correct, evidence irrelevant.
- `wrong_answer_plausible_rationale`: explanation sounds plausible but answer is
  wrong.
- `small_object_metric_bias`: IoU failure driven by object scale.
- `detector_fallback_artifact`: answer changes because an intermediate detector
  failed.
- `prompt_induced_evidence_shift`: prompt wording changes evidence selection.
- `counterfactual_blindness`: model ignores relevant visual edits.
- `scene_prior_shortcut`: model appears to answer from global context or priors.

## Claim Boundaries

Acceptable claims:

- final-answer evaluation can miss evidence failures;
- targeted interventions reveal failures not captured by matched random
  controls;
- IoU alone is insufficient for small construction-safety objects;
- construction-safety VLM evaluation needs evidence-level metrics.

Unsupported without additional studies:

- deployment readiness;
- injury reduction;
- calibrated human trust;
- demographic fairness;
- faithful internal model reasoning;
- autonomous compliance enforcement.
