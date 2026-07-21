# Human Audit Adjudication Package

This package contains only the 12 rows where the two independent AI-generated audit passes disagreed.

Open `adjudication_form.csv` and fill only these fields:

- `adjudicated_answer_label`: `compliant`, `violation`, or `uncertain`.
- `adjudicated_evidence_regions_xyxy`: JSON boxes supporting the final decision, or `[]`.
- `adjudicated_ambiguous`: `yes` or `no`.
- `adjudication_notes`: one short explanation of the decision.

Use the image, rule/question, and both annotator notes. The source annotations are AI-generated and should be treated as competing recommendations, not ground truth.
