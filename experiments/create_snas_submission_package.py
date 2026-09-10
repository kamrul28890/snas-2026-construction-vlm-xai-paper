"""Create the SNAS submission-ready package and clean reproducibility export."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "snas_submission_ready"
REPRO = OUT / "reproducibility_repo"
ZIP_BASE = OUT / "SNAS_2026_FaithBench_submission_package"
PUBLIC_REPO_URL = "https://github.com/kamrul28890/snas-2026-construction-safety-faithbench"

FILES = [
    ".gitignore",
    "requirements.txt",
    "benchmark/README.md",
    "benchmark/data_card.md",
    "benchmark/evaluation_card.md",
    "benchmark/model_output_schema.json",
    "benchmark/rules.json",
    "benchmark/prompts/safety_rule_prompts.json",
    "benchmark/splits/README.md",
    "benchmark/splits/pilot_manifest.csv",
    "benchmark/splits/pilot_manifest_summary.json",
    "benchmark/splits/scaleup_candidate_manifest.csv",
    "benchmark/splits/scaleup_candidate_manifest_summary.json",
    "benchmark/interventions/README.md",
    "benchmark/interventions/pilot_interventions.csv",
    "benchmark/interventions/pilot_interventions.jsonl",
    "benchmark/interventions/pilot_interventions_summary.json",
    "benchmark/annotations/annotation_protocol.md",
    "benchmark/annotations/human_annotation_prompt.md",
    "benchmark/annotations/human_audit_protocol.md",
    "benchmark/annotations/model_assisted_methodology.md",
    "benchmark/annotations/pilot_annotation_template.csv",
    "benchmark/annotations/pilot_annotation_template.jsonl",
    "benchmark/annotations/pilot_model_assisted_annotation_summary.json",
    "benchmark/annotations/pilot_model_assisted_annotations.csv",
    "benchmark/annotations/pilot_model_assisted_annotations.jsonl",
    "benchmark/annotations/scaleup_annotation_template.csv",
    "benchmark/annotations/scaleup_annotation_template.jsonl",
    "benchmark/annotations/scaleup_model_assisted_annotation_summary.json",
    "benchmark/annotations/scaleup_model_assisted_annotations.csv",
    "benchmark/annotations/scaleup_model_assisted_annotations.jsonl",
    "benchmark/annotations/human_audit_batch_001.csv",
    "benchmark/annotations/human_audit_batch_001.jsonl",
    "benchmark/annotations/human_audit_batch_001_adjudication.csv",
    "benchmark/annotations/human_audit_batch_001_adjudication.jsonl",
    "benchmark/annotations/human_audit_batch_001_ai_disagreements.csv",
    "benchmark/annotations/human_audit_batch_001_final_labels.csv",
    "benchmark/annotations/human_audit_batch_001_final_labels.jsonl",
    "benchmark/annotations/human_audit_batch_001_final_labels_summary.json",
    "benchmark/annotations/human_audit_batch_001_returned_adjudication_manifest.json",
    "benchmark/annotations/human_audit_batch_001_returned_adjudication_README.md",
    "benchmark/annotations/human_audit_batch_001_summary.json",
    "results/frozen_model_outputs/README.md",
    "results/frozen_model_outputs/pilot_annotation_bootstrap.csv",
    "results/frozen_model_outputs/pilot_annotation_bootstrap.jsonl",
    "results/frozen_model_outputs/pilot_annotation_bootstrap_summary.json",
    "results/frozen_model_outputs/pilot_florence_grounding.csv",
    "results/frozen_model_outputs/pilot_florence_grounding.jsonl",
    "results/frozen_model_outputs/pilot_florence_grounding_summary.json",
    "results/frozen_model_outputs/pilot_majority_violation.csv",
    "results/frozen_model_outputs/pilot_majority_violation.jsonl",
    "results/frozen_model_outputs/pilot_majority_violation_summary.json",
    "results/frozen_model_outputs/pilot_manifest_seed.csv",
    "results/frozen_model_outputs/pilot_manifest_seed.jsonl",
    "results/frozen_model_outputs/pilot_manifest_seed_summary.json",
    "results/frozen_model_outputs/scaleup_annotation_bootstrap.csv",
    "results/frozen_model_outputs/scaleup_annotation_bootstrap.jsonl",
    "results/frozen_model_outputs/scaleup_annotation_bootstrap_summary.json",
    "results/frozen_model_outputs/scaleup_caption_keyword.csv",
    "results/frozen_model_outputs/scaleup_caption_keyword.jsonl",
    "results/frozen_model_outputs/scaleup_caption_keyword_summary.json",
    "results/frozen_model_outputs/scaleup_florence_grounding.csv",
    "results/frozen_model_outputs/scaleup_florence_grounding.jsonl",
    "results/frozen_model_outputs/scaleup_florence_grounding_summary.json",
    "results/frozen_model_outputs/scaleup_majority_violation.csv",
    "results/frozen_model_outputs/scaleup_majority_violation.jsonl",
    "results/frozen_model_outputs/scaleup_majority_violation_summary.json",
    "results/frozen_model_outputs/scaleup_manifest_seed.csv",
    "results/frozen_model_outputs/scaleup_manifest_seed.jsonl",
    "results/frozen_model_outputs/scaleup_manifest_seed_summary.json",
    "results/intervention_outputs/README.md",
    "results/intervention_outputs/pilot_florence_interventions.csv",
    "results/intervention_outputs/pilot_florence_interventions.jsonl",
    "results/intervention_outputs/pilot_florence_interventions_summary.json",
    "results/tables/README.md",
    "results/tables/human_audit_batch_001_ai_agreement.csv",
    "results/tables/human_audit_batch_001_final_label_per_example_scores.csv",
    "results/tables/human_audit_batch_001_final_label_scores.csv",
    "results/tables/human_audit_batch_001_status.csv",
    "results/tables/pilot_florence_interventions_per_intervention.csv",
    "results/tables/pilot_florence_interventions_summary.csv",
    "results/tables/scaleup_florence_grounding_slices.csv",
    "paper/snas/README.md",
    "paper/snas/SNAS_2026_FaithBench_short_paper.tex",
    "paper/snas/SNAS_2026_FaithBench_abstract_blind.tex",
    "paper/snas/SUBMISSION_TEXTS.md",
    "paper/snas/SUBMISSION_RISKS_AND_FIXES.md",
    "paper/snas/figures/pipeline_architecture.pdf",
    "paper/snas/figures/audit_result_dashboard.pdf",
    "paper/snas/figures/intervention_effects_chart.pdf",
    "src/faithbench/__init__.py",
    "src/faithbench/annotation.py",
    "src/faithbench/geometry.py",
    "src/faithbench/intervention_metrics.py",
    "src/faithbench/interventions.py",
    "src/faithbench/manifest.py",
    "src/faithbench/metrics.py",
    "src/faithbench/model_harness.py",
    "src/faithbench/scaleup.py",
    "src/faithbench/schema.py",
    "src/faithbench/scoring.py",
    "src/faithbench/statistics.py",
    "tests/test_faithbench_specs.py",
    "experiments/analyze_score_slices.py",
    "experiments/build_human_audit_batch.py",
    "experiments/build_intervention_specs.py",
    "experiments/build_model_assisted_annotations.py",
    "experiments/build_pilot_manifest.py",
    "experiments/build_scaleup_annotations.py",
    "experiments/build_scaleup_candidate_manifest.py",
    "experiments/ingest_human_audit_adjudication.py",
    "experiments/ingest_human_audit_passes.py",
    "experiments/make_paper_figures.py",
    "experiments/run_florence_grounding_outputs.py",
    "experiments/run_florence_intervention_outputs.py",
    "experiments/run_model_harness.py",
    "experiments/score_human_audit_final_labels.py",
    "experiments/score_human_audit_status.py",
    "experiments/score_intervention_outputs.py",
    "experiments/score_model_outputs.py",
    "experiments/validate_all.py",
    "experiments/validate_annotations.py",
    "experiments/validate_benchmark_specs.py",
    "experiments/validate_human_audit_batch.py",
    "experiments/validate_intervention_outputs.py",
    "experiments/validate_model_outputs.py",
    "experiments/validate_phase4_outputs.py",
    "experiments/validate_scaleup_manifest.py",
]

SUBMISSION_FILES = [
    ("tmp/snas/SNAS_2026_FaithBench_short_paper.pdf", "submission/SNAS_2026_FaithBench_short_paper_blind.pdf"),
    ("tmp/snas/SNAS_2026_FaithBench_abstract_blind.pdf", "submission/SNAS_2026_FaithBench_abstract_blind.pdf"),
]


def copy_file(src_rel: str, dst_rel: str | None = None) -> None:
    src = ROOT / src_rel
    if not src.exists():
        raise FileNotFoundError(src)
    dst = REPRO / (dst_rel or src_rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def reset_export_dir() -> None:
    REPRO.mkdir(parents=True, exist_ok=True)
    for child in REPRO.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child, onerror=make_writable)
        else:
            child.unlink()


def make_writable(function, path, _exc_info) -> None:
    os.chmod(path, 0o700)
    function(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_readme() -> None:
    text = f"""# ConstructionSafety-FaithBench

Clean reproducibility package for the SNAS 2026 short paper:

**ConstructionSafety-FaithBench: Auditing Visual-Evidence Faithfulness in Construction-Safety Vision-Language Models**

Public repository: {PUBLIC_REPO_URL}

## What Is Included

- Blind SNAS short-paper and abstract PDFs under `submission/`.
- Copy-paste submission text and final risk checklist under `paper/snas/`.
- Benchmark manifests, safety rules, prompts, schemas, and intervention specs.
- Frozen model outputs and generated score tables used in the paper.
- The 120-row final audit-label layer with explicit A/B audit-pass and adjudication provenance.
- Source code and tests required to validate schemas and regenerate major results.

Raw ConstructionSite images, model weights, local annotator handoff folders, caches, and venue-draft material are not included.

## Headline Numbers

- Audit labels: 120 rows; 108 A/B consensus rows plus 12 returned adjudication decisions.
- Final label distribution: 83 violation, 31 compliant, 6 uncertain.
- Florence grounding accuracy on the audit layer: 18.3%.
- Automated baseline accuracy on the audit layer: 78.3%.
- Targeted evidence-occlusion answer flip rate: 39.2%.
- Matched-random answer flip rate: 9.2%.
- Paired answer-flip difference: 30.0 percentage points.

## Important Provenance Note

The final audit labels should be described as:

`two independent audit passes plus returned adjudication`

or:

`adjudicated audit labels with AI-pass provenance`

Do not describe them as unqualified human ground truth unless an independent human/domain audit replaces or verifies this layer.

## Reproduce Checks

```powershell
pip install -r requirements.txt
python .\\experiments\\validate_benchmark_specs.py
python .\\experiments\\validate_annotations.py
python .\\experiments\\validate_human_audit_batch.py
python .\\experiments\\validate_model_outputs.py
python .\\experiments\\validate_intervention_outputs.py
python .\\experiments\\validate_phase4_outputs.py
python .\\experiments\\validate_scaleup_manifest.py
pytest .\\tests -q
```
"""
    (REPRO / "README.md").write_text(text, encoding="utf-8")


def write_manifest() -> None:
    records = []
    for path in sorted(p for p in REPRO.rglob("*") if p.is_file() and ".git" not in p.parts):
        rel = path.relative_to(REPRO).as_posix()
        records.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "paper_title": "ConstructionSafety-FaithBench: Auditing Visual-Evidence Faithfulness in Construction-Safety Vision-Language Models",
        "public_repo_url": PUBLIC_REPO_URL,
        "file_count": len(records),
        "files": records,
    }
    (REPRO / "REPRODUCIBILITY_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def assert_clean_text() -> None:
    blocked = ["NeurIPS", "neurips ready", "top-tier neurips"]
    # Absolute Windows/UNC paths would publish local directory layout, including
    # sibling project directories outside this repository.
    machine_paths = re.compile(r"[A-Za-z]:\\\\?[A-Za-z0-9_. -]|\\\\[A-Za-z0-9_.-]+\\")
    offenders: list[str] = []
    path_offenders: list[str] = []
    for path in REPRO.rglob("*"):
        if ".git" in path.parts:
            continue
        if not path.is_file() or path.suffix.lower() not in {".md", ".tex", ".py", ".json", ".csv", ".jsonl", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(term in text for term in blocked):
            offenders.append(path.relative_to(REPRO).as_posix())
        if machine_paths.search(text):
            path_offenders.append(path.relative_to(REPRO).as_posix())
    if offenders:
        raise RuntimeError("Blocked venue wording found in export: " + ", ".join(offenders))
    if path_offenders:
        raise RuntimeError(
            "Absolute machine paths found in export (run "
            "experiments/sanitize_release_paths.py): " + ", ".join(path_offenders)
        )


def write_zip() -> Path:
    zip_path = ZIP_BASE.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in REPRO.rglob("*") if p.is_file() and ".git" not in p.parts):
            archive.write(path, path.relative_to(REPRO).as_posix())
    return zip_path


def main() -> int:
    reset_export_dir()

    for src_rel in FILES:
        copy_file(src_rel)

    for src_name, dst_rel in SUBMISSION_FILES:
        copy_file(src_name, dst_rel)

    write_readme()
    assert_clean_text()
    write_manifest()

    archive = write_zip()
    print(f"Wrote clean reproducibility export: {REPRO}")
    print(f"Wrote zip package: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
