# Frozen Model Outputs

This folder stores normalized model-output files produced by
`experiments/run_model_harness.py`.

Current built-in adapters are deterministic baselines used to test the harness:

- `annotation_bootstrap`: echoes model-assisted/source-metadata annotations.
- `manifest_seed`: echoes the weak manifest answer seed.
- `majority_violation`: image-blind majority-class baseline.

These outputs are not multi-model VLM benchmark results yet. They are the first
validated harness artifacts for Phase 3.

Regenerate the default output:

```powershell
python .\experiments\run_model_harness.py --adapter annotation_bootstrap
python .\experiments\validate_model_outputs.py
```

