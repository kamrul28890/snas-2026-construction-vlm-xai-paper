# NeurIPS-Level Upgrade Plan for the Construction-Safety VLM/XAI Paper

Prepared: 2026-07-19

Working paper now: `Beyond Stable Answers: Auditing Explanation Faithfulness in a Construction-Safety Vision-Language Pipeline`

Current local evidence reviewed:

- `README.md`
- `SNAS_2026_paper_draft.md`
- `SNAS_2026_literature_matrix.md`
- `SNAS_2026_submission_todo.md`
- `analysis/protocol.json`
- `analysis/outputs/paper_results.json`
- `analysis/outputs/analysis_summary.md`

## Executive Conclusion

The current paper should not be treated as a weak draft that only needs better writing. For a NeurIPS-type venue, the current work is too small, too single-model, too domain-specific in presentation, and too dependent on a deterministic safety pipeline wrapped around Florence-2 grounding. The idea is still worth keeping, but it must be reframed as an evaluation contribution:

> A reproducible counterfactual benchmark and evaluation protocol for measuring whether construction-safety VLMs ground their answers in the visual evidence they claim or imply.

The strongest top-tier path is not "we tested Florence-2 on 163 images." The strongest path is:

> **ConstructionSafety-FaithBench:** a domain-grounded benchmark and audit suite showing that answer accuracy, textual rationales, and box IoU can substantially overstate visual-evidence faithfulness in safety-critical VLM inspection.

The most realistic top-tier target is the NeurIPS Evaluations & Datasets track, or a NeurIPS main-track Use-Inspired submission if the paper also contributes a stronger method. NeurIPS 2026 deadlines have already passed as of this document date, so the practical target would be a future NeurIPS/ICLR/CVPR/ICCV-style cycle, not NeurIPS 2026.

## Why the Current Paper Is Not Yet Top-Tier

The current SNAS version is good enough for a short interdisciplinary conference, but not for NeurIPS-level review.

Major weaknesses:

1. **Too small:** 163 images is a feasibility sample, not a convincing benchmark.
2. **Too narrow:** one model, one dataset, one deterministic decision pipeline.
3. **Not native VQA:** Florence-2 provides grounding; deterministic geometry produces the answer. This limits claims about VLM reasoning.
4. **No strong model comparison:** top-tier reviewers will ask whether the failure is Florence-2-specific, pipeline-specific, or general to modern VLMs.
5. **No released benchmark artifact yet:** NeurIPS E&D expects evaluation artifacts, code, documentation, and clear intended use.
6. **No human/domain validation:** construction safety is a real-world use case, but the paper does not yet show that rules, counterfactuals, or explanation failures are meaningful to safety professionals.
7. **Writing is not shaped like an ML paper:** the current text reads like a careful applied audit. A NeurIPS paper needs a crisp problem formalization, benchmark definition, model suite, baselines, metrics, ablations, limitations, reproducibility, and claim boundaries.

The good news: the current result has the seed of a publishable idea. The matched-random control, size-invariant drift correction, and distinction between stable answers and unstable evidence are strong. They need to become the foundation of a much broader evaluation contribution.

## Internet Research Summary

### NeurIPS Requirements and Review Bar

NeurIPS 2026 explicitly welcomes work in computer vision, language and multimodal language models, socio-technical AI, human interaction in AI systems, data-centric AI, and in-depth analysis of existing methods. It also says interdisciplinary submissions are welcome and encourages analyses that reveal limitations or behavior beyond the original scope of prior work.

NeurIPS main-track submissions are judged on Quality, Clarity, Significance, and Originality. The 2026 reviewer guidelines define quality as technical soundness and well-supported claims; clarity as clear organization and enough detail to reproduce results; significance as impact and whether others will build on the work; and originality as new insights, problem framings, metrics, methods, or combinations.

The NeurIPS Use-Inspired category is relevant because it evaluates whether the use case is real, whether methods and metrics match that use case, and whether the work gives insights that guide methods development. The construction-safety use case fits, but only if the paper explains the domain constraints without requiring reviewers to be construction experts.

The NeurIPS Evaluations & Datasets track is an even stronger fit. Its 2026 call states that evaluation itself is an object of scientific study and welcomes work that compares evaluation designs, stress-tests prior evaluations, proposes new evaluation protocols, audits datasets, contributes tools/frameworks, and presents use-case-inspired evaluations. This directly matches the current idea.

NeurIPS formatting and reproducibility expectations matter. The main text is limited to nine content pages, references and appendices do not count, the official LaTeX template is required, and submissions must be anonymized. Code and data should support reproducibility; E&D requires accessible, documented code when the main contribution is a reusable benchmark or tool. Dataset-oriented E&D work also needs strong hosting and Croissant/RAI metadata.

### Research Landscape

ConstructionSite 10k is the most relevant construction-safety dataset. It contains about 10,000 construction-site images with image captioning, safety-rule VQA, and construction-element grounding tasks. The paper introducing it argues that current large pre-trained VLMs show useful generalization but still need additional training before practical construction-site use.

Recent multimodal evaluation papers make the current idea more timely:

- MERLIM identifies "hidden hallucinations": correct answers without visual grounding.
- VLM Reality Check uses causal counterfactual image variants to show that VLMs can rely on shortcuts rather than genuine visual reasoning.
- Medical VLM faithfulness work uses controlled text and image perturbations and finds that answer accuracy and explanation quality are decoupled.
- Recent VLM chain-of-thought faithfulness work shows that models may fail to articulate image-based biases and can produce inconsistent reasoning.
- SPD-Faith Bench focuses on multimodal CoT faithfulness and identifies perception-reasoning dissociation, reinforcing the need to evaluate faithfulness beyond final correctness.

Conclusion from the literature:

> The field is moving away from "does the model answer correctly?" toward "does the model use, cite, and remain sensitive to the right evidence under controlled interventions?" The current paper is aligned with that movement, but it must become a benchmark/protocol paper rather than a one-off pilot.

## Recommended Target Paper

### Proposed Title

**ConstructionSafety-FaithBench: Counterfactual Evaluation of Visual-Evidence Faithfulness in Vision-Language Safety Inspection**

Alternative:

**When Safety Answers Are Right for the Wrong Visual Reasons: A Counterfactual Benchmark for Construction-Site VLM Faithfulness**

### Target Track

Primary recommendation: **NeurIPS Evaluations & Datasets Track**

Reason: the contribution is an evaluation protocol, benchmark suite, metric validity study, and audit framework. E&D explicitly welcomes this.

Secondary recommendation: **NeurIPS Main Track, Use-Inspired**

Only choose main-track Use-Inspired if the work adds a method that improves faithfulness, not just evaluates it. For example, a training-free evidence-calibrated prompting/reranking method that improves answer-evidence alignment across models.

### Core Claim

The paper should make this claim:

> Existing construction-safety VLM evaluations can substantially overestimate trustworthiness when they measure answer correctness, textual plausibility, or box IoU alone. Counterfactual evidence interventions reveal answer-evidence dissociation, size-biased grounding metrics, and disappearance/fallback failures across modern VLMs.

The paper should not claim:

- first construction-safety VLM;
- first explainable construction AI system;
- deployment-ready construction inspection;
- faithful internal reasoning from boxes alone;
- human trust or decision improvement without a user study.

## Required Contributions

A top-tier version should have four main contributions.

### Contribution 1: A Formal Evaluation Problem

Define the task clearly:

Given an image `x`, safety rule `r`, model answer `a`, generated or extracted rationale `t`, and visual evidence `e`, evaluate whether `a` is causally and semantically aligned with `e` under interventions that preserve or alter the rule-relevant evidence.

The paper needs formal notation for:

- image;
- rule;
- answer;
- evidence region;
- rationale;
- targeted intervention;
- matched control intervention;
- counterfactual label expectation;
- answer faithfulness;
- evidence stability;
- rationale-evidence consistency.

This formalization is currently missing.

### Contribution 2: ConstructionSafety-FaithBench

Build a benchmark artifact, not just an analysis script.

Minimum benchmark contents:

- construction-site images referenced from the source dataset without redistributing restricted raw data unless licensing allows it;
- safety rule prompts;
- expected answer labels;
- object/evidence annotations or derived evidence targets;
- perturbation/counterfactual specifications;
- model output schema;
- scoring scripts;
- reproducible environment files;
- data card and evaluation card;
- Croissant metadata if targeting NeurIPS E&D;
- anonymized submission repository.

The benchmark should include at least:

- PPE/hard-hat rules;
- harness/fall protection rules;
- guardrail/edge protection rules;
- struck-by/equipment-proximity rules;
- compliant scenes;
- multi-worker scenes;
- small-object cases;
- occluded/low-resolution cases;
- ambiguous scenes marked as ambiguous rather than forced into clean labels.

Recommended scale:

- Minimum defensible pilot: 1,000 to 2,000 images.
- Stronger NeurIPS-scale benchmark: full ConstructionSite 10k test split plus a curated stress-test subset.
- Human-audited subset: 300 to 500 examples with safety/explanation annotations from at least two trained annotators or domain experts.

### Contribution 3: Multi-Model Audit

Run the benchmark across a model suite. One Florence-2 pipeline is not enough.

Model categories:

- grounding-oriented open model, such as Florence-2;
- open native VQA or instruction VLMs available at experiment time;
- stronger open multimodal reasoning models available at experiment time;
- at least one closed/proprietary VLM if allowed and budget permits;
- a detector-only baseline;
- an image-blind/text-only baseline;
- a random or majority-class baseline.

Do not hard-code model names too early. The model list should be frozen right before experiments, because VLM leaderboards change quickly. The paper should report exact model names, versions, access dates, decoding settings, seeds, hardware, and prompts.

Minimum experiment matrix:

| Axis | Minimum |
| --- | --- |
| Models | 5 to 8 |
| Images | 1,000+ |
| Rules | 4+ |
| Prompt templates | 3 |
| Interventions | targeted, same-size random, semantic counterfactual, prompt bias |
| Seeds | 3 to 5 where stochasticity exists |
| Human-audited subset | yes |

### Contribution 4: Metric Validity and Failure Taxonomy

The strongest existing result is that IoU, area ranking, and answer stability can mislead. Turn that into a rigorous metric-validity contribution.

Required metrics:

- final answer accuracy/F1;
- answer flip under targeted intervention;
- answer flip under matched random control;
- difference-in-flip rate;
- evidence IoU;
- normalized centroid drift;
- object disappearance;
- evidence-rationale consistency;
- counterfactual label consistency;
- calibration or confidence shift if models expose confidence;
- abstention/invalid-output rate;
- prompt sensitivity.

Required failure taxonomy:

- **Answer-evidence dissociation:** answer remains stable but evidence moves or disappears.
- **Right answer, wrong evidence:** answer correct but cited/grounded object is irrelevant.
- **Wrong answer, plausible rationale:** rationale sounds safety-relevant but contradicts image evidence.
- **Small-object metric bias:** IoU penalizes small PPE boxes differently from large equipment or worker boxes.
- **Detector fallback artifact:** answer changes because a required intermediate detection fails, not because the intended safety object was causally important.
- **Prompt-induced evidence shift:** wording changes the evidence or rationale more than the image does.
- **Counterfactual blindness:** model fails to update after relevant object removal/addition.
- **Over-reliance on global scene priors:** model predicts likely safety status from construction context without local evidence.

## Experiments That Must Be Added

### Study 1: Dataset and Annotation Audit

Goal: show that the benchmark itself is trustworthy.

Tasks:

- Audit ConstructionSite 10k labels used in this paper.
- Separate unambiguous, ambiguous, and low-quality examples.
- Annotate rule-relevant evidence regions for a subset.
- Record inter-annotator agreement.
- Compare dataset boxes to human-selected evidence boxes.
- Document label noise and excluded cases.

Outputs:

- annotation protocol;
- label-quality table;
- agreement statistics;
- examples of ambiguous cases;
- data card.

Why it matters:

Top-tier reviewers will not accept a safety benchmark if labels and rules are underspecified.

### Study 2: Counterfactual Image Interventions

Goal: move beyond black-box masking.

Intervention types:

- same-size random occlusion;
- targeted object occlusion;
- segmentation-aware object removal;
- inpainting-based removal;
- object insertion where possible;
- prompt-only bias;
- image-only visual cue change;
- combined image/text conflict.

For each intervention, define expected behavior:

- If hard hat is removed from a worker, a PPE-compliance answer should change.
- If a same-size random background region is removed, answer should change much less.
- If prompt wording changes but image evidence does not, evidence should remain stable.
- If the model cites an object, removing that object should change either the answer or the stated evidence.

Outputs:

- intervention generator;
- intervention validity checks;
- before/after examples;
- per-intervention metric table.

### Study 3: Native VQA and Rationale Evaluation

Goal: remove the biggest weakness of the current paper.

Current weakness:

The current system is a VLM-grounded deterministic geometry pipeline. That is acceptable for a pilot but weak for claims about VLM reasoning.

Required upgrade:

Evaluate native VQA/instruction behavior:

- Ask the model whether the scene violates a safety rule.
- Ask for structured evidence: answer, rule, cited objects, box if possible, brief rationale.
- Force a schema where possible.
- Evaluate whether rationale and evidence agree.
- Compare generated evidence to model grounding and to human/dataset evidence.

Recommended output schema:

```json
{
  "answer": "compliant|violation|uncertain",
  "rule": "ppe|fall_harness|guardrail|struck_by",
  "evidence_objects": ["worker", "hard hat"],
  "evidence_region": "box or textual location",
  "rationale": "one short sentence",
  "confidence": 0.0
}
```

Do not evaluate long chain-of-thought as if it were internal reasoning. Use concise rationales or structured evidence statements. If chain-of-thought is studied, frame it explicitly as generated explanation faithfulness, not true internal cognition.

### Study 4: Multi-Model Benchmark Results

Goal: prove the finding generalizes.

Report:

- answer performance by model and rule;
- targeted vs matched-random answer flip;
- evidence drift;
- disappearance;
- rationale-evidence consistency;
- prompt sensitivity;
- invalid/abstention rate;
- cost and latency.

Use paired tests wherever possible because each model sees the same images and intervention pairs.

Add effect sizes, confidence intervals, and multiplicity control. Avoid relying only on p-values.

### Study 5: Ablation and Sanity Checks

Required ablations:

- area ranking vs rule-aware ranking;
- box mask vs segmentation mask;
- black mask vs blur vs inpaint;
- single prompt vs prompt ensemble;
- exact same-size random vs unconstrained random;
- object-size bands;
- with and without ambiguous examples;
- with and without multi-worker scenes;
- human boxes vs dataset boxes vs model boxes.

Required sanity checks:

- image-blind baseline;
- shuffled evidence regions;
- random evidence regions;
- label shuffle test for metric pipeline;
- no-op transformation;
- duplicate image consistency;
- prompt paraphrase consistency.

### Study 6: Human/Domain Validation

Goal: connect the benchmark to actual construction safety review.

Minimum:

- two to three domain reviewers or trained annotators;
- safety-rule interpretation review;
- evidence-region review on a stratified subset;
- human judgment of whether the model's evidence is acceptable for review.

Best version:

- user study with safety students or professionals;
- compare answer-only vs answer-plus-evidence interfaces;
- measure appropriate reliance, not just trust;
- include wrong-answer and wrong-evidence cases.

Do not overclaim human-centered benefit unless this study is done.

## Rewritten Paper Structure

Target: 9 NeurIPS pages plus references, appendix, checklist, and supplementary benchmark/code.

### Abstract

One paragraph:

- state problem: safety VLM evaluations overfocus on final answers;
- introduce ConstructionSafety-FaithBench;
- describe counterfactual evidence interventions and matched controls;
- summarize multi-model finding;
- state artifact release and limitation.

### 1. Introduction

Must answer:

- Why does visual-evidence faithfulness matter?
- Why are current construction-safety VLM evaluations insufficient?
- What is the ML/evaluation contribution beyond construction?
- What exact artifact and claims are introduced?

End with 3 to 4 contributions, no vague prose.

### 2. Related Work

Organize by problem, not by a long citation list:

- construction-safety VLMs and ConstructionSite 10k;
- VLM hallucination and grounding benchmarks;
- explanation/rationale faithfulness;
- counterfactual and perturbation-based evaluation;
- trustworthy AI and safety-critical evaluation.

Every cited work should be used to position the gap.

### 3. Benchmark and Problem Setup

Define:

- task;
- dataset;
- safety rules;
- model input/output schema;
- evidence forms;
- counterfactual/intervention protocol;
- benchmark splits;
- annotation protocol;
- limitations of the source data.

### 4. Metrics

Define metrics mathematically:

- answer correctness;
- targeted effect;
- matched-random control effect;
- causal evidence sensitivity;
- evidence stability;
- rationale-evidence agreement;
- counterfactual consistency;
- disappearance/fallback failure.

Add a short paragraph explaining why IoU alone is insufficient.

### 5. Experimental Setup

Include:

- models;
- prompts;
- decoding;
- hardware;
- seeds;
- statistics;
- confidence intervals;
- multiple comparison handling;
- human annotation procedure;
- artifact availability.

### 6. Results

Recommended result order:

1. Final-answer scores do not predict evidence faithfulness.
2. Targeted interventions reveal stronger failures than matched controls.
3. IoU and area ranking overstate or misclassify failures.
4. Failures generalize across models, but failure modes differ.
5. Human/domain audit confirms which evidence failures matter.

### 7. Discussion

Discuss:

- what this changes about evaluating VLM safety inspection;
- which metrics should be standard;
- how the benchmark should be used;
- what the benchmark cannot prove.

### 8. Limitations and Ethics

Required:

- dataset limitations;
- construction-site privacy and surveillance concerns;
- non-deployment claim;
- possible labor/disciplinary misuse;
- bias/fairness limits;
- licensing and redistribution;
- environmental/compute cost;
- human-subject or non-human-subject determination.

## Concrete Artifact Checklist

Create these files/folders:

```text
benchmark/
  README.md
  data_card.md
  evaluation_card.md
  rules.json
  splits/
  prompts/
  interventions/
  annotations/
  examples/
  croissant.json

src/
  faithbench/
    load_data.py
    interventions.py
    models/
    scoring.py
    statistics.py
    visualization.py

experiments/
  run_model.py
  run_interventions.py
  run_scoring.py
  make_tables.py
  make_figures.py

results/
  frozen_model_outputs/
  tables/
  figures/
  audit_logs/

paper/
  main.tex
  references.bib
  sections/
  figures/
  appendix.tex

tests/
  test_interventions.py
  test_metrics.py
  test_statistics.py
  test_schema.py
```

Required documentation:

- exact setup commands;
- model version manifest;
- data license notes;
- benchmark intended use;
- benchmark prohibited use;
- known failure modes;
- reproducibility checklist;
- anonymized review instructions.

## Minimum Acceptance Bar

To have a credible top-tier submission, the project should satisfy all of these:

- at least 1,000 images evaluated;
- at least 5 models;
- at least 4 safety rules;
- at least 3 prompt templates;
- targeted and matched-random controls;
- segmentation or inpainting intervention beyond black boxes;
- human/domain evidence audit;
- confidence intervals and effect sizes;
- full reproducibility package;
- anonymized benchmark/code repository;
- clear artifact documentation;
- no unsupported deployment or trust claims.

## Strong Acceptance Bar

For a genuinely strong NeurIPS E&D or main-track use-inspired paper:

- full ConstructionSite 10k test split or a carefully justified large subset;
- 8 to 12 models, including open and closed systems;
- domain-expert adjudicated safety evidence for a meaningful subset;
- cross-dataset validation on another construction/PPE/hazard dataset;
- counterfactual generation quality validation;
- prompt-bias and image-bias experiments;
- method or metric that other researchers can reuse immediately;
- public artifact by camera-ready, respecting licenses;
- appendix with full examples, prompts, and failure cases;
- a clean benchmark leaderboard script.

## Project Timeline

### Phase 0: Stop Polishing the Current Draft

Duration: 1 to 2 days

Decision:

- Keep the SNAS draft as a record.
- Do not rewrite it into NeurIPS format yet.
- Start a new benchmark-paper branch or folder.

### Phase 1: Benchmark Specification

Duration: 1 week

Tasks:

- Write formal task definition.
- Freeze safety rules.
- Define model output schema.
- Define interventions.
- Define metrics.
- Write annotation protocol.
- Decide track: E&D vs main Use-Inspired.

Deliverable:

- `benchmark/README.md`
- `benchmark/rules.json`
- `benchmark/evaluation_card.md`

### Phase 2: Data and Annotation

Duration: 2 to 4 weeks

Tasks:

- Build image/sample manifest.
- Stratify by rule, object size, ambiguity, and scene complexity.
- Human-audit a subset.
- Compute agreement.
- Create benchmark splits.
- Validate licensing.

Deliverable:

- frozen benchmark manifest;
- annotation report;
- data card.

### Phase 3: Model Harness

Duration: 2 to 3 weeks

Tasks:

- Implement unified model runner.
- Add schema validation.
- Add retry/invalid-output logging.
- Add prompt templates.
- Add model version manifest.

Deliverable:

- reproducible model-output pipeline;
- tests for schema and scoring.

### Phase 4: Intervention and Scoring

Duration: 2 to 4 weeks

Tasks:

- Implement intervention generator.
- Add same-size random controls.
- Add segmentation/inpainting options.
- Add no-op and shuffled-region sanity checks.
- Add scoring and statistics.

Deliverable:

- frozen result tables;
- figures;
- audit logs.

### Phase 5: Paper Writing

Duration: 2 to 3 weeks

Tasks:

- Write NeurIPS-style paper from results.
- Keep the first draft short and figure-driven.
- Move details to appendix.
- Fill checklist honestly.
- Prepare anonymized code supplement.

Deliverable:

- paper PDF;
- appendix;
- reproducibility supplement.

### Phase 6: Internal Review

Duration: 2 weeks

Required reviewers:

- ML/VLM reviewer;
- XAI/evaluation reviewer;
- construction-safety/domain reviewer;
- methods/statistics reviewer if available.

Review questions:

- Is the claim novel to ML reviewers?
- Is the benchmark reusable?
- Are interventions valid?
- Are conclusions supported without overclaiming?
- Would a reviewer trust the code and data?

## Immediate Next Step

Do not revise the prose first. The next concrete step is to create the benchmark specification:

```powershell
New-Item -ItemType Directory -Force benchmark, src\faithbench, experiments, tests
```

Then write:

1. `benchmark/rules.json`
2. `benchmark/evaluation_card.md`
3. `benchmark/README.md`

After that, implement the multi-model runner and intervention generator.

## Source Notes from Internet Research

- NeurIPS 2026 Call for Papers: scope includes computer vision, language and multimodal language models, socio-technical aspects of AI, human interaction in AI systems, data-centric AI, and in-depth analysis of existing methods. https://neurips.cc/Conferences/2026/CallForPapers
- NeurIPS 2026 Main Track Handbook: nine-page content limit; official LaTeX template; double-blind policy; reproducibility and artifact expectations; checklist requirement; ethics and harm mitigation expectations. https://neurips.cc/Conferences/2026/MainTrackHandbook
- NeurIPS 2026 Reviewer Guidelines: review criteria are Quality, Clarity, Significance, and Originality; Use-Inspired work is judged by real use-case fit and ML insight. https://neurips.cc/Conferences/2026/ReviewerGuidelines
- NeurIPS 2026 Evaluations & Datasets Call: evaluation is treated as a scientific object; track welcomes stress-testing, auditing, evaluation protocols, benchmark tools, and use-case-inspired evaluations. https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets
- NeurIPS Paper Checklist guidance: claims, limitations, reproducibility, code/data, experimental details, ethics, and LLM usage must be addressed transparently. https://neurips.cc/public/guides/PaperChecklist
- ConstructionSite 10k paper: introduces about 10,000 images with captioning, safety-rule VQA, and visual grounding; reports that additional training is needed for practical construction-site use. https://arxiv.org/html/2508.11011v1
- MERLIM: identifies correct answers without visual grounding as hidden hallucinations in image-language models. https://openaccess.thecvf.com/content/CVPR2025W/BEAM/html/Villa_Behind_the_Magic_MERLIM_Multi-modal_Evaluation_Benchmark_for_Large_Image-Language_CVPRW_2025_paper.html
- VLM Reality Check: uses causal counterfactual visual edits to diagnose VLM shortcut behavior and reasoning failures. https://openaccess.thecvf.com/content/CVPR2026W/DataMFM/html/Sar_VLM_Reality_Check_A_Causal_Counterfactual_Benchmark_for_Diagnosing_Cognitive_CVPRW_2026_paper.html
- Medical VLM faithfulness via multimodal perturbations: finds answer accuracy and explanation quality are decoupled, supporting evidence-level evaluation beyond final answers. https://arxiv.org/html/2510.11196v1
- Bias and CoT faithfulness in LVLMs: studies image- and text-based bias articulation and shows reasoning traces can be unfaithful or inconsistent. https://arxiv.org/html/2505.23945v1
- SPD-Faith Bench: argues multimodal CoT faithfulness must be evaluated beyond response correctness and identifies perception-reasoning dissociation. https://arxiv.org/html/2602.07833v1
