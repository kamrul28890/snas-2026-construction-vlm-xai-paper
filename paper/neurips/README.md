# NeurIPS Paper Scaffold

This folder is a working scaffold for a future NeurIPS-style benchmark paper:

**ConstructionSafety-FaithBench: Counterfactual Evaluation of Visual-Evidence
Faithfulness in Vision-Language Safety Inspection**

This is not a submission-ready paper. It currently captures the benchmark
structure, pilot artifacts, baseline harness, intervention specs, and claim
boundaries. Real NeurIPS-level results still require multi-model VLM runs and
independent human/domain annotation.

## Regenerate Tables

```powershell
python .\experiments\make_paper_tables.py
python .\experiments\validate_paper_scaffold.py
```

## Compile Note

The current `main.tex` uses a portable `article` scaffold. Before submission,
replace it with the official NeurIPS template for the target year and rerun
formatting checks.

