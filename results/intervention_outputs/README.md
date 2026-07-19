# Intervention Outputs

This folder stores model outputs generated after applying frozen visual intervention
specifications from `benchmark/interventions`.

Current artifact:

- `pilot_florence_interventions`: Florence-2 grounding rerun on 948 pilot
  occlusions, covering 158 targeted masks and 790 matched-random controls.

Regenerate with:

```powershell
$python = '..\Explainable-AI-Mustafa-Abdallah\pilot\.venv\Scripts\python.exe'
& $python .\experiments\run_florence_intervention_outputs.py --interventions .\benchmark\interventions\pilot_interventions.jsonl --output-stem pilot_florence_interventions
python .\experiments\score_intervention_outputs.py --intervention-output .\results\intervention_outputs\pilot_florence_interventions.jsonl --intervention-csv .\results\intervention_outputs\pilot_florence_interventions.csv --baseline-output .\results\frozen_model_outputs\pilot_florence_grounding.jsonl --manifest .\benchmark\splits\pilot_manifest.csv --name pilot_florence_interventions
```

These are intervention-behavior diagnostics for the current local Florence
pipeline. They do not establish human-ground-truth benchmark validity.
