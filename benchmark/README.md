# ConstructionSafety-FaithBench

ConstructionSafety-FaithBench is the benchmark layer for the construction-safety
VLM/XAI paper. It frames the SNAS study as a reusable evaluation protocol for
visual-evidence faithfulness.

The benchmark asks whether a vision-language model or VLM-grounded decision
pipeline answers construction-safety questions using rule-relevant visual
evidence, rather than relying only on scene priors, prompt wording, or unstable
post hoc rationales.

## Current Status

This folder currently contains the benchmark specification, documentation
contract, generated manifests, model-assisted labels, model outputs, and the
120-row final audit-label layer used in the SNAS submission. The final audit
labels must be reported with their explicit A/B audit-pass and adjudication
provenance, not as unqualified human ground truth.

Existing validated pilot artifacts remain under `analysis/`. Those files are
the seed evidence for this benchmark, but the benchmark is intentionally
structured as a broader artifact that can support larger image manifests,
multiple VLMs, counterfactual interventions, human/domain audits, and
conference-grade reproducibility.

## Intended Contribution

The intended contribution is an evaluation benchmark and audit protocol:

- safety-rule prompts for construction-site images;
- structured model-output schema for answers, evidence, and rationales;
- targeted and matched-control visual interventions;
- evidence-faithfulness metrics that separate answer correctness from evidence
  stability;
- failure taxonomy for answer-evidence dissociation;
- reproducible scoring scripts and artifact documentation.

## Directory Contract

```text
benchmark/
  README.md
  data_card.md
  evaluation_card.md
  rules.json
  prompts/
    safety_rule_prompts.json
  splits/
  interventions/
  annotations/
  examples/
```

Planned generated files:

- `splits/*.csv`: image IDs, dataset split, rule IDs, labels, and audit flags.
- `annotations/*.jsonl`: human/domain evidence annotations.
- `interventions/*.jsonl`: frozen intervention specifications.
- `examples/`: small visual examples safe to redistribute or references to
  non-redistributed source images.

Raw ConstructionSite images and model weights should not be copied here unless
redistribution rights are explicitly verified.

## Output Schema

Model runners should normalize model responses into:

```json
{
  "image_id": "0000001",
  "rule_id": "ppe_hard_hat",
  "model_id": "model/provider-version",
  "prompt_id": "direct_vqa_v1",
  "answer": "compliant|violation|uncertain|invalid",
  "evidence_objects": ["worker", "hard_hat"],
  "evidence_regions": [[0, 0, 1, 1]],
  "rationale": "Short evidence-grounded statement.",
  "confidence": null,
  "raw_response": "original model text or structured payload"
}
```

Boxes are absolute pixel coordinates in `[x0, y0, x1, y1]` format unless a file
explicitly declares normalized coordinates.

## Core Evaluation Questions

1. Does final-answer accuracy predict visual-evidence faithfulness?
2. Does removing rule-relevant evidence change the answer more than a matched
   random control?
3. Do evidence regions remain stable when answers remain stable?
4. Do generated rationales cite the same evidence the model grounds or uses?
5. Which failures are artifacts of metric choice, prompt wording, detector
   fallback, or small-object size bias?

## Prohibited Uses

This benchmark is for research evaluation only. It must not be used as a
standalone construction-site inspection system, autonomous compliance monitor,
worker discipline tool, or surveillance product.
