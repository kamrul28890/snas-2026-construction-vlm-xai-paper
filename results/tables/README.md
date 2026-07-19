# Score Tables

This folder stores generated benchmark score tables.

Regenerate the current pilot baseline score tables:

```powershell
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\pilot_annotation_bootstrap.jsonl --name pilot_annotation_bootstrap
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\pilot_manifest_seed.jsonl --name pilot_manifest_seed
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\pilot_majority_violation.jsonl --name pilot_majority_violation
```

The current scores use model-assisted annotations as reference labels. They are
pipeline validation artifacts, not final human-ground-truth benchmark results.

