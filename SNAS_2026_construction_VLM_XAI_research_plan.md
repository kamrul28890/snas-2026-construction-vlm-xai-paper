# SNAS 2026 Research Plan: Explainable Vision-Language AI for Construction Safety

Prepared: July 16, 2026

Working conference target: 5th SNAS Interdisciplinary Research Conference

Conference theme: Trustworthy Innovation, Learning, and Human Development in the Age of Intelligent Systems

Working submission type: double-blind 4-8 page short paper, excluding references

## Todo List First

### Submission Gate: Do This Immediately

- [ ] Check whether the SNAS 2026 EasyChair portal will still accept a new submission.
- [ ] Because the listed abstract deadline was July 15, email `info@snascholars.org` immediately if a new abstract cannot be created.
- [ ] Ask whether a short paper may still be submitted by August 1 if no abstract was entered by July 15.
- [ ] Save the organizer response and EasyChair confirmation in this project folder.

### Topic and Scope

- [x] Select the broad direction: explainable vision-language AI for construction safety.
- [ ] Approve the recommended paper concept in this plan.
- [ ] Freeze the paper as a study of a **VLM-grounded safety decision pipeline**, not a claim that Florence-2 performs native free-form safety VQA.
- [ ] Freeze the primary dataset as the ConstructionSite 10k test-split pilot sample.
- [ ] Use the existing 163-sample study as the minimum viable evidence base.
- [ ] Expand the sample only if the corrected pipeline passes all validation gates by July 20.
- [ ] Do not add a human-subject experiment for this deadline; it would require IRB review, recruitment, and a longer schedule.

### Analysis and Evidence

- [ ] Regenerate every paper result from scripts or CSV files; do not copy numbers manually from prose reports.
- [ ] Use rule-aware region ranking rather than area ranking for the main analysis.
- [ ] Report frozen area-ranking results only as a baseline or construct-validity comparison.
- [ ] Report worker-loss-corrected masking results.
- [ ] Use size-invariant centroid drift and explicit box disappearance alongside IoU.
- [ ] Retain targeted and matched random-location occlusion as the main intervention comparison.
- [ ] Add bootstrap 95% confidence intervals to every headline rate.
- [ ] Use paired Wilcoxon signed-rank tests for matched intervention comparisons.
- [ ] Enforce the current minimum subgroup size of 30; label smaller groups exploratory.
- [ ] Add one random-region or randomized-ranking sanity baseline if it can be produced without destabilizing the schedule.
- [ ] Freeze seeds, package versions, prompts, thresholds, and output tables used in the paper.

### Writing and Submission

- [ ] Draft a maximum-300-word double-blind abstract.
- [ ] Draft the 4-8 page paper using the page budget in this plan.
- [ ] Keep the claim focused on explanation faithfulness, robustness, and metric validity.
- [ ] Explain the Florence-2 grounding-proxy adaptation in the Methods section and again in Limitations.
- [ ] Include no more than three high-value figures and two compact result tables.
- [ ] Convert the starter bibliography to APA style and verify every DOI and publication status.
- [ ] Remove author names, affiliations, acknowledgments, self-identifying repository links, and document metadata.
- [ ] Run a final claim-to-evidence audit before uploading.

## Executive Recommendation

Submit a focused empirical short paper built around this claim:

> A construction-safety system can preserve the same safety answer while its visual evidence changes substantially, so answer-level accuracy or robustness alone is not enough to establish trustworthy behavior. Explanation-level interventions and metric-validity controls are needed to distinguish genuine evidence drift from artifacts caused by region size, ranking rules, and detector fallback behavior.

### Recommended Working Title

**Beyond Stable Answers: Auditing Explanation Faithfulness in a Construction-Safety Vision-Language Pipeline**

Alternative titles:

1. **When the Safety Answer Stays the Same but the Evidence Moves: A Construction-Safety VLM Case Study**
2. **Do Construction-Safety VLM Explanations Survive Perturbation? A Metric-Validity Audit**
3. **From Plausible to Faithful: Evaluating Visual Evidence in Construction-Safety Vision-Language Systems**

### Why This Is the Best SNAS Paper

- It directly addresses trustworthy innovation, explainability, robustness, and human oversight.
- It uses completed experiments and corrected analyses rather than depending on a new model-training campaign.
- It fills a visible gap in construction VLM research, where most papers emphasize answer accuracy, caption similarity, or explanation relevance rather than causal explanation faithfulness.
- It has an interdisciplinary story: construction safety, multimodal AI, XAI evaluation, statistical validity, and responsible workplace technology.
- It fits a short-paper format because it can make one clear argument with three tightly connected experiments.
- It contains an honest and useful self-correction: the original IoU-based drift result was partly a small-box artifact, but a smaller genuine drift signal survives size-invariant analysis.

## Current Research Assets

The existing project at `D:\My Projects\Explainable-AI-Mustafa-Abdallah` already provides most of the required evidence.

### Completed Technical Assets

- Florence-2-base-ft, approximately 231 million parameters, running locally on a single RTX 3070.
- ConstructionSite 10k test-split sample with 163 images:
  - 50 compliant.
  - 50 PPE violation.
  - 50 fall hazard.
  - 13 struck-by risk.
- A grounding-based safety decision pipeline for four construction safety rules.
- Region extraction, visual masking, prompt perturbation, image perturbation, cross-attention, and runtime instrumentation.
- Six adapted XAI dimensions:
  - descriptive accuracy;
  - sparsity;
  - stability;
  - efficiency;
  - robustness;
  - bounded completeness.
- Validated scale-up corrections:
  - rule-aware ranking;
  - multi-label handling;
  - context matching;
  - worker-loss instrumentation;
  - unified decoding;
  - hardcoded-literal audits;
  - graded and mask-mode checks;
  - size-invariant sparsity and stability measures;
  - robustness severity sweeps;
  - targeted versus random occlusion;
  - bootstrap intervals and paired Wilcoxon tests.
- A from-scratch 20-sample reproducibility run that completed all pipeline stages without manual intervention.

### Existing Results That Can Anchor the Paper

Treat these as candidate results until regenerated into a paper-specific frozen table.

| Existing result | Why it matters |
| --- | --- |
| Frozen top-1 descriptive accuracy: 36.2%, 95% CI [28.8%, 43.6%] | Establishes that highlighted regions are load-bearing only for a minority of cases. |
| Rule-aware visual-ablation top-1 flip rate: 38.7% | Measures the corrected intervention on the safety object instead of the largest box. |
| Targeted object occlusion answer-flip rate: 39.2% | Shows the output is more sensitive when the safety object is actually removed. |
| Matched random-location occlusion answer-flip rate: 17.2% | Provides the necessary control against general scene disruption. |
| Targeted versus random centroid drift: 0.198 versus 0.142, paired Wilcoxon p = 0.0011 | Supplies a statistically supported explanation-level robustness result. |
| IoU initially flags about one quarter of stable-answer boxes as drifted | Demonstrates why answer stability alone can hide explanation instability. |
| Only 13.7% move more than 0.2 of the image diagonal after size control | Shows that roughly half the apparent IoU drift was a metric artifact, while genuine relocation remains. |
| Targeted occlusion causes object-box disappearance in 5.1% of reruns | Captures severe explanation failure that an IoU-only average would omit. |
| Small boxes cross the IoU drift threshold more than twice as often as large boxes | Demonstrates a construct-validity problem in naive box-overlap comparisons. |
| Rule-aware ranking reduces worker top-1 selection from 50.3% to 0.6% among model-box samples | Shows that a simple ranking choice can materially change what an XAI metric claims to measure. |

## Critical Framing Constraint

The paper must describe the system accurately.

Florence-2 has no native free-form VQA task token in this implementation. The project uses open-vocabulary grounding to detect workers and safety objects, then applies a deterministic person-relative geometric rule to produce a compliant/violation answer. Therefore:

- Do call it a **VLM-grounded construction-safety decision pipeline**.
- Do say that the study evaluates the faithfulness and robustness of the VLM-provided visual evidence used by the pipeline.
- Do not claim that Florence-2 itself performs end-to-end safety reasoning.
- Do not equate the mean token probability proxy with calibrated confidence.
- Do not claim the system is ready for autonomous deployment or worker discipline.

This limitation is not fatal. It creates a precise and defensible case study of how explanation evaluation changes when a tabular XAI framework is transferred to multimodal grounding.

## Literature-Derived Research Gap

The reviewed literature supports three connected gaps.

### Gap 1: Construction VLM Papers Prioritize Performance Over Faithfulness

Recent construction-safety VLM studies report safety classification accuracy, F1, caption metrics, BERTScore, grounding IoU, expert preference, or LLM-based ratings. These are useful measures of task performance and explanation plausibility, but they do not establish that the cited visual evidence caused or supported the output.

Examples include domain-fine-tuned safety assessment, fall-hazard captioning, prompt-guided hazard identification, ConstructionSite 10k benchmarking, and detector-guided small VLMs. None of these contributions makes a controlled, explanation-level robustness audit the central evaluation target.

### Gap 2: Plausible or Stable Explanations Can Be Unfaithful

The broader XAI literature warns that attention should not automatically be treated as explanation, that a correct answer may rely on irrelevant regions, and that faithfulness should be tested through interventions or corroborated attribution methods. This directly matches the local observation that stable answers can coexist with relocated or vanished grounding evidence.

### Gap 3: XAI Metrics Do Not Transfer Across Modalities Without Construct Validation

The six-metric framework was developed for tabular intrusion-detection features. Image regions create new confounds:

- IoU penalizes small boxes more harshly for the same pixel displacement.
- Area ranking promotes a worker body over a small safety object.
- Masking can erase the worker detector and trigger fallback logic rather than remove only the intended evidence.
- A deterministic decoding path can make repeated inference look perfectly stable.
- Visual and text ablations are not mathematically interchangeable.

The contribution is therefore not merely applying six existing metrics to images. It is showing which controls are required before those metrics produce defensible claims in a construction VLM setting.

## Recommended Study Design

### Objective

Evaluate whether visual explanations in a VLM-grounded construction-safety pipeline remain faithful and robust under controlled visual perturbations, and determine how common box-based XAI choices distort that evaluation.

### Research Questions

Use three primary research questions to keep the short paper focused.

**RQ1.** How often do safety answers remain unchanged while the pipeline's visual evidence relocates or disappears under controlled image perturbations?

**RQ2.** How much of the apparent explanation drift is genuine, and how much is caused by size-sensitive IoU and semantically inappropriate region ranking?

**RQ3.** Does occluding the safety-relevant object produce greater answer and explanation change than a matched random-location occlusion?

Optional secondary question, only if space permits:

**RQ4.** What adaptations are required to transfer descriptive accuracy, stability, robustness, and completeness from tabular XAI evaluation to visual grounding?

### Hypotheses

- **H1:** A non-trivial subset of stable-answer cases will show genuine explanation relocation or disappearance.
- **H2:** IoU-only drift will overstate explanation instability for small PPE boxes relative to size-invariant centroid drift.
- **H3:** Targeted safety-object occlusion will cause larger answer changes and explanation drift than matched random-location occlusion.
- **H4:** Rule-aware ranking will reduce metric contamination caused by selecting the worker body instead of the queried safety object.

### Data

Minimum viable dataset:

- ConstructionSite 10k test-split pilot sample, n = 163.
- Preserve the existing four primary classes.
- Report struck-by-risk results as exploratory because n = 13 is below the minimum floor of 30.
- Report results by safety rule when the mechanism differs, especially harness versus guardrail.

Conditional strengthened dataset:

- Expand only if the corrected scale-up pipeline is frozen by July 20.
- Prioritize meeting n >= 30 for every reported subgroup over simply maximizing the overall sample count.
- Preserve a held-out test design and do not mix training images into the main test estimate without explicit labeling.

### System

- Model: `microsoft/Florence-2-base-ft`.
- Output path: open-vocabulary grounding for worker and rule-specific safety object.
- Decision layer: deterministic person-relative geometric rule.
- Main explanation unit: rule-relevant object box.
- Secondary explanation unit, if retained: decoder-to-encoder cross-attention heatmap.
- Main region policy: rule-aware ranking.
- Baseline region policy: area ranking.

### Experimental Conditions

1. Baseline image and baseline rule query.
2. Targeted occlusion covering the rule-relevant safety object.
3. Random-location occlusion matched for area.
4. Center occlusion retained only as a historical comparison.
5. Blur severity sweep.
6. Gamma or low-light severity sweep.
7. Contrast severity sweep.

Prompt rewording should be moved to a secondary or future-work analysis unless a larger, expert-validated paraphrase set is added. The existing harness/lanyard pair changes the underlying physical concept and is not a clean synonym test.

### Primary Outcomes

Answer level:

- answer changed;
- worker-loss-corrected answer changed;
- graded score change where defined.

Explanation level:

- normalized centroid drift;
- object disappearance rate;
- IoU, stratified by object-box size;
- optional attention-map drift if the attribution stream is frozen and validated.

Faithfulness and validity:

- targeted versus random-location intervention difference;
- rule-aware versus area-ranking difference;
- black, blur, and inpaint mask sensitivity;
- non-monotonic masking count;
- random-region or randomized-ranking sanity baseline.

### Statistical Plan

- Use the image as the paired analysis unit.
- Report point estimates with percentile-bootstrap 95% confidence intervals.
- Use paired Wilcoxon signed-rank tests for targeted versus random drift.
- Report effect sizes, not only p-values.
- Use a two-sided alpha of 0.05 and identify analyses that were exploratory.
- Enforce n >= 30 for stable subgroup estimates.
- Do not make a strong per-class claim for struck-by risk at n = 13.
- Do not treat multiple perturbation rows from one image as independent samples.
- State thresholds before the final run, including the 0.2 image-diagonal genuine-relocation threshold.

### Robustness Checks

- Recompute headline results with and without worker-loss cases.
- Stratify box-based measures by small, medium, and large object area.
- Compare rule-aware and area ranking.
- Count disappeared boxes as failures rather than dropping NaN IoU rows.
- Verify that targeted and random occlusions have matched area distributions.
- Add a random explanation baseline if time permits.
- Verify all qualitative examples directly from saved before/after images.

## Paper Concepts

### Idea A: Beyond Stable Answers

**Working title:** Beyond Stable Answers: Auditing Explanation Faithfulness in a Construction-Safety Vision-Language Pipeline

**Core contribution:** Separates answer-level robustness from explanation-level robustness and shows how size controls and targeted interventions change the conclusion.

**Evidence already available:** Strong. Targeted/random experiments, centroid drift, disappearance, confidence intervals, and Wilcoxon tests exist.

**New work required:** Paper-specific result generation, one sanity baseline, figure consolidation, and writing.

**Main risk:** Reviewers may object that the final safety answer comes from geometric code. Mitigate through precise pipeline framing and by making visual-grounding faithfulness the actual object of study.

**Recommendation:** Best choice for SNAS 2026.

### Idea B: Do XAI Metrics Transfer Across Modalities?

**Working title:** Do XAI Metrics Transfer Across Modalities? A Construct-Validity Audit from Network Intrusion Features to Construction-Safety Images

**Core contribution:** Examines how six tabular XAI evaluation dimensions must be adapted for multimodal visual grounding.

**Research questions:** Which metrics transfer directly? Which produce artifacts? Which controls recover validity?

**Evidence already available:** Very strong. Area-ranking bias, worker-loss fallback, deterministic-stability trap, IoU size bias, text/visual separation, and bounded completeness are all documented.

**New work required:** Build a compact metric-by-metric taxonomy and avoid overloading the 8-page limit.

**Main risk:** The paper may become too broad and read like an engineering postmortem. Keep one quantitative result per metric and organize around construct validity.

**Recommendation:** Strong second choice, or use it as the methods framing inside Idea A.

### Idea C: Prompt Wording as a Safety-Reliability Variable

**Working title:** When Paraphrases Change the Hazard: Prompt Sensitivity in Construction-Safety Visual Grounding

**Core contribution:** Tests whether semantically equivalent safety prompts preserve answers and grounding evidence.

**Required new study:** Create 6-10 domain-expert-validated paraphrases per rule, separate true synonyms from related concepts, and measure answer and box drift.

**Evidence already available:** Moderate. Existing prompt changes show 50.0% answer change for harness/lanyard versus 10.2% for guardrail/edge barrier, but the former pair is not semantically equivalent.

**Main risk:** The existing prompt set is too small and partially invalid. A clean paraphrase study is feasible but requires careful expert review before inference.

**Recommendation:** Good backup if the organizers prefer a language, learning, or AI-literacy angle.

### Idea D: Small VLMs for Trustworthy On-Site Safety Support

**Working title:** Accuracy, Efficiency, and Faithfulness Tradeoffs in Small Vision-Language Models for Construction Safety

**Core contribution:** Compare Florence-2 with a native-VQA model such as Qwen2.5-VL 3B under a common safety benchmark.

**Required new study:** Run a same-proxy comparison and a separately labeled native-VQA comparison; add model-specific attribution adapters.

**Evidence already available:** Low to moderate. Florence-2 results exist, but the comparison model and fair attribution protocol do not.

**Main risk:** Too much implementation and compute risk before August 1. Proxy versus native-VQA comparisons can easily become confounded.

**Recommendation:** Better for the later full journal paper than this SNAS deadline.

### Idea E: Explanations and Safety-Professional Trust Calibration

**Working title:** Do Visual Explanations Help Safety Professionals Appropriately Rely on AI Hazard Warnings?

**Core contribution:** Human-centered evaluation of whether grounding boxes and uncertainty cues improve appropriate reliance rather than merely increasing trust.

**Required new study:** IRB approval, safety-professional recruitment, interface design, controlled correct/incorrect cases, and trust/reliance measures.

**Evidence already available:** Conceptual only.

**Main risk:** Cannot be completed responsibly for the current deadline.

**Recommendation:** Long-term extension, not SNAS 2026.

## Concept Ranking

Scores use a 1-5 scale, where 5 is strongest.

| Concept | SNAS fit | Novelty | Existing evidence | Deadline feasibility | Method risk | Overall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Beyond Stable Answers | 5.0 | 4.8 | 5.0 | 4.8 | 4.2 | **4.8** |
| B. Metric Transfer Audit | 5.0 | 4.7 | 5.0 | 4.5 | 4.0 | **4.6** |
| C. Prompt Sensitivity | 4.4 | 4.0 | 3.1 | 3.8 | 3.4 | **3.7** |
| D. Small-VLM Tradeoffs | 4.6 | 4.3 | 2.5 | 2.2 | 2.6 | **3.2** |
| E. Human Trust Calibration | 5.0 | 4.5 | 1.0 | 1.0 | 1.5 | **2.2** |

## Proposed Paper Structure and Page Budget

Target 7.5-8 pages, excluding references.

| Section | Target length | Purpose |
| --- | ---: | --- |
| Title and abstract | 0.3 page | State the trustworthiness problem, paired intervention design, central result, and contribution. |
| 1. Introduction | 0.8 page | Construction safety need, why answer accuracy is insufficient, research questions, contributions. |
| 2. Related work | 1.0 page | Construction VLMs, explanation faithfulness, XAI in construction, gap. |
| 3. System and data | 0.8 page | ConstructionSite 10k, 163-sample composition, Florence-2 grounding proxy, rules. |
| 4. Evaluation method | 1.5 pages | Rule-aware regions, targeted/random interventions, outcomes, statistics, safeguards. |
| 5. Results | 1.8 pages | Answer versus explanation robustness, size confound, targeted/random comparison. |
| 6. Discussion | 0.9 page | Trustworthy innovation, human oversight, metric-transfer lessons, practical meaning. |
| 7. Limitations and ethics | 0.6 page | Proxy decision layer, sample size, dataset representativeness, privacy, no deployment claim. |
| 8. Conclusion | 0.3 page | One concise conclusion and next validation step. |

### Recommended Figures

1. **Pipeline and intervention diagram:** image -> Florence-2 grounding -> rule-aware safety object -> geometric verdict -> targeted/random perturbation -> answer and explanation outcomes.
2. **Targeted versus random result panel:** answer-flip rate, centroid drift, and disappearance with confidence intervals.
3. **Metric-validity panel:** IoU drift by object-size band versus size-invariant centroid drift, plus one qualitative stable-answer/evidence-move example.

### Recommended Tables

1. Dataset, rules, sample counts, and underpowered-subgroup flag.
2. Main quantitative results with estimates, confidence intervals, effect sizes, and p-values.

## Contribution Statements for the Draft

The final Introduction should make no more than three contributions:

1. A construction-specific evaluation that separates answer robustness from visual-explanation robustness in a VLM-grounded safety pipeline.
2. A matched targeted-versus-random intervention protocol with size-invariant drift and explicit explanation-disappearance measures.
3. Empirical evidence that naive IoU, area-based region ranking, and detector fallback behavior can overstate or misattribute explanation failures when tabular XAI metrics are transferred to multimodal safety systems.

## Ethics and Responsible-AI Position

- Position the system as decision support for trained safety personnel, not autonomous enforcement.
- State that explanations do not guarantee correctness, fairness, or calibrated human trust.
- Avoid inferring worker identity, intent, competence, or blame from images.
- Acknowledge that camera placement, lighting, occlusion, PPE appearance, and dataset composition can create unequal error patterns.
- Do not claim demographic fairness because the dataset does not provide a valid demographic evaluation basis.
- Explain that workplace images can create privacy and surveillance concerns even when used for safety.
- Recommend human review, appeal paths, data minimization, and documented knowledge limits before deployment.
- Tie the study to NIST's valid/reliable, safe, transparent, explainable, and accountable characteristics.

## Claim Boundaries

The paper may claim:

- answer stability can coexist with explanation instability;
- size-sensitive metrics can exaggerate small-object drift;
- targeted interventions provide a more meaningful faithfulness test than unstructured scene perturbation;
- metric design choices materially affect XAI conclusions;
- the pipeline is reproducible and computationally feasible as a research testbed.

The paper must not claim:

- that Florence-2 performs native end-to-end safety reasoning;
- that grounding boxes reveal the model's complete internal reasoning;
- that an explanation causes human trust or improves safety outcomes without a human study;
- that the results generalize to all VLMs, sites, worker populations, or camera systems;
- that the n = 13 struck-by subgroup supports a stable class-level estimate;
- that a synthetic patch proves a real-world attack vulnerability;
- that the system is ready for unsupervised deployment.

## Execution Schedule

This schedule assumes work begins July 16 and the paper is due August 1.

### July 16: Submission and Scope Gate

- Check EasyChair and contact organizers if necessary.
- Approve Idea A, with Idea B as its methodological framing.
- Freeze title, research questions, and author list outside the blind manuscript.

### July 17-18: Literature and Protocol Freeze

- Verify the literature matrix and APA metadata.
- Write the preregistered analysis note: outcomes, thresholds, tests, exclusions, and subgroup floor.
- Decide whether a random explanation baseline will be included.

### July 19-20: Data and Pipeline Audit

- Confirm sample identities, class counts, and no train/test leakage.
- Confirm rule-aware ranking, worker-loss correction, decoding, thresholds, and version pins.
- Decide whether to remain at n = 163 or expand.

### July 21-22: Final Analysis

- Run the paper-specific analysis script.
- Generate frozen CSV/JSON result tables.
- Produce confidence intervals, effect sizes, and Wilcoxon tests.
- Audit qualitative examples against source images.

### July 23: Figures

- Generate the three paper figures directly from frozen outputs.
- Check labels, sample sizes, legends, and color accessibility.

### July 24-25: Methods and Results Draft

- Write Methods from the frozen protocol.
- Write Results from generated tables only.
- Add limitations adjacent to every potentially misleading result.

### July 26-27: Introduction, Related Work, and Discussion

- Write the literature-derived gap.
- Connect the results to trustworthy innovation and human oversight.
- Avoid unsupported claims about trust or accident prevention.

### July 28: Complete Draft

- Assemble the full 4-8 page manuscript.
- Reduce figures and prose until the central argument is easy to follow.

### July 29: Technical Review

- Ask Professor Abdallah and construction-domain collaborators to review claims, methods, and interpretation.
- Resolve comments that affect validity before stylistic edits.

### July 30: Revision and References

- Revise the manuscript.
- Verify APA references, DOIs, publication years, and arXiv status.

### July 31: Blind and Format Audit

- Remove identifying content and metadata.
- Confirm Times New Roman 12 pt, double spacing, 4-8 pages excluding references.
- Render and inspect the final PDF page by page.

### August 1: Submit

- Upload through EasyChair.
- Verify the uploaded PDF rather than only the local copy.
- Save the submitted file and confirmation locally.

## Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Abstract deadline already passed | Submission may be blocked | Check EasyChair and contact organizers immediately. |
| Florence-2 is not native VQA | Reviewers may see the task framing as overstated | Use the VLM-grounded pipeline framing consistently and make the decision layer explicit. |
| n = 163 and class imbalance | Weak subgroup generalization | Use intervals, n >= 30 floor, exploratory labels, and avoid class claims for struck-by risk. |
| IoU size bias | Inflated explanation-drift claims | Report size bands, centroid drift, and disappearance; do not use IoU alone. |
| Worker-loss fallback | Masking can flip the answer for the wrong reason | Report corrected and raw values and retain non-monotonicity checks. |
| Attention is treated as explanation | Faithfulness may be overstated | Use causal perturbation as the primary evidence and label attention as a secondary attribution signal. |
| Too many metrics for 8 pages | Paper becomes diffuse | Center the paper on answer/explanation robustness; use other metrics only as validity controls. |
| Manual number copying | Draft and data can diverge | Generate tables and figure inputs programmatically from frozen outputs. |
| Human-trust claims without participants | Interdisciplinary implications become overstated | Discuss oversight and trust calibration as implications, not measured outcomes. |
| Dirty or evolving source repository | Results can change during drafting | Tag or record a paper-analysis commit and hash every frozen output. |

## Acceptance Criteria for the Paper Package

The submission is ready only when all of the following are true:

- The organizer or EasyChair permits the submission.
- Every headline number is generated from a frozen artifact.
- Every reported subgroup meets n >= 30 or is explicitly labeled exploratory.
- Targeted and random occlusions are matched and analyzed as paired observations.
- IoU is never the only explanation-drift measure.
- Disappeared boxes remain in the failure accounting.
- Worker-loss contamination is quantified.
- The Methods section states that the safety verdict is produced by geometric logic over VLM grounding.
- The Discussion distinguishes technical explanation faithfulness from human trust.
- The PDF passes double-blind and formatting checks.
- The submitted PDF has been opened and visually inspected after upload.

## Immediate Decision

Proceed with **Idea A: Beyond Stable Answers**, and use **Idea B: Metric Transfer Audit** as the methodological lens. This combination gives the paper one clear empirical story while preserving the strongest interdisciplinary contribution: trustworthy AI requires validating both the model evidence and the metrics used to judge that evidence.

