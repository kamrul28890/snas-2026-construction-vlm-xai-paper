# Internal Review Checklist

Prepared: 2026-07-19

Use this before treating the scaffold as a serious NeurIPS-style submission.

## Technical Review

- [ ] Confirm the benchmark task definition is clear to an ML reviewer.
- [ ] Confirm answer metrics and evidence metrics are separated.
- [ ] Confirm every metric has a stated failure mode and limitation.
- [ ] Confirm intervention specs are deterministic and reproducible.
- [ ] Confirm same-size random controls preserve mask size.
- [ ] Confirm IoU is never used alone for small-object conclusions.
- [ ] Confirm every generated table can be regenerated from scripts.

## Annotation Review

- [ ] Do not describe `pilot_model_assisted_annotations.*` as human ground truth.
- [ ] Select a stratified subset for independent annotation.
- [ ] Use at least two annotators per audited example.
- [ ] Report agreement for answer labels and evidence regions.
- [ ] Mark ambiguous examples instead of forcing binary labels.
- [ ] Have a construction-safety reviewer inspect the rule definitions.

## Model Review

- [ ] Add real VLM adapters behind the normalized model-output schema.
- [ ] Freeze exact model names, versions, prompts, decoding settings, and dates.
- [ ] Include image-blind, majority, and detector/pipeline baselines.
- [ ] Log invalid outputs and abstentions.
- [ ] Preserve raw responses for audit.
- [ ] Avoid comparing closed-model outputs without recording access conditions.

## Writing Review

- [ ] Replace the portable article scaffold with the official target-year NeurIPS template.
- [ ] Rebuild the paper after every generated-table update.
- [ ] Make all claims match the actual artifact status.
- [ ] Keep deployment, surveillance, and worker-discipline limitations explicit.
- [ ] Move implementation details to appendix when the main text exceeds page limits.

