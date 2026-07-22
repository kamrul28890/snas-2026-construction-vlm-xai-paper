# Human Audit Protocol

This protocol is for independent review of `human_audit_batch_001`.

The batch is prioritized from scale-up Florence diagnostics. It intentionally
over-samples rows where Florence disagrees with the automated baseline
annotation, where the baseline label is nonambiguous, or where evidence overlap is
weak. It is not a random benchmark split.

Each audited row should receive two independent annotations:

- `answer_label`: `compliant`, `violation`, or `uncertain`.
- `evidence_regions_xyxy`: JSON list of one or more absolute-pixel boxes that
  justify the answer, or `[]` when no visual evidence can be localized.
- `ambiguous`: `yes` if the image, rule, or evidence is not clear enough for a
  confident binary label.
- `notes`: short free text explaining uncertainty, missing context, or evidence.

Adjudication should be completed only after both independent annotations are
present. Disagreements should be resolved by a construction-safety reviewer
where possible. Until adjudication is complete, these files must not be described
as human ground truth.
