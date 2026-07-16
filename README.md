# SNAS 2026 Construction VLM-XAI Paper

Research workspace for the SNAS 2026 short paper:

**Beyond Stable Answers: Auditing Explanation Faithfulness in a
Construction-Safety Vision-Language Pipeline**

This repository preserves the paper sources, research plan, literature matrix,
analysis scripts, frozen protocol, statistical outputs, generated tables and
figures, compiled PDFs, submission packages, and reproducibility records.

GitHub archive:
https://github.com/kamrul28890/snas-2026-construction-vlm-xai-paper

Visibility is intentionally private while the double-blind paper is unpublished.

## Current Status

- Submission candidate: complete and double-blind
- Paper length: 8 body pages; references begin on page 9
- Standalone abstract: 250 words
- Source test suite: 179 passed
- Paper-analysis test suite: 7 passed
- Remaining work: coauthor approval, author metadata, and EasyChair submission

The authoritative task list is
[SNAS_2026_submission_todo.md](SNAS_2026_submission_todo.md).

## Primary Deliverables

- [Submission-candidate paper PDF](output/submission/SNAS_2026_paper_submission_candidate.pdf)
- [Standalone abstract PDF](output/submission/SNAS_2026_abstract_submission_candidate.pdf)
- [Submission files ZIP](output/submission/SNAS_2026_submission_files.zip)
- [Reproducibility bundle ZIP](output/submission/SNAS_2026_reproducibility_bundle.zip)
- [EasyChair metadata](SNAS_2026_submission_metadata.md)
- [Blind-review checklist](SNAS_2026_blind_review_checklist.md)

## Headline Results

- Targeted answer change: 39.2%
- Five-seed, same-size matched-random answer change: 9.2%
- Paired difference: 30.0 percentage points, 95% CI [22.3, 37.7]
- Targeted normalized centroid drift: 0.196
- Matched-random normalized centroid drift: 0.031
- Paired drift difference: 0.166, 95% CI [0.140, 0.193]

These results support location-specific intervention sensitivity. They do not
establish recovery of internal model reasoning or deployment readiness.

## Repository Map

- analysis/: protocol, analysis code, tests, CSV/JSON results, and manifest
- figures/: publication figures in PDF and PNG formats
- generated/: generated LaTeX tables
- output/pdf/: draft and submission-candidate PDFs
- output/submission/: upload-ready PDFs and archival ZIP packages
- SNAS_2026_*: plans, drafts, LaTeX sources, metadata, and checklists

Temporary LaTeX output, rendered QA pages, caches, and local virtual
environments are intentionally excluded from version control.

## Resume the Work

Clone this repository and the XAI source repository as sibling directories:

    git clone https://github.com/kamrul28890/snas-2026-construction-vlm-xai-paper.git
    git clone https://github.com/kamrul28890/Explainable-AI-Mustafa-Abdallah.git
    cd .\snas-2026-construction-vlm-xai-paper

The paper analysis used XAI source commit
84ec95177fab618f7168f4139b06138c700eabab. The exact source files used in
the completed run are additionally protected by SHA-256 hashes in
analysis/outputs/artifact_manifest.json.

Use the validated XAI pilot environment:

    $python = '..\Explainable-AI-Mustafa-Abdallah\pilot\.venv\Scripts\python.exe'
    & $python -m pytest .\analysis\tests -q
    & $python .\analysis\run_matched_random_occlusion.py
    & $python .\analysis\generate_paper_results.py
    powershell -ExecutionPolicy Bypass -File .\build_latex.ps1

The intervention runner is resumable. Use --force only when intentionally
discarding and recomputing the paper-owned intervention output.

## Frozen Research Inputs

- Dataset: LouisChen15/ConstructionSite
- Dataset revision: ca3d9b885b45cbec956817edc42253664c7faf3f
- Dataset license: CC BY-NC 4.0
- Model: microsoft/Florence-2-base-ft
- Model revision: f6c1a25888ffc1d945ee8a1a77ac833c7303d46e
- Protocol: analysis/protocol.json

The repository does not contain raw dataset images or model weights. One
qualitative figure contains transformed dataset imagery and is retained for
private research continuity. Review dataset attribution and redistribution
rights before changing this repository to public visibility.

## Submission Safety

The paper and abstract PDFs are double-blind. Keep author names and affiliations
in EasyChair rather than in the review files. Before uploading, complete the
human checks in [SNAS_2026_blind_review_checklist.md](SNAS_2026_blind_review_checklist.md).
