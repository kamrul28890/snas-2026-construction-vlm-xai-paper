# Benchmark Splits

This folder contains generated split and manifest files for
ConstructionSafety-FaithBench.

## Current Files

- `pilot_manifest.csv`: 163 image-rule pairs generated from
  `analysis/outputs/sample_audit.csv`.
- `pilot_manifest_summary.json`: counts, legacy rule mapping, and annotation
  priority counts for the pilot manifest.
- `scaleup_candidate_manifest.csv`: larger metadata-derived candidate split for
  future human annotation and multi-model runs.
- `scaleup_candidate_manifest_summary.json`: class and rule counts for the
  candidate split.

## Regeneration

Run:

```powershell
python .\experiments\build_pilot_manifest.py
python .\experiments\build_scaleup_candidate_manifest.py
```

The pilot-manifest script also regenerates annotation templates under
`benchmark/annotations/`.

## Important Limitation

The pilot manifest and scale-up candidate manifest are not final deployment
validation splits. They are seed manifests for annotation workflow and model-run
harness development.
