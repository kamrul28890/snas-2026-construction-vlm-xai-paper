# Model Run Plan

Prepared: 2026-07-19

This is the next implementation milestone after the current scaffold.

## Required Adapter Contract

Every model adapter must emit the normalized schema in
`benchmark/model_output_schema.json`:

- `image_id`
- `rule_id`
- `model_id`
- `prompt_id`
- `answer`
- `evidence_objects`
- `evidence_regions_xyxy`
- `rationale`
- `confidence`
- `raw_response`
- `provenance`

## Minimum Model Set

Start with:

- one grounding-oriented open model;
- one open instruction/VQA VLM;
- one stronger open multimodal reasoning model;
- one detector-only or Florence-style pipeline baseline;
- one caption-only leakage baseline;
- the existing image-blind majority baseline.

Add closed models only after budget, data-sharing, and API logging constraints
are clear.

## Run Order

1. Run each model on `benchmark/splits/pilot_manifest.csv`.
2. Validate outputs with `experiments/validate_model_outputs.py`.
3. Score outputs with `experiments/score_model_outputs.py`.
4. Run intervention specs from `benchmark/interventions/pilot_interventions.jsonl`.
5. Compare targeted vs matched-random changes per image.
6. Promote the harness to the larger benchmark split only after pilot outputs pass.

## Pause Points

User or advisor input is needed before:

- spending API money on closed models;
- selecting final model list for a paper claim;
- recruiting or naming human/domain annotators;
- publishing raw image-derived artifacts publicly;
- claiming any result as human-ground-truth validated.
