# Human Annotation Instructions

Thank you for helping annotate construction-safety images for this research project.

The goal is to independently judge whether a visible construction scene satisfies a specific safety rule, and to mark the visual evidence that supports your judgment. Please use only the image and the rule/question shown for that row. Do not use any model predictions, previous labels, or other annotator decisions while completing your annotation.

## What You Will Receive

For each row, you should receive:

- `audit_id`: unique row ID.
- `image_id`: source image ID.
- the image itself.
- `rule_id`: safety rule name.
- `question`: the safety question to answer.
- optionally, `image_caption`: a short source caption. Use this only as context if the image is unclear; the image should be the main evidence.

If the spreadsheet includes columns such as `model_assisted_answer_label`, `florence_predicted_answer`, `priority_score`, `source_violation_boxes_xyxy`, or `model_assisted_evidence_regions_xyxy`, please ignore them. Those are diagnostic columns for the researchers and should not influence your independent annotation.

## Labels To Fill

Fill the fields assigned to you, for example `annotator_1_*` or `annotator_2_*`.

### 1. Answer Label

Fill `answer_label` with exactly one of:

- `compliant`: the image appears to satisfy the rule.
- `violation`: the image appears to violate the rule.
- `uncertain`: the image does not provide enough visual evidence for a confident compliant/violation decision.

Do not force a binary answer. Use `uncertain` when the worker, equipment, edge, protective gear, distance, or relevant context is not visually clear.

### 2. Evidence Regions

Fill `evidence_regions_xyxy` with a JSON list of bounding boxes around the visual evidence that supports your answer.

Use absolute pixel coordinates in this format:

```text
[[x_min, y_min, x_max, y_max]]
```

For multiple evidence regions:

```text
[[100, 50, 180, 220], [260, 70, 340, 210]]
```

Use `[]` if no specific visual evidence can be localized.

Box guidance:

- Draw boxes around the smallest useful region, not the whole image.
- Include the worker and the relevant safety object/context when both are needed.
- For PPE, mark the worker/head/helmet area or the missing-PPE region if visible.
- For harness/fall protection, mark the worker and visible harness/lanyard or fall-risk context.
- For guardrail/edge protection, mark the edge/opening and guardrail/barrier area.
- For struck-by risk, mark the worker, heavy equipment, and proximity area if visible.

### 3. Ambiguous

Fill `ambiguous` with:

- `yes`: the image/rule/evidence is visually unclear, even if you chose compliant or violation.
- `no`: the image provides enough evidence for a confident judgment.

Use `yes` for blur, occlusion, tiny objects, poor lighting, mixed worker compliance, unclear height, unclear equipment activity, or uncertain distance/depth.

### 4. Notes

Fill `notes` with one short sentence explaining your decision or uncertainty.

Examples:

- `Worker head is visible but helmet area is too small to judge.`
- `One worker near the edge appears to lack fall protection.`
- `Excavator is visible, but worker distance is hard to infer from the image.`
- `Guardrail is visible along the open edge.`

## Safety Rules

### `ppe_hard_hat`

Question: Is each visible worker wearing required head protection?

- `compliant`: all visible workers who require head protection appear to have hard hats or equivalent head protection.
- `violation`: at least one visible worker appears to lack required head protection.
- Common ambiguity: small/blurred heads, helmets hidden by angle, mixed compliance across several workers.

### `fall_harness`

Question: Does the worker at height have visible fall-protection equipment?

- `compliant`: workers exposed to fall risk have visible harness/lanyard or equivalent protection.
- `violation`: a worker exposed to fall risk appears to lack visible fall protection.
- Common ambiguity: fall height unclear, harness hidden by clothing, ladder/platform context unclear.

### `guardrail_edge`

Question: Is the visible elevated edge protected by a guardrail or equivalent barrier?

- `compliant`: a visible elevated edge/opening has a guardrail, barrier, or equivalent protection.
- `violation`: a visible elevated edge/opening lacks guardrail/barrier protection.
- Common ambiguity: camera crop hides the full edge, barrier unclear, edge height unclear.

### `struck_by_equipment`

Question: Is a worker unsafely close to active heavy equipment?

- `compliant`: visible workers appear outside the danger zone of heavy equipment.
- `violation`: at least one visible worker appears unsafely close to heavy equipment.
- Common ambiguity: still image does not show equipment activity, depth/distance unclear, barrier not visible, equipment partly cropped.

## Important Rules For Annotation Quality

- Work independently. Do not discuss labels with another annotator before submitting.
- Do not look at model predictions or existing automated baseline annotations.
- Do not infer facts that are not visible in the image.
- Mark `uncertain` rather than guessing when visual evidence is insufficient.
- Do not identify people or assign blame. This is only a visual safety-rule annotation task.
- Keep notes short and factual.

## Output Example

For one row, a completed annotation might look like:

```text
answer_label: violation
evidence_regions_xyxy: [[396,594,480,666], [576,558,660,666]]
ambiguous: no
notes: Two workers at height appear to lack visible fall protection.
```

Another acceptable row:

```text
answer_label: uncertain
evidence_regions_xyxy: []
ambiguous: yes
notes: Worker and helmet area are too small and blurred to judge.
```
