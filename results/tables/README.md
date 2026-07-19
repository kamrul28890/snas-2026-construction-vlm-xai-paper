# Score Tables

This folder stores generated benchmark score tables.

Regenerate the current pilot baseline score tables:

```powershell
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\pilot_annotation_bootstrap.jsonl --name pilot_annotation_bootstrap
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\pilot_florence_grounding.jsonl --name pilot_florence_grounding
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\pilot_manifest_seed.jsonl --name pilot_manifest_seed
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\pilot_majority_violation.jsonl --name pilot_majority_violation
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\scaleup_annotation_bootstrap.jsonl --name scaleup_annotation_bootstrap --annotations .\benchmark\annotations\scaleup_model_assisted_annotations.jsonl --manifest .\benchmark\splits\scaleup_candidate_manifest.csv
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\scaleup_caption_keyword.jsonl --name scaleup_caption_keyword --annotations .\benchmark\annotations\scaleup_model_assisted_annotations.jsonl --manifest .\benchmark\splits\scaleup_candidate_manifest.csv
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\scaleup_florence_grounding.jsonl --name scaleup_florence_grounding --annotations .\benchmark\annotations\scaleup_model_assisted_annotations.jsonl --manifest .\benchmark\splits\scaleup_candidate_manifest.csv
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\scaleup_manifest_seed.jsonl --name scaleup_manifest_seed --annotations .\benchmark\annotations\scaleup_model_assisted_annotations.jsonl --manifest .\benchmark\splits\scaleup_candidate_manifest.csv
python .\experiments\score_model_outputs.py --model-output .\results\frozen_model_outputs\scaleup_majority_violation.jsonl --name scaleup_majority_violation --annotations .\benchmark\annotations\scaleup_model_assisted_annotations.jsonl --manifest .\benchmark\splits\scaleup_candidate_manifest.csv
python .\experiments\score_intervention_outputs.py --intervention-output .\results\intervention_outputs\pilot_florence_interventions.jsonl --intervention-csv .\results\intervention_outputs\pilot_florence_interventions.csv --baseline-output .\results\frozen_model_outputs\pilot_florence_grounding.jsonl --manifest .\benchmark\splits\pilot_manifest.csv --name pilot_florence_interventions
```

The current scores use model-assisted annotations as reference labels. They are
pipeline validation and intervention-behavior artifacts, not final
human-ground-truth benchmark results.
