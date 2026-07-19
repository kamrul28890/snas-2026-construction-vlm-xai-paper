# Intervention Specs

This folder stores frozen intervention specifications for benchmark runners.

Current generated files:

- `pilot_interventions.jsonl`
- `pilot_interventions.csv`
- `pilot_interventions_summary.json`

The pilot specs are generated from `benchmark/splits/pilot_manifest.csv` and
include one targeted occlusion plus five same-size matched-random occlusions for
each row with a target evidence box.

Regenerate:

```powershell
python .\experiments\build_intervention_specs.py
```

