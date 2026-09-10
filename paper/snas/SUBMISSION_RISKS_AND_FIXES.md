# Submission Risks and Required Fixes

## Status: Camera-Ready Revision (Review 1)

The paper was accepted and is now being revised for camera-ready against
`reviews/review-1.md`. The double-blind constraints below no longer apply:
author names, affiliations, and the repository link are now intentionally
present.

## Done in the Camera-Ready Revision

- Rewrote Introduction, Benchmark, Metrics, Results, Discussion, Limitations,
  Conclusion, and Abstract around an explicit problem/gap/RQ/contribution story.
- Added RQ1/RQ2/RQ3 and mapped each to its experiment, metric, and result.
- Defined every technical term at first use, including Florence-2, grounding
  adapter, deterministic, IoU, macro-F1, and centroid drift.
- Added in-text citations throughout; reference list expanded to 11 and audited
  in both directions.
- Added author byline, PDF author metadata, and a Reproducibility Statement
  carrying the public repository link.
- Produced an IEEE two-column camera-ready variant
  (`SNAS_2026_FaithBench_camera_ready_ieee.tex`).
- Stripped machine-specific absolute paths from generated artifacts and added an
  export guard that fails if they reappear.

## Two Open Format Questions

- Confirm whether the camera-ready must use the IEEE template or the original
  SNAS format (Times New Roman, 12 pt, double-spaced, APA).
- Confirm the camera-ready page limit. The IEEE variant is currently about 8.2
  body pages, marginally over the 4-8 page limit stated in the original call.

## Do Not Misrepresent

The returned annotation files explicitly state that the A/B passes were AI-generated. Do not call them human annotators or actual human personas. The safe wording is:

`two independent audit passes plus returned adjudication`

or:

`adjudicated audit labels with AI-pass provenance`

## Remaining Human Checks Before Camera-Ready Upload

- Confirm the required template (IEEE vs. original SNAS format) and the page limit.
- Confirm author order, affiliations, and corresponding author in the byline.
- Publish the reproducibility repository before upload, since the paper now cites
  its URL. Run `python experiments/sanitize_release_paths.py --check` first.
- Have a construction-safety domain reviewer verify or replace the audit layer
  before making stronger human-ground-truth claims.
- Verify the two headline behavioural claims added in revision: that no audited
  row was answered `uncertain`, and that the hard-hat and guardrail slices were
  answered `compliant` for all 30 rows each.
