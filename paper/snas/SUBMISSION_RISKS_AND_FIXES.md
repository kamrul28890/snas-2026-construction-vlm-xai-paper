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
- Stripped machine-specific absolute paths from generated artifacts and added an
  export guard that fails if they reappear.
- Ported the manuscript onto the official SNAS camera-ready LaTeX template and
  converted the hand-written APA reference list to BibTeX (`references.bib`,
  `apacite`).

## Format: Settled

On 2026-09-15 the program chair emailed the official camera-ready templates.
They are **not** IEEE: the LaTeX template is a single-column
`\documentclass[12pt,letterpaper]{article}` with 1 in margins, `newtxtext`,
`\onehalfspacing`, and APA citations via `apacite`. The manuscript now follows
it, and the IEEE variant and its generator have been deleted. The email also
states that authors may change headings freely, so this paper's section names
need no adjustment.

## One Open Format Question

- Confirm the camera-ready page limit. **Neither the templates nor the
  camera-ready email states one.** The manuscript currently runs 21 pages in the
  official single-column template, against the 4-8 page limit in the original
  call. If that limit still applies, the paper needs substantial compression.

## Do Not Misrepresent

The returned annotation files explicitly state that the A/B passes were AI-generated. Do not call them human annotators or actual human personas. The safe wording is:

`two independent audit passes plus returned adjudication`

or:

`adjudicated audit labels with AI-pass provenance`

## Remaining Human Checks Before Camera-Ready Upload

- Confirm the camera-ready page limit with the organizers (see above).
- Complete the presentation attendance-mode form and conference registration;
  registration closes 2026-09-25, the same day as the camera-ready upload.
- Confirm author order, affiliations, and corresponding author in the byline.
- Publish the reproducibility repository before upload, since the paper now cites
  its URL. Run `python experiments/sanitize_release_paths.py --check` first.
- Have a construction-safety domain reviewer verify or replace the audit layer
  before making stronger human-ground-truth claims.
- Verify the two headline behavioural claims added in revision: that no audited
  row was answered `uncertain`, and that the hard-hat and guardrail slices were
  answered `compliant` for all 30 rows each.
