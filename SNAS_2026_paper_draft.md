# Draft Short Paper

> **Draft status:** Rapid working draft for technical and advisor review. This is not the camera-ready manuscript. Quantitative results come from the current Construction-VLM XAI project artifacts and must be regenerated into a frozen paper-specific table before submission.

# Beyond Stable Answers: Auditing Explanation Faithfulness in a Construction-Safety Vision-Language Pipeline

## Abstract

Vision-language models (VLMs) can support construction-safety monitoring by connecting natural-language safety rules to visual evidence. However, answer accuracy alone does not establish whether the evidence underlying a safety judgment is faithful or robust. This feasibility study adapts a six-dimensional explainable artificial intelligence evaluation framework, originally developed for tabular intrusion detection, to a VLM-grounded construction-safety pipeline. We evaluated Florence-2-base-ft on 163 held-out images from ConstructionSite 10k representing compliant scenes, personal protective equipment violations, fall hazards, and struck-by risks. Because Florence-2 does not provide native free-form visual question answering in this implementation, open-vocabulary grounding identified workers and rule-relevant safety objects, while a deterministic person-relative rule produced the compliance judgment. Explanation quality was tested through rule-aware region ranking, safety-object masking, severity-controlled perturbations, targeted and random-location occlusion, size-invariant centroid drift, bounding-box disappearance, worker-loss correction, bootstrap confidence intervals, and paired Wilcoxon tests. Area ranking selected the worker rather than the safety object in 50.3% of usable cases; rule-aware ranking reduced this to 0.6%. The corrected rule-aware top-region ablation changed 37.4% of judgments. Targeted object occlusion changed 39.2% of judgments and produced greater explanation drift than the strongest random-location control (0.198 versus 0.142; paired n = 144, p = .0011). Although intersection over union initially classified 25.0% of stable-answer cases as drifted, only 13.7% moved more than 0.2 of the image diagonal, revealing substantial small-box bias; 5.1% of targeted explanations disappeared entirely. These findings show that trustworthy construction-safety AI requires explanation-level evaluation, semantic region selection, size-aware metrics, and explicit failure accounting in addition to answer-level performance. The pipeline remains a research testbed requiring human oversight, not an autonomous safety system.

**Keywords:** Explainable artificial intelligence; vision-language models; construction safety; explanation faithfulness; robustness; trustworthy AI

## 1. Introduction

Construction remains a high-risk industry. In 2024, construction and extraction occupations experienced 1,032 fatal work injuries in the United States, corresponding to 12.6 fatalities per 100,000 full-time-equivalent workers (U.S. Bureau of Labor Statistics [BLS], 2026). Manual inspection and established safety-management practices remain essential, but visual monitoring systems may help professionals review large volumes of site imagery, identify possible violations, and prioritize follow-up investigation.

Vision-language models (VLMs) extend conventional object detection by combining visual inputs with natural-language instructions. Recent construction research has used VLMs for hazard classification, visual grounding, caption generation, and rule-based safety assessment. Domain-adapted systems have reported strong hazard-identification and captioning performance (Kim et al., 2025; Li et al., 2026), while ConstructionSite 10k provides a public benchmark connecting site images to captions, safety-rule questions, rationales, and grounding boxes (Chen & Zou, 2025). These developments suggest that VLMs may support more contextual inspection than detectors limited to predefined object classes.

High task accuracy, however, is not equivalent to trustworthy reasoning. A system can return the same answer after a perturbation while grounding that answer in a different or irrelevant location. A textual rationale can also sound plausible without reflecting the process that generated the output. Research on explainable visual question answering has highlighted cases in which correct answers coexist with irrelevant visual or textual rationales (Li et al., 2025). More broadly, attention weights should not be treated automatically as faithful explanations (Jain & Wallace, 2019), and common perturbation metrics can fail to distinguish meaningful explanations from weak or random attribution (Wu et al., 2024).

This problem is especially important in construction safety. An apparently stable warning may be unsuitable for professional review if the visual evidence moves from a hard hat to unrelated scaffolding, or if an explanation disappears while the binary answer remains unchanged. Explainability must therefore be evaluated at the evidence level rather than inferred from answer accuracy alone.

This study adapts a six-dimensional XAI evaluation framework developed for network intrusion detection, comprising descriptive accuracy, sparsity, stability, efficiency, robustness, and completeness (Arreche et al., 2024; Arreche & Abdallah, 2025). The conceptual dimensions transfer to construction safety, but their original tabular implementations do not. Image regions introduce box-size effects, masking artifacts, multimodal prompts, detector failure paths, and spatial relationships that are absent from fixed feature vectors.

The study addresses three research questions:

**RQ1:** How often do safety answers remain unchanged while visual evidence relocates or disappears under controlled perturbations?

**RQ2:** How much apparent explanation drift is genuine, and how much is caused by size-sensitive intersection over union (IoU) or inappropriate region ranking?

**RQ3:** Does occluding the rule-relevant safety object produce greater answer and explanation change than random-location occlusion?

The paper makes three contributions. First, it separates answer-level robustness from explanation-level robustness in a VLM-grounded safety pipeline. Second, it evaluates targeted and random-location interventions using IoU, size-invariant centroid drift, disappearance, and worker-loss correction. Third, it documents how area ranking, small-box bias, and detector fallback behavior can distort XAI conclusions when tabular evaluation concepts are transferred to multimodal safety evidence.

## 2. Related Work

### 2.1 Vision-Language Models for Construction Safety

Construction computer-vision systems have traditionally focused on specialized tasks such as personal protective equipment detection, worker-equipment proximity, or unsafe-action recognition. VLMs offer a broader interface by accepting both images and natural-language instructions. Kim et al. (2025) combined domain-specific image-text generation, vision-encoder adaptation, and low-rank fine-tuning for construction safety assessment. Their model achieved 94.25% safety-status accuracy on 400 images, and textual justifications were evaluated through expert and model-based judgments of relevance and preference. Li et al. (2026) adapted Qwen2.5-7B for fall-hazard identification and standardized captioning, reporting a hazard-identification F1 score of 90.2%.

Other studies have emphasized general-purpose or resource-efficient VLM evaluation. Adil et al. (2025) converted safety guidance into contextual prompts and compared several large VLMs on 1,100 construction images. A later detection-guided small-VLM framework improved hazard F1 and explanation BERTScore with limited runtime overhead (Adil et al., 2026). Chen and Zou (2025) introduced ConstructionSite 10k, a 10,013-image dataset with image captions, safety-rule VQA, rationales, and construction-element grounding.

These studies establish that construction VLMs can classify hazards and generate meaningful descriptions. Their dominant evaluation criteria are answer accuracy, F1, caption similarity, rationale relevance, or grounding IoU. Such measures establish performance or plausibility, but they do not necessarily establish whether the model-provided evidence remains causally connected to the answer under intervention.

### 2.2 Explanation Faithfulness and Metric Validity

The distinction between a plausible explanation and a faithful explanation is central to XAI. NIST defines explanation accuracy as the degree to which an explanation correctly reflects the reason for an output or the system process that generated it (Phillips et al., 2021). A faithful explanation should therefore respond predictably when supposedly important evidence is removed or altered.

Attention visualization alone is insufficient for this purpose. Jain and Wallace (2019) found that attention could be weakly related to gradient-based importance and that substantially different attention distributions could produce equivalent predictions. Wu et al. (2024) similarly showed that common cumulative perturbation metrics can overlook important properties of salience distributions. These findings motivate targeted interventions, sanity controls, and multiple explanation measures.

The six-dimension E-XAI framework provides a structured starting point for evaluating explanation quality (Arreche et al., 2024). Its white-box extension compares Integrated Gradients, layer-wise relevance propagation, and DeepLIFT using the same dimensions (Arreche & Abdallah, 2025). The present study transfers the framework at the conceptual level while adapting its operational definitions to grounding boxes and visual perturbations.

### 2.3 Trustworthy Workplace AI

The NIST AI Risk Management Framework identifies validity, reliability, safety, transparency, explainability, accountability, and documented knowledge limits as connected characteristics of trustworthy AI (National Institute of Standards and Technology [NIST], 2023). NIOSH similarly cautions that workplace AI can create risks related to autonomy, privacy, bias, transparency, and accountability even when introduced for beneficial purposes (Howard & Schulte, 2024).

Technical explanation quality should not be equated with human trust. Human studies in other safety-critical domains show that explanation type and task context can influence reliance, and that explanations can sometimes increase over-reliance (Naiseh et al., 2023). The current study therefore evaluates technical faithfulness only. It does not claim that the explanations improve professional trust, decision quality, or injury outcomes.

## 3. Method

### 3.1 Study Design and Dataset

The study used the test split of ConstructionSite 10k (Chen & Zou, 2025). The dataset contains construction images and annotations for captions, safety-rule violations, rationales, and grounding boxes. A stratified pilot sample targeted 50 images in each of four primary classes. The test split contained only 13 available struck-by-risk cases, producing a final sample of 163 images: 50 compliant, 50 PPE violation, 50 fall hazard, and 13 struck-by risk.

| Primary class | Intended n | Actual n | Reporting status |
| --- | ---: | ---: | --- |
| Compliant | 50 | 50 | Main subgroup |
| PPE violation | 50 | 50 | Main subgroup |
| Fall hazard | 50 | 50 | Main subgroup |
| Struck-by risk | 50 | 13 | Exploratory; below minimum n |
| **Total** | **200** | **163** | Feasibility sample |

The four dataset rules were mapped to safety concepts: missing basic PPE, missing harness protection at height, missing guardrail or edge protection, and unsafe worker-excavator proximity. Because an image can contain more than one worker or violation, the pipeline assigned a rule for evaluation while preserving available multi-label information for later auditing.

### 3.2 Model and Grounding-Based Decision Pipeline

The model was `microsoft/Florence-2-base-ft`, an approximately 231.6-million-parameter encoder-decoder vision foundation model supporting prompted captioning, detection, and grounding tasks (Xiao et al., 2024). Experiments ran on one NVIDIA RTX 3070.

Florence-2 did not expose a native free-form VQA task token for this implementation. The study therefore used open-vocabulary detection to ground a worker and a rule-relevant object. For PPE and fall-protection rules, a person-relative geometric check determined whether each detected worker was sufficiently close to the relevant object. PPE used an 8% maximum-image-dimension proximity threshold, while structural guardrail protection used 20%. The struck-by rule separately grounded the worker and excavator and evaluated their spatial proximity.

This distinction is fundamental: Florence-2 supplied the visual grounding, but deterministic geometric logic produced the compliant/violation judgment. The evaluated system is therefore a **VLM-grounded safety decision pipeline**, not a native end-to-end VQA model. The grounding boxes are treated as model-provided visual evidence used by the decision pipeline.

The first scene-level object-existence proxy detected only 3.0% of the 100 PPE and fall violations while achieving 97.4% specificity on the corresponding compliant cases. Replacing it with the person-relative check improved sensitivity to 27.0% and produced 73.7% specificity. This ninefold sensitivity increase demonstrated that the pipeline was no longer an almost constant compliant classifier, but its absolute sensitivity remained inadequate for deployment.

### 3.3 Explanation Representation and Region Ranking

The primary explanation unit was the bounding box returned for the rule-relevant safety object: hard hat, harness, guardrail, or excavator. Worker boxes were retained because the decision logic required person-object relationships. Four images had no native model box and used a grid fallback; these were labeled as lacking a native grounding explanation.

The frozen pilot ranked candidate regions by descending pixel area. This method systematically promoted a full worker body over small PPE. A corrected `rule_aware` policy ranked the queried safety object before other detections and used area only within semantic tiers. Area ranking was retained as a reproducible baseline rather than overwritten.

Decoder-to-encoder cross-attention was computed in the broader pilot as a secondary visual attribution signal. It is not treated here as proof of internal reasoning because attention and faithfulness are not equivalent. The paper's primary evidence comes from interventions on grounded regions.

### 3.4 Explanation and Robustness Measures

The broader project implemented six XAI dimensions. This paper focuses on descriptive accuracy, robustness, and validity controls because they directly test the relationship between evidence and output.

**Descriptive accuracy.** The top-ranked region was masked and the pipeline rerun. An answer change was counted as evidence that the region was load-bearing. Black, blur, and inpaint masking were tested to assess sensitivity to the masking operator.

**Worker-loss correction.** Masking sometimes removed the only detected worker, causing the geometric decision path to enter a scene-level fallback. A flip co-occurring with worker disappearance was labeled `flip_due_to_worker_loss` and excluded from the corrected or genuine flip rate.

**Robustness sweep.** Blur, gamma, contrast, centered occlusion, and seeded random-location occlusion were applied at three severities. The resulting file contained 2,603 perturbation rows. Targeted occlusion separately masked the baseline rule-relevant object box when one existed.

**Answer-level outcome.** `answer_changed` recorded whether the compliant/violation judgment differed from baseline.

**Explanation-level outcomes.** IoU measured box overlap, normalized centroid drift measured the distance between baseline and perturbed box centers as a fraction of the image diagonal, and `object_disappeared` recorded failure to return a post-perturbation object box. Disappearance was counted explicitly rather than omitted as a missing IoU value.

### 3.5 Statistical Analysis and Reproducibility

Percentile-bootstrap 95% confidence intervals were added to headline rates using a fixed seed. Paired Wilcoxon signed-rank tests compared per-image explanation drift. A minimum subgroup size of 30 was used to distinguish stable subgroup estimates from exploratory findings. The struck-by subgroup, n = 13, was retained with an explicit underpowered label.

The targeted-versus-random drift test paired targeted occlusion with the strongest random-location condition (severity 0.35) on images containing both measurements. Missing drift measurements were removed pairwise, yielding n = 144.

All eleven stages of the original pipeline were also executed from a clean environment on a fresh 20-image sample without manual intervention. The software test suite and generated artifacts were used to verify the metric logic and preserve the frozen pilot outputs while corrected modes wrote separate files.

## 4. Results

### 4.1 Feasibility and Baseline Limits

All six XAI dimensions ran end to end on the 163-image sample. The frozen pilot produced 36.2% top-region descriptive accuracy, 77.5% answer agreement across stochastic stability reruns, 80.7% answer survival under four Level-1 perturbations, and an estimated 0.50 GPU-hours for the complete six-metric pipeline at 1,000 samples. These values establish computational feasibility, not deployment readiness.

The descriptive-accuracy estimate was 36.2% with a bootstrap 95% confidence interval of [28.8%, 43.6%]. The apparent struck-by estimate was higher, but its n = 13 interval was [38.5%, 84.6%], too wide for a stable class-level conclusion. This subgroup is therefore not used to support the main claims.

### 4.2 Semantic Ranking Changes What the Metric Measures

Among 159 images with a model-provided explanation box, area ranking selected the worker body as the top region in 50.3% of cases. Rule-aware ranking reduced worker selection to 0.6%, selecting the queried object for nearly every usable case. For PPE specifically, the top region changed in 92.1% of samples.

This correction changed the interpretation of the masking experiment. Under frozen area ranking, the raw top-region answer-change rate was 36.2%, and the worker-loss-corrected rate was 34.4%. Under rule-aware ranking, the raw rate was 38.7%, and the corrected rate was 37.4%. The important result is not the modest aggregate increase. The corrected policy ensures that the intervention tests the safety object named by the rule rather than whichever detected entity occupies the most pixels.

| Ranking policy | Worker selected top-1 | Raw top-1 flip | Worker-loss-corrected flip |
| --- | ---: | ---: | ---: |
| Area baseline | 50.3% | 36.2% | 34.4% |
| Rule-aware | 0.6% | 38.7% | 37.4% |

### 4.3 Targeted Occlusion Produces Stronger Changes Than Random Occlusion

Targeted occlusion was possible for 158 images and changed the safety judgment in 39.2% of cases. Across the three random-location severities, the pooled answer-change rate was 17.2%; the strongest random condition, severity 0.35, changed 24.5% of judgments. Centered occlusion produced an intermediate pooled rate of 25.6%. This ordering indicates that a centered square mixed two mechanisms: it sometimes covered a relevant object and sometimes merely disrupted the scene.

Explanation-level analysis produced the same general conclusion. In the paired comparison against the strongest random-location condition, targeted occlusion had mean normalized centroid drift of 0.198 compared with 0.142 for random occlusion. The difference was statistically significant (paired n = 144, Wilcoxon p = .0011).

The severity sweep also revealed a dose-response pattern. Gamma-induced answer changes increased from 5.5% to 20.2% as severity increased. Blur increased from 27.0% to 28.8%, while centered occlusion increased from 15.3% to 33.1% and random occlusion increased from 12.3% to 24.5%. These curves are more interpretable than a single arbitrary perturbation setting.

| Condition | Answer-change rate | Mean centroid drift | Explanation disappearance |
| --- | ---: | ---: | ---: |
| Targeted object occlusion | 39.2% | 0.196 overall; 0.198 paired | 5.1% |
| Random occlusion, severity 0.35 | 24.5% | 0.143 overall; 0.142 paired | 6.7% |
| Center occlusion, severity 0.20 | 28.2% | 0.105 | 4.9% |

### 4.4 Stable Answers Can Hide Evidence Failure, but IoU Overstates It

The original fixed-perturbation pilot found that 28.3% of stable-answer rows with comparable object boxes had IoU below 0.3. Read alone, this suggested that nearly one third of unchanged answers concealed major explanation drift. The validity analysis reproduced an IoU-based rate of approximately 23% to 25%, then tested whether that finding survived size controls.

It did, but at a smaller magnitude. Among stable-answer boxes, 31.0% of small boxes crossed the IoU < 0.3 threshold compared with 24.4% of medium boxes and 13.5% of large boxes. The same stable-answer set had mean normalized centroid drift of only 0.062, and 13.7% moved more than 0.2 of the image diagonal. Thus, roughly half of the apparent IoU failures represented genuine positional relocation; the remainder largely reflected small boxes changing extent near the same location.

This correction strengthens rather than eliminates the main conclusion. Some stable answers genuinely retained different visual evidence, but IoU alone exaggerated the frequency. In addition, targeted occlusion caused the object box to disappear entirely in 5.1% of reruns. Such cases were missing from an IoU-only average and must be counted separately as severe explanation failures.

### 4.5 Detector Fallback Can Produce False Evidence of Faithfulness

The pilot initially treated every post-mask answer flip as support for the masked explanation. Detailed tracing showed that some flips occurred because the mask erased the only detected worker and activated a fallback decision path. Under frozen centered occlusion, the raw answer-change rate was 28.2%, while the worker-loss-corrected rate was 22.7%; nine of 163 flips were associated with worker loss. For rule-aware top-region descriptive accuracy, correction reduced the raw 38.7% rate to 37.4%.

The size of the correction varied by intervention, but the methodological implication is general. A perturbation test must record intermediate system state. Otherwise, a pipeline failure can be misclassified as evidence that an explanation was faithful.

## 5. Discussion

### 5.1 Answer Robustness and Explanation Robustness Are Different Properties

The results show why answer-level reporting is insufficient for safety-critical multimodal systems. A stable answer can coexist with a relocated or missing grounding box. Conversely, an answer flip can result from worker-detector failure rather than removal of the intended safety evidence. These outcomes would be indistinguishable in a binary answer-robustness table.

Trustworthy evaluation should therefore report at least three channels separately: output change, evidence movement, and evidence availability. Combining them into one score would hide which part of the system failed. This separation is consistent with NIST's emphasis on context-specific measurement, documentation, and knowledge limits (NIST, 2023).

### 5.2 XAI Metrics Require Multimodal Construct Validation

The six conceptual XAI dimensions remain useful, but image-based operationalization introduces new assumptions. Area is not semantic importance. IoU is not size invariant. Deterministic decoding can create vacuous stability. Black masking can create out-of-distribution inputs. A detector fallback can mimic causal sensitivity. Visual and textual evidence cannot be merged without explicit normalization and interpretation.

Three controls were especially valuable. Rule-aware ranking aligned the intervention with the safety concept. Targeted and random-location occlusion separated object removal from generic scene disruption. Centroid drift and disappearance prevented IoU from being the sole explanation-stability measure. These controls should be considered baseline requirements for future box-based XAI evaluation in construction VLMs.

### 5.3 Implications for Construction Safety Practice

The study does not demonstrate a deployable inspection system. The redesigned person-relative proxy detected only 27.0% of PPE and fall violations, and Florence-2 often returned only one worker box in scenes containing multiple workers. These limitations make autonomous safety decisions inappropriate.

The practical implication is instead procedural. A future decision-support tool should expose the visual evidence associated with a warning, document when evidence is absent or unstable, and defer to trained safety personnel. Explanations should help users interrogate a system's limits rather than encourage unconditional acceptance. Technical explanation faithfulness is a prerequisite for such a workflow, but human-centered validation would still be necessary to determine whether the interface supports appropriate reliance.

## 6. Limitations and Ethical Considerations

This feasibility study has several limitations. First, it evaluates one small VLM and one dataset. Results may not generalize to native-VQA models, other construction sites, video, or real-time camera systems. Second, the 163-image sample is modest, and the struck-by subgroup contains only 13 cases. Third, the final judgment is produced by geometric logic over VLM grounding rather than by end-to-end VLM reasoning. The study evaluates the evidence supplied to that pipeline, not the complete internal reasoning of a generative model.

Fourth, the person-relative proxy remains insensitive because open-vocabulary detection often returns one worker in multi-worker scenes. Fifth, the token-probability confidence value is not calibrated and is not used as a correctness probability. Sixth, masking and perturbation can create unnatural images, although blur, inpainting, severity sweeps, random controls, and worker-loss accounting reduce this concern. Seventh, no human-subject study was conducted; meaningfulness, professional trust, reliance, workload, and decision quality remain unmeasured.

Workplace imagery also raises privacy, surveillance, and fairness concerns. The study does not infer worker identity, intent, competence, or blame. The dataset does not provide a sufficient basis for demographic fairness claims. Any future deployment should include data minimization, worker notice, access controls, human review, documented appeal procedures, and explicit restrictions against autonomous disciplinary use. Explanations should support safety investigation while preserving worker autonomy and accountability for organizational decisions.

## 7. Conclusion

This study demonstrates that a stable construction-safety answer does not guarantee stable or faithful visual evidence. In a 163-image Florence-2 grounding study, semantically inappropriate ranking, IoU size bias, and worker-detector fallback each changed the interpretation of XAI metrics. Rule-aware ranking aligned interventions with safety objects, targeted occlusion produced greater output and explanation change than random controls, and size-invariant analysis showed that genuine hidden evidence relocation persisted at a smaller rate than IoU suggested. Trustworthy construction-safety AI therefore requires explanation-level interventions, size-aware metrics, explicit disappearance and fallback accounting, and clear knowledge limits in addition to answer-level performance. The current pipeline is a reproducible research testbed and a basis for future native-VQA, multi-model, and human-centered evaluation, not an autonomous inspection system.

## References

Adil, M., Ahmed, M., Aqib, M., Gonzalez, V. A., Lee, G., & Mei, Q. (2026). Integration of object detection and small VLMs for construction safety hazard identification. *arXiv*. https://arxiv.org/abs/2604.05210

Adil, M., Lee, G., Gonzalez, V. A., & Mei, Q. (2025). Using vision language models for safety hazard identification in construction. *arXiv*. https://arxiv.org/abs/2504.09083

Arreche, O., & Abdallah, M. (2025). A comparative analysis of DNN-based white-box explainable AI methods in network security. *EURASIP Journal on Information Security, 2025*, Article 16. https://doi.org/10.1186/s13635-025-00201-x

Arreche, O., Guntur, T. R., Roberts, J. W., & Abdallah, M. (2024). E-XAI: Evaluating black-box explainable AI frameworks for network intrusion detection. *IEEE Access, 12*, 23954-23988. https://doi.org/10.1109/ACCESS.2024.3365140

Chen, X., & Zou, Z. (2025). Are large pre-trained vision language models effective construction safety inspectors? *arXiv*. https://arxiv.org/abs/2508.11011

Howard, J., & Schulte, P. A. (2024, September 9). Exploring approaches to keep an AI-enabled workplace safe for workers. *National Institute for Occupational Safety and Health*. https://www.cdc.gov/niosh/bulletin/2024/ai-risk-management.html

Jain, S., & Wallace, B. C. (2019). Attention is not explanation. In *Proceedings of NAACL-HLT 2019* (pp. 3543-3556). https://doi.org/10.18653/v1/N19-1357

Kim, T., Kim, S., Chern, W.-C., Park, S., Kim, D., & Kim, H. (2025). Optimizing large vision-language models for context-aware construction safety assessment. *Automation in Construction, 180*, 106510. https://doi.org/10.1016/j.autcon.2025.106510

Li, K., Vosselman, G., & Yang, M. Y. (2025). Multimodal rationales for explainable visual question answering. In *Proceedings of the CVPR Workshops* (pp. 191-201). https://openaccess.thecvf.com/content/CVPR2025W/MULA2025/html/Li_Multimodal_Rationales_for_Explainable_Visual_Question_Answering_CVPRW_2025_paper.html

Li, Y., Xu, F., Zhang, Z., Mei, X., & Huang, H. (2026). Construction site fall hazard identification and automated captioning using adapted vision-language models. *Automation in Construction, 183*, 106790. https://doi.org/10.1016/j.autcon.2026.106790

Naiseh, M., Al-Thani, D., Jiang, N., & Ali, R. (2023). How the different explanation classes impact trust calibration: The case of clinical decision support systems. *International Journal of Human-Computer Studies, 169*, 102941. https://doi.org/10.1016/j.ijhcs.2022.102941

National Institute of Standards and Technology. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0).* https://doi.org/10.6028/NIST.AI.100-1

Phillips, P. J., Hahn, C. A., Fontana, P. C., Yates, A. N., Greene, K., Broniatowski, D. A., & Przybocki, M. A. (2021). *Four principles of explainable artificial intelligence* (NISTIR 8312). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.IR.8312

U.S. Bureau of Labor Statistics. (2026). *Number and rate of fatal work injuries, civilian workers, by major occupational group, 2024*. https://www.bls.gov/charts/census-of-fatal-occupational-injuries/number-and-rate-of-fatal-work-injuries-by-occupation.htm

Wu, J., Kang, W., Tang, H., Hong, Y., & Yan, Y. (2024). On the faithfulness of Vision Transformer explanations. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 10936-10945). https://openaccess.thecvf.com/content/CVPR2024/html/Wu_On_the_Faithfulness_of_Vision_Transformer_Explanations_CVPR_2024_paper.html

Xiao, B., Wu, H., Xu, W., Dai, X., Hu, H., Lu, Y., Zeng, M., Liu, C., & Yuan, L. (2024). Florence-2: Advancing a unified representation for a variety of vision tasks. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*. https://arxiv.org/abs/2311.06242

## Draft Revision Checklist

- [ ] Replace all manually written result values with a generated paper-results table.
- [ ] Add bootstrap confidence intervals for targeted and random-location answer-change rates.
- [ ] Decide whether the original six-metric summary belongs in the final short paper or supplementary material.
- [ ] Insert the pipeline figure, targeted-versus-random result figure, and size-bias figure.
- [ ] Verify every APA reference against its publisher record.
- [ ] Ask the XAI-methodology collaborator to review the metric-transfer claims.
- [ ] Ask a construction-safety domain expert to review rule interpretation and practical implications.
- [ ] Remove this draft-status note and revision checklist before submission.
- [ ] Apply Times New Roman 12 pt, double spacing, and the final 4-8 page limit in Word or LaTeX.
- [ ] Recheck double-blind metadata after rendering the PDF.
