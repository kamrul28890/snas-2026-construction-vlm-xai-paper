# SNAS 2026 Literature Matrix: Construction-Safety VLMs, XAI Faithfulness, and Trustworthy AI

Prepared: July 16, 2026

Purpose: establish the related-work landscape and document the specific research gap for the proposed SNAS short paper.

## Review Questions

1. How are VLMs currently evaluated for construction safety?
2. Do those evaluations test explanation plausibility, explanation faithfulness, or both?
3. Which XAI methods and validity checks are appropriate for transformer-based visual systems?
4. How should the work be connected to trustworthy AI, workplace safety, and human oversight?

## Search Scope

The review prioritized primary sources published or available through July 2026:

- peer-reviewed journal articles;
- peer-reviewed conference papers;
- original arXiv research where a journal version was not identified;
- NIST, NIOSH/CDC, and U.S. Bureau of Labor Statistics sources;
- the two XAI evaluation papers underlying Professor Mustafa Abdallah's six-metric framework.

Secondary summaries, generic blog posts, and vendor marketing were not used to define the research gap.

## A. Construction-Safety Vision-Language Research

### 1. Kim et al. (2025), Automation in Construction

**Source:** [Optimizing large vision-language models for context-aware construction safety assessment](https://doi.org/10.1016/j.autcon.2025.106510)

**What it contributes:** A domain-adapted LVLM using construction-specific image-text generation, vision-encoder fine-tuning, and LoRA. It reports 94.25% safety-status accuracy on 400 images from 10 hazard situations, plus caption and explanation-quality measures.

**Evaluation style:** Safety classification accuracy; ROUGE-L, SPICE, and SBERT for captions; GPT-4V and expert ratings for textual justification relevance and preference.

**Gap for this paper:** Relevance and preference establish whether an explanation sounds useful, not whether the cited visual evidence faithfully supports the output under intervention.

### 2. Li et al. (2026), Automation in Construction

**Source:** [Construction site fall hazard identification and automated captioning using adapted vision-language models](https://doi.org/10.1016/j.autcon.2026.106790)

**What it contributes:** CS-VLM, a Qwen2.5-7B-Instruct model adapted with LoRA for fall-hazard identification and standardized captioning. It reports a 90.2% hazard-identification F1 score and strong caption metrics.

**Evaluation style:** Hazard F1 and caption-generation metrics such as CIDEr and SPICE.

**Gap for this paper:** The study evaluates detection and description quality, but does not make causal visual-explanation faithfulness or explanation drift its central outcome.

### 3. Chen and Zou (2025), ConstructionSite 10k

**Source:** [Are Large Pre-trained Vision Language Models Effective Construction Safety Inspectors?](https://arxiv.org/abs/2508.11011)

**What it contributes:** ConstructionSite 10k, containing 10,013 construction images with captions, safety-rule VQA annotations, reasoning, and visual grounding. It benchmarks pre-trained VLMs in zero- and few-shot settings.

**Evaluation style:** Precision and recall for rule violations, IoU for visual grounding, and relevance/equivalence criteria for reasoning.

**Importance here:** This is the source dataset and the strongest benchmark foundation for the proposed study.

**Gap for this paper:** The benchmark tests whether answers, reasons, and boxes match annotations. It does not test whether those explanations remain causally load-bearing and stable under matched interventions.

### 4. Adil et al. (2025), construction hazard identification

**Source:** [Using Vision Language Models for Safety Hazard Identification in Construction](https://arxiv.org/abs/2504.09083)

**What it contributes:** A prompt-engineering framework that turns safety guidance into contextual queries and evaluates GPT-4o, Gemini, Llama 3.2, and InternVL2 on 1,100 construction images.

**Evaluation style:** BERTScore for generated hazard assessments and processing-time comparisons.

**Gap for this paper:** The evaluation shows semantic answer quality but does not verify that a model's cited or grounded visual evidence is faithful.

### 5. Adil et al. (2026), detection-guided small VLMs

**Source:** [Integration of Object Detection and Small VLMs for Construction Safety Hazard Identification](https://arxiv.org/abs/2604.05210)

**What it contributes:** A YOLOv11n-guided small-VLM pipeline that improves hazard F1 from 34.5% to 50.6% for the best model and improves explanation BERTScore while adding little inference overhead.

**Evaluation style:** Hazard F1, explanation BERTScore, and runtime.

**Gap for this paper:** Detector guidance improves performance and explanation similarity, but similarity does not demonstrate that the explanation is causally connected to the system output.

### 6. Sammour et al. (2024/2026), responsible AI in construction safety

**Source:** [Responsible AI in Construction Safety: Systematic Evaluation of Large Language Models and Prompt Engineering](https://arxiv.org/abs/2411.08320)

**What it contributes:** A systematic evaluation of GPT-3.5 and GPT-4o on 385 professional safety questions across seven knowledge areas. It shows model-, prompt-, and knowledge-area-dependent performance and identifies reasoning, knowledge, memory, and calculation failures.

**Evaluation style:** Accuracy, reliability, consistency, prompt configuration, and error analysis.

**Gap for this paper:** It establishes why responsible, domain-specific evaluation and human oversight are needed, but it studies text-only safety knowledge rather than visual explanation faithfulness.

### 7. Love et al. (2023), XAI in construction

**Source:** [Explainable artificial intelligence: Precepts, models, and opportunities for research in construction](https://doi.org/10.1016/j.aei.2023.102024)

**What it contributes:** A construction-focused XAI taxonomy and research agenda. It argues that black-box AI limits confidence, error detection, and adoption in construction.

**Use in this paper:** Supports the need for construction-specific explainability evaluation and the interdisciplinary link between technical explanation quality and practical oversight.

**Gap for this paper:** It is a narrative review and agenda, not an empirical evaluation of explanation faithfulness in construction VLMs.

## B. XAI Evaluation and Faithfulness

### 8. Arreche et al. (2024), E-XAI

**Source:** [E-XAI: Evaluating Black-Box Explainable AI Frameworks for Network Intrusion Detection](https://doi.org/10.1109/ACCESS.2024.3365140)

**What it contributes:** An end-to-end evaluation of SHAP and LIME for network intrusion detection using six dimensions: descriptive accuracy, sparsity, stability, efficiency, robustness, and completeness.

**Importance here:** This is the original black-box framework being transferred to construction VLM evidence.

**Transfer challenge:** Tabular features have no box-size bias, visual occlusion artifact, cross-modal prompt stream, or object-detector fallback path. The six dimensions can transfer conceptually, but their operational definitions need multimodal construct validation.

### 9. Arreche and Abdallah (2025), white-box XAI

**Source:** [A comparative analysis of DNN-based white-box explainable AI methods in network security](https://doi.org/10.1186/s13635-025-00201-x)

**What it contributes:** Extends the six-metric framework to Integrated Gradients, LRP, and DeepLIFT across three intrusion datasets and compares white-box, black-box, and hybrid methods.

**Importance here:** Supplies the methodological basis for testing whether transformer-compatible attribution can be assessed under the same conceptual dimensions.

**Transfer challenge:** Florence-2 is an encoder-decoder transformer with visual patches, cross-attention, generated tokens, and grounding boxes. Traditional tabular DNN white-box implementations do not transfer unchanged.

### 10. Jain and Wallace (2019), attention is not explanation

**Source:** [Attention is not Explanation](https://doi.org/10.18653/v1/N19-1357)

**What it contributes:** Demonstrates that learned attention may be uncorrelated with gradient-based importance and that very different attention distributions can yield equivalent predictions.

**Use in this paper:** Justifies treating cross-attention as a secondary attribution signal, not proof of faithfulness. Controlled intervention should remain the primary evidence.

### 11. Wu et al. (2024), faithfulness of Vision Transformer explanations

**Source:** [On the Faithfulness of Vision Transformer Explanations](https://openaccess.thecvf.com/content/CVPR2024/html/Wu_On_the_Faithfulness_of_Vision_Transformer_Explanations_CVPR_2024_paper.html)

**What it contributes:** Introduces the Salience-guided Faithfulness Coefficient and argues that faithfulness evaluation should compare the model impact of pixel groups with different salience levels. It also shows that common cumulative perturbation metrics can fail to distinguish strong explanations from random attribution.

**Use in this paper:** Supports intervention-based evaluation, a random baseline, and caution about relying on one cumulative removal test.

### 12. Li et al. (2025), multimodal rationales for VQA

**Source:** [Multimodal Rationales for Explainable Visual Question Answering](https://openaccess.thecvf.com/content/CVPR2025W/MULA2025/html/Li_Multimodal_Rationales_for_Explainable_Visual_Question_Answering_CVPRW_2025_paper.html)

**What it contributes:** Generates both visual and textual rationales and introduces a visual-textual similarity measure. The paper explicitly notes that VQA systems can produce correct answers while focusing on irrelevant visual regions or text tokens.

**Use in this paper:** Provides direct precedent for separating answer correctness from visual and textual evidence quality.

### 13. Florence-2 foundation model

**Source:** [Florence-2: Advancing a Unified Representation for a Variety of Vision Tasks](https://arxiv.org/abs/2311.06242)

**What it contributes:** A unified sequence-to-sequence model for captioning, object detection, grounding, and segmentation using prompt-based task tokens.

**Use in this paper:** Establishes the architecture and supported task types.

**Important limitation:** The local implementation relies on open-vocabulary grounding because it does not expose a native free-form VQA task token for the proposed safety questions.

## C. Trustworthy AI, Human Oversight, and Workplace Safety

### 14. NIST AI Risk Management Framework

**Source:** [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)

**What it contributes:** Organizes risk management into govern, map, measure, and manage. It calls for documented test, evaluation, verification, and validation; context-specific performance; knowledge limits; human oversight; robustness; transparency; and explainability.

**Use in this paper:** Provides an authoritative framework for positioning the study as measurement and validation of trustworthy behavior rather than a general accuracy benchmark.

### 15. NIST Four Principles of Explainable AI

**Source:** [Four Principles of Explainable Artificial Intelligence](https://doi.org/10.6028/NIST.IR.8312)

**What it contributes:** Defines four principles: explanation, meaningfulness, explanation accuracy, and knowledge limits.

**Use in this paper:** The proposed study primarily tests explanation accuracy, meaning whether visual evidence correctly reflects the process producing the output. It does not measure meaningfulness to safety professionals without a human study.

### 16. NIOSH on AI-enabled workplace risk

**Source:** [Exploring Approaches to Keep an AI-Enabled Workplace Safe for Workers](https://www.cdc.gov/niosh/bulletin/2024/ai-risk-management.html)

**What it contributes:** Emphasizes that workplace AI creates risks as well as benefits and highlights autonomy, privacy, bias, transparency, accountability, and trustworthy operation.

**Use in this paper:** Grounds the ethical argument that construction-safety AI should support workers and professionals without becoming unaccountable surveillance or autonomous disciplinary infrastructure.

### 17. U.S. Bureau of Labor Statistics, 2024 fatal injuries

**Source:** [Number and rate of fatal work injuries by major occupational group, 2024](https://www.bls.gov/charts/census-of-fatal-occupational-injuries/number-and-rate-of-fatal-work-injuries-by-occupation.htm)

**What it contributes:** Reports 1,032 fatal injuries among construction and extraction workers in 2024, at a rate of 12.6 per 100,000 full-time-equivalent workers.

**Use in this paper:** Establishes the public-safety importance of reliable construction safety support. It does not justify claiming that the proposed pipeline will reduce fatalities.

### 18. Naiseh et al. (2023), explanation and trust calibration

**Source:** [How the different explanation classes impact trust calibration](https://doi.org/10.1016/j.ijhcs.2022.102941)

**What it contributes:** A human study with 41 medical practitioners showing that explanation type and work context affect trust calibration and that explanations can introduce over-reliance.

**Use in this paper:** Supports a cautious discussion: explanations are not automatically beneficial, and technical faithfulness should not be equated with calibrated human trust.

## Cross-Paper Comparison

| Research stream | Typical input | Common evaluation | What it establishes | What it does not establish |
| --- | --- | --- | --- | --- |
| Construction VLM performance | Site images plus prompts | Accuracy, F1, BERTScore, caption metrics | Task performance and semantic similarity | Causal faithfulness of cited evidence |
| Construction VLM grounding | Site images plus object/rule query | Bounding-box IoU | Agreement with annotated location | Stability under perturbation or freedom from size bias |
| Textual explanation evaluation | Generated rationale | Expert preference, relevance, LLM-as-judge | Plausibility and usefulness | Whether the rationale reflects the actual model process |
| Tabular XAI evaluation | Fixed feature vectors | Descriptive accuracy, sparsity, stability, efficiency, robustness, completeness | Quality of feature attributions in the tabular setting | Validity of the same operational metrics for visual boxes and prompts |
| Transformer faithfulness research | Pixels, patches, tokens | Perturbation, gradients, attention analysis, sanity baselines | Whether attribution tracks model behavior | Construction-domain safety meaning and deployment constraints |
| Human trust calibration | Human-AI decisions | Reliance, trust, confidence, task performance | Human response to explanations | Technical faithfulness unless model evidence is separately validated |

## Defensible Novelty Statement

The proposed paper should not claim to be the first construction-safety VLM or the first explainable construction AI system. Those claims would be false or too broad.

The defensible novelty is:

> This study applies a controlled, explanation-level faithfulness and robustness audit to a VLM-grounded construction-safety decision pipeline, and demonstrates how box size, region-ranking policy, and detector fallback behavior can distort conclusions when tabular XAI evaluation concepts are transferred to multimodal safety evidence.

An even narrower version for the abstract is:

> We separate answer stability from visual-evidence stability and show that matched targeted interventions and size-invariant measures reveal failures that answer accuracy and IoU alone can miss.

## Literature-Informed Method Requirements

The literature review implies that the paper should include all of the following:

- intervention-based faithfulness testing rather than explanation plausibility alone;
- a random or non-targeted control;
- answer-level and explanation-level outcomes reported separately;
- size-invariant measures in addition to IoU;
- explicit accounting for disappeared explanations;
- careful treatment of attention as a candidate signal rather than guaranteed explanation;
- visual and textual evidence treated as separate channels;
- knowledge limits and intended human oversight stated explicitly;
- no claim that technical explainability automatically creates appropriate human trust.

## Starter APA-Style References

These entries must receive a final metadata and APA audit before submission.

Adil, M., Lee, G., Gonzalez, V. A., & Mei, Q. (2025). Using vision language models for safety hazard identification in construction. *arXiv*. https://arxiv.org/abs/2504.09083

Adil, M., Ahmed, M., Aqib, M., Gonzalez, V. A., Lee, G., & Mei, Q. (2026). Integration of object detection and small VLMs for construction safety hazard identification. *arXiv*. https://arxiv.org/abs/2604.05210

Arreche, O., & Abdallah, M. (2025). A comparative analysis of DNN-based white-box explainable AI methods in network security. *EURASIP Journal on Information Security, 2025*, Article 16. https://doi.org/10.1186/s13635-025-00201-x

Arreche, O., Guntur, T. R., Roberts, J. W., & Abdallah, M. (2024). E-XAI: Evaluating black-box explainable AI frameworks for network intrusion detection. *IEEE Access, 12*, 23954-23988. https://doi.org/10.1109/ACCESS.2024.3365140

Chen, X., & Zou, Z. (2025). Are large pre-trained vision language models effective construction safety inspectors? *arXiv*. https://arxiv.org/abs/2508.11011

Jain, S., & Wallace, B. C. (2019). Attention is not explanation. In *Proceedings of NAACL-HLT 2019* (pp. 3543-3556). https://doi.org/10.18653/v1/N19-1357

Kim, T., Kim, S., Chern, W.-C., Park, S., Kim, D., & Kim, H. (2025). Optimizing large vision-language models for context-aware construction safety assessment. *Automation in Construction, 180*, 106510. https://doi.org/10.1016/j.autcon.2025.106510

Li, K., Vosselman, G., & Yang, M. Y. (2025). Multimodal rationales for explainable visual question answering. In *Proceedings of the CVPR Workshops* (pp. 191-201). https://openaccess.thecvf.com/content/CVPR2025W/MULA2025/html/Li_Multimodal_Rationales_for_Explainable_Visual_Question_Answering_CVPRW_2025_paper.html

Li, Y., Xu, F., Zhang, Z., Mei, X., & Huang, H. (2026). Construction site fall hazard identification and automated captioning using adapted vision-language models. *Automation in Construction, 183*, 106790. https://doi.org/10.1016/j.autcon.2026.106790

Love, P. E. D., Fang, W., Matthews, J., Porter, S., Luo, H., & Ding, L. (2023). Explainable artificial intelligence: Precepts, models, and opportunities for research in construction. *Advanced Engineering Informatics, 57*, 102024. https://doi.org/10.1016/j.aei.2023.102024

Naiseh, M., Al-Thani, D., Jiang, N., & Ali, R. (2023). How the different explanation classes impact trust calibration: The case of clinical decision support systems. *International Journal of Human-Computer Studies, 169*, 102941. https://doi.org/10.1016/j.ijhcs.2022.102941

National Institute of Standards and Technology. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0).* https://doi.org/10.6028/NIST.AI.100-1

Phillips, P. J., Hahn, C. A., Fontana, P. C., Yates, A. N., Greene, K., Broniatowski, D. A., & Przybocki, M. A. (2021). *Four principles of explainable artificial intelligence* (NISTIR 8312). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.IR.8312

Sammour, F., Xu, J., Wang, X., Hu, M., & Zhang, Z. (2024). Responsible AI in construction safety: Systematic evaluation of large language models and prompt engineering. *arXiv*. https://arxiv.org/abs/2411.08320

Wu, J., Kang, W., Tang, H., Hong, Y., & Yan, Y. (2024). On the faithfulness of Vision Transformer explanations. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 10936-10945). https://openaccess.thecvf.com/content/CVPR2024/html/Wu_On_the_Faithfulness_of_Vision_Transformer_Explanations_CVPR_2024_paper.html

Xiao, B., Wu, H., Xu, W., Dai, X., Hu, H., Lu, Y., Zeng, M., Liu, C., & Yuan, L. (2024). Florence-2: Advancing a unified representation for a variety of vision tasks. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*. https://arxiv.org/abs/2311.06242

