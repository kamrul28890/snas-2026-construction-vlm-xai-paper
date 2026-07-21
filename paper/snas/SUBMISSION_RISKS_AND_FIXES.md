# Submission Risks and Required Fixes

## Fixed in This Package

- Removed prior venue-specific wording from the SNAS paper and abstract.
- Prepared a double-blind SNAS short-paper PDF and abstract PDF.
- Kept the paper within the SNAS 4-8 page body limit, excluding references.
- Used Times New Roman, 12-point font, double spacing, clear headings, and APA-style references.
- Removed PDF author metadata through LaTeX `pdfauthor={}`.
- Created exact copy-paste submission text in `SUBMISSION_TEXTS.md`.
- Created a clean reproducibility repository package without raw dataset images or local handoff bundles.

## Do Not Misrepresent

The returned annotation files explicitly state that the A/B passes were AI-generated. Do not call them human annotators or actual human personas. The safe wording is:

`two independent role-conditioned audit passes plus returned adjudication`

or:

`adjudicated audit labels with AI-pass provenance`

## Remaining Human Checks Before Upload

- Confirm EasyChair still allows paper submission even though the abstract deadline was July 15, 2026.
- Confirm whether SNAS requires a previously submitted abstract before the August 1, 2026 paper upload.
- Enter author names and affiliations only in EasyChair, not inside the review PDF.
- Do not put a GitHub URL under `kamrul28890` in the double-blind abstract or paper unless SNAS explicitly permits non-anonymous artifacts.
- If you want a repo link in the reviewed abstract, ask SNAS whether this violates double-blind review. The package includes a public/post-review abstract with the repo link, but the safer review version omits it.
- Have a construction-safety domain reviewer verify or replace the role-conditioned audit layer before making stronger human-ground-truth claims.
- Decide whether to describe the work as `work in progress`, `audit benchmark`, or `empirical study`; the current safest label is `compact empirical audit study`.
