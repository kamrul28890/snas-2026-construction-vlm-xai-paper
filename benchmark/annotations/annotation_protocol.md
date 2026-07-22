# Pilot Annotation Protocol

Prepared: 2026-07-19

This protocol defines the first human/domain audit layer for
ConstructionSafety-FaithBench. The pilot template is generated from
`analysis/outputs/sample_audit.csv`.

`pilot_model_assisted_annotations.*` is a completed automated baseline
annotation pass generated from dataset metadata, captions, source rule-violation
records, and pilot target boxes. It is useful for development and triage, but it
is not a replacement for independent human/domain-expert annotation.

## Goal

The annotation goal is to validate whether each image-rule pair has a clear
safety label and rule-relevant visual evidence. Annotators should not judge the
model's internal reasoning. They should judge what is visible in the image and
whether a model-provided evidence region would be acceptable for safety review.

## Input Per Example

Each annotation row contains:

- `image_id`: source ConstructionSite image ID.
- `rule_id`: normalized benchmark rule ID.
- `question`: rule-specific safety question.
- `expected_answer_seed`: weak label inherited from the pilot sample class.

The seed label is not authoritative. Correct it when the image evidence does not
support it.

## Required Fields

- `annotator_id`: stable anonymized annotator code.
- `applies_to_image`: `yes`, `no`, or `uncertain`.
- `answer_label`: `compliant`, `violation`, or `uncertain`.
- `evidence_objects`: comma-separated visible evidence objects.
- `evidence_regions_xyxy`: JSON list of absolute-pixel boxes.
- `ambiguous`: `yes` or `no`.
- `image_quality_issue`: `yes` or `no`.
- `multi_worker_ambiguity`: `yes` or `no`.
- `model_evidence_acceptable`: `yes`, `no`, or `not_shown`.
- `free_text_notes`: short note only when needed.

## Label Rules

Use `compliant` when the rule applies and visible evidence supports compliance.
Use `violation` when the rule applies and visible evidence supports a safety
violation. Use `uncertain` when the rule applicability, image quality, occlusion,
or scene geometry prevents a defensible label.

Do not infer worker intent, identity, competence, or blame.

## Evidence Regions

Mark the smallest visible regions needed to justify the safety answer. Prefer
objects named by the rule: worker, hard hat, harness, guardrail, edge, excavator,
or heavy equipment.

If multiple workers have different safety status, annotate the relevant worker
and mark `multi_worker_ambiguity=yes`.

## Disagreement Handling

At least two annotators should label the human-audited subset. Disagreements on
`answer_label`, `applies_to_image`, or evidence regions should be adjudicated by
a domain reviewer or marked as unresolved/ambiguous.

## Reporting

The paper should report:

- number of annotated examples;
- annotator count;
- agreement on answer labels;
- evidence-region agreement or overlap;
- number of ambiguous examples;
- examples excluded from headline claims.
