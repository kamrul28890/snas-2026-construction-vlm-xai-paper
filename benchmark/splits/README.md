# Benchmark Splits

This folder contains generated split and manifest files for
ConstructionSafety-FaithBench.

## Current Files

- `pilot_manifest.csv`: 163 image-rule pairs generated from
  `analysis/outputs/sample_audit.csv`.
- `pilot_manifest_summary.json`: counts, legacy rule mapping, and annotation
  priority counts for the pilot manifest.

## Regeneration

Run:

```powershell
python .\experiments\build_pilot_manifest.py
```

The script also regenerates annotation templates under `benchmark/annotations/`.

## Important Limitation

The pilot manifest is not a final NeurIPS-scale benchmark split. It is the seed
manifest for annotation workflow and model-run harness development.

