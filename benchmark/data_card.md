# Data Card: ConstructionSafety-FaithBench

Prepared: 2026-07-19

## Dataset Lineage

The planned benchmark builds on the public ConstructionSite dataset referenced
by the current paper workspace:

- dataset ID: `LouisChen15/ConstructionSite`
- frozen pilot revision: `ca3d9b885b45cbec956817edc42253664c7faf3f`
- frozen pilot split: `test`
- frozen pilot sample size: 163 images
- license recorded in current protocol: CC BY-NC 4.0

The benchmark should reference source image IDs and dataset revisions rather
than redistributing raw images unless the license and intended release context
are reviewed.

The current seed manifest is `benchmark/splits/pilot_manifest.csv`, generated
from `analysis/outputs/sample_audit.csv`.

## Data Contents

Planned benchmark records include:

- image ID;
- source dataset split and revision;
- safety rule ID;
- expected answer label;
- rule-relevant object category;
- evidence region annotations where available;
- ambiguity and quality flags;
- perturbation specifications;
- model outputs and scoring metadata.

## Safety Rules

The first benchmark version covers four construction-safety rule families:

- hard-hat/PPE compliance;
- harness/fall protection;
- guardrail/edge protection;
- struck-by/equipment proximity.

Rules are formally defined in `rules.json`.

## Annotation Plan

The current 120-row audit layer combines role-conditioned A/B audit passes with
returned adjudication for the 12 A/B disagreements. It should be treated as an
audited-label layer with explicit provenance, not as unqualified human ground
truth.

Recommended next human/domain-audit target:

- 300 to 500 audited examples;
- at least two annotators per example;
- adjudication for disagreements;
- agreement statistics for labels and evidence regions;
- explicit `ambiguous` labels instead of forcing uncertain cases into a binary
  category.

Recommended annotator tasks:

- determine whether the rule applies;
- assign answer label: `compliant`, `violation`, or `uncertain`;
- mark rule-relevant visible evidence;
- flag multi-worker ambiguity;
- flag image-quality limitations;
- judge whether model evidence would be acceptable for safety review.

## Known Risks and Biases

Construction-site imagery can encode geography, worksite type, camera position,
lighting, equipment availability, and local safety-practice biases. The current
dataset does not support demographic fairness claims. The benchmark should avoid
identity inference and should not classify worker competence, intent, blame, or
protected attributes.

Small PPE objects create metric bias because a small location shift can sharply
reduce IoU even when the evidence remains semantically similar. The benchmark
therefore reports normalized centroid drift and disappearance alongside IoU.

## Redistribution and Privacy

Before public release:

- verify the source dataset license and attribution requirements;
- avoid redistributing raw images if rights are unclear;
- remove any accidental identifying metadata;
- document non-commercial restrictions;
- include intended-use and prohibited-use statements.

## Versioning

Every benchmark release should freeze:

- source dataset revision;
- image manifest hash;
- rule file hash;
- prompt file hash;
- intervention specification hash;
- scoring code version;
- model output schema version.
