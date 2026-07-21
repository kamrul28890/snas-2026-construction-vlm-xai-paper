# Model-Assisted Annotation Methodology

Prepared: 2026-07-19

## Status

The files `pilot_model_assisted_annotations.jsonl` and
`pilot_model_assisted_annotations.csv` are complete bootstrap annotations for
the 163-image pilot manifest.

The files `scaleup_model_assisted_annotations.jsonl` and
`scaleup_model_assisted_annotations.csv` are complete bootstrap annotations for
the 588-row scale-up candidate manifest.

They are not human ground truth. They should be described as
model-assisted/source-metadata-assisted annotations.

## Inputs

The annotation pass uses:

- `benchmark/splits/pilot_manifest.csv`;
- ConstructionSite test-split metadata for the selected image IDs;
- source dataset captions;
- source dataset rule-violation records and reasons;
- source dataset violation boxes when present;
- pilot target boxes for seed compliant examples where no source violation box
  exists.

Raw images are not copied into this repository.

## Label Logic

For each image-rule pair:

- if the source dataset has a violation object for that rule, the annotation
  label is `violation`;
- otherwise the annotation label is `compliant`;
- the source violation box is converted from normalized coordinates to absolute
  pixel coordinates;
- for compliant rows, the pilot target box is used as a provisional evidence
  region when available;
- applicability and ambiguity flags are inferred from captions, source metadata,
  pilot missing-evidence flags, and image-quality metadata.

## Limitations

This pass can bootstrap development, prioritization, and reviewer-facing
provenance. It cannot replace independent annotation because it inherits source
dataset errors, caption incompleteness, and the pilot model's target-box
selection for compliant examples.

Before using these rows as evidence in a stronger benchmark paper, complete an
independent human/domain audit on a stratified subset and report agreement.
