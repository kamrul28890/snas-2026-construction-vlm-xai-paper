# NeurIPS Paper Scaffold

This folder is a working scaffold for a future NeurIPS-style benchmark paper:

**ConstructionSafety-FaithBench: Counterfactual Evaluation of Visual-Evidence
Faithfulness in Vision-Language Safety Inspection**

This is not a submission-ready paper. It currently captures the benchmark
structure, pilot artifacts, baseline harness, intervention specs, final audit
labels with explicit AI-pass provenance, generated figures, and claim
boundaries. Real broad NeurIPS-level model-ranking claims still require
multi-model VLM runs and independent human/domain verification of the audit
layer.

## Regenerate Tables

```powershell
python .\experiments\make_paper_tables.py
python .\experiments\make_paper_figures.py
python .\experiments\validate_paper_scaffold.py
```

## Compile Note

The current `main.tex` uses a portable `article` scaffold. Before submission,
replace it with the official NeurIPS template for the target year and rerun
formatting checks. NeurIPS-style submissions should keep the main content within
the target-year page limit; the current draft keeps dense results in the main
paper and detailed reproducibility material in the appendix.
