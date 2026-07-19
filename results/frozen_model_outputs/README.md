# Frozen Model Outputs

This folder stores normalized model-output files produced by
`experiments/run_model_harness.py`.

Current built-in adapters are deterministic baselines used to test the harness:

- `annotation_bootstrap`: echoes model-assisted/source-metadata annotations.
- `manifest_seed`: echoes the weak manifest answer seed.
- `majority_violation`: image-blind majority-class baseline.
- `caption_keyword`: uses only source captions and rule-specific keywords,
  without image pixels.
- `pilot_florence_grounding` / `scaleup_florence_grounding`: run the local Florence-2 grounding pipeline and
  deterministic geometric decision layer.

These outputs are not multi-model VLM benchmark results yet. They are the first
validated harness artifacts for Phase 3.

Scale-up outputs use the same adapters over
`benchmark/splits/scaleup_candidate_manifest.csv`.

Regenerate the default output:

```powershell
python .\experiments\run_model_harness.py --adapter annotation_bootstrap
python .\experiments\validate_model_outputs.py
```
