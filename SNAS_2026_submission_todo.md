# SNAS 2026 Paper Submission Todo and Requirements

GitHub archive: https://github.com/kamrul28890/snas-2026-construction-vlm-xai-paper

Repository visibility: private

Default branch: main

## Full-Paper Completion Update

- [x] Preserved the original visible draft and created a separate submission candidate.
- [x] Created the candidate paper source: SNAS_2026_paper_submission_candidate.tex.
- [x] Created the candidate paper PDF: output/pdf/SNAS_2026_paper_submission_candidate.pdf.
- [x] Created the 250-word standalone abstract and PDF submission candidate.
- [x] Froze the protocol, model and dataset revisions, thresholds, seeds, and claim boundaries.
- [x] Replaced the invalid severity control with five exactly same-size random-location controls per image.
- [x] Ran paired bootstrap intervals, Wilcoxon tests, rank-biserial effects, Holm adjustment, and sensitivity analysis.
- [x] Generated analysis CSVs, publication figures, LaTeX tables, and an artifact hash manifest.
- [x] Verified eight body pages, references from page 9, ten total pages, and one abstract page.
- [x] Verified embedded Times New Roman, empty author metadata, clean LaTeX logs, and all rendered pages.
- [x] Created SNAS_2026_submission_metadata.md and SNAS_2026_blind_review_checklist.md.
- [x] Source test suite: 179 passed. Paper-analysis suite: 7 passed.
- [ ] Human-only: confirm author order and collaborator approval.
- [ ] Human-only: confirm EasyChair still accepts a new or late abstract registration.
- [ ] Human-only: upload the double-blind paper and save the confirmation.

Source read: https://snascholars.org/snas-interdisciplinary-research-conference-2026/
Submission portal: https://easychair.org/conferences/?conf=snas2026
Checked: July 16, 2026

Selected research direction: Explainable vision-language AI for construction safety.

Research plan: `SNAS_2026_construction_VLM_XAI_research_plan.md`

Literature matrix: `SNAS_2026_literature_matrix.md`

Abstract draft: `SNAS_2026_abstract_draft.md`

Short-paper draft: `SNAS_2026_paper_draft.md`

LaTeX abstract draft: `SNAS_2026_abstract_draft.tex`

LaTeX short-paper draft: `SNAS_2026_paper_draft.tex`

Rendered draft PDFs: `output/pdf/SNAS_2026_abstract_draft.pdf` and `output/pdf/SNAS_2026_paper_draft.pdf`

Rebuild command: `powershell -ExecutionPolicy Bypass -File .\build_latex.ps1`

## Todo List First

- [x] Select the broad paper direction: explainable vision-language AI for construction safety.
- [x] Use the working concept: "Beyond Stable Answers: Auditing Explanation Faithfulness in a Construction-Safety Vision-Language Pipeline."
- [x] Use the short-paper route for peer review and proceedings consideration.
- [ ] Treat this as urgent: the abstract deadline was July 15, 2026. Check EasyChair immediately to see whether the system still accepts a new submission or late abstract.
- [x] Prepare a 4-8 page short-paper submission candidate for the August 1, 2026 deadline.
- [x] Create the first abstract draft, maximum 300 words.
- [ ] Review and revise the abstract with collaborators.
- [x] Make sure the abstract covers:
  - [x] Research motivation or problem statement.
  - [x] Methodology or conceptual framework, if applicable.
  - [x] Key findings or expected contribution.
  - [x] Implications for trustworthy innovation, learning, or human development.
- [x] Create the first short-paper draft with clear sections such as:
  - [x] Introduction.
  - [x] Related Work or Literature Review.
  - [x] Methods or Conceptual Framework.
  - [x] Results, Findings, or Expected Contributions.
  - [x] Discussion.
  - [x] Implications.
  - [x] References.
- [x] Create a conference-formatted LaTeX draft:
  - [x] 8 body pages, with references beginning on page 9 and excluded from the body count.
  - [x] PDF/LaTeX output.
  - [x] Times New Roman.
  - [x] 12-point font.
  - [x] Double-spaced.
  - [x] APA-style in-text citations and references.
  - [x] Visible `DRAFT - NOT CAMERA READY` running header.
- [x] Prepare a double-blind draft version:
  - [x] Remove author names from abstract and paper.
  - [x] Remove affiliations from abstract and paper.
  - [x] Clear the PDF author metadata field.
  - [ ] Enter author details only inside EasyChair.
- [ ] Create or log into EasyChair and submit through the SNAS 2026 portal.
- [ ] Save the submitted files and EasyChair confirmation locally.
- [ ] Wait for author notification by September 1, 2026.
- [ ] If accepted, revise the paper using reviewer feedback.
- [ ] Submit the camera-ready version by September 20, 2026.
- [ ] Register at least one author by September 20, 2026.
- [ ] Decide presentation mode if accepted: in-person, online, oral, panel, or poster depending on assignment.
- [ ] If eligible as a current U.S. doctoral student, prepare a separate SNAS Doctoral Research Grant application and email it to info@snascholars.org.
- [ ] If attending in person, plan travel to George Mason University, Mason Square, Arlington, Virginia for October 9-10, 2026.

## Draft Build Verification

- Status: working draft for technical and advisor review; not camera ready.
- Standalone abstract: 272 words and one rendered page.
- Short paper: eight body pages; references begin on page 9; ten pages total.
- Typography: embedded Times New Roman regular, bold, and italic only.
- Spacing and page setup: 12-point, double-spaced, U.S. letter paper, one-inch margins.
- Review copy: `DRAFT - NOT CAMERA READY` appears in the running header on every page.
- Blind review: no author names or affiliations; PDF author metadata is empty.
- LaTeX verification: no compilation warnings, unresolved cross-references, overfull boxes, or underfull boxes.
- Visual verification: all abstract, body, table, and reference pages rendered and inspected without clipping or overlap.
- Rebuild command: `powershell -ExecutionPolicy Bypass -File .\build_latex.ps1`.

## Key Conference Facts

- Conference: 5th SNAS Interdisciplinary Research Conference.
- Theme: Trustworthy Innovation, Learning, and Human Development in the Age of Intelligent Systems.
- Location: George Mason University, Mason Square, Arlington, Virginia.
- Dates: October 9-10, 2026.
- Format: Hybrid, with in-person sessions and scheduled online presentation sessions.
- Submission portal: EasyChair for SNAS 2026.

## Important Deadlines

- Abstract submission deadline: July 15, 2026.
- Paper submission deadline: August 1, 2026.
- Author notification deadline: September 1, 2026.
- Camera-ready version deadline: September 20, 2026.
- Presenter registration deadline: September 20, 2026.

## Submission Types

### Abstract Submission

Purpose:
- For poster presentation consideration.

Length:
- Maximum 300 words.

Must include:
- Research motivation or problem statement.
- Methodology or conceptual framework, if applicable.
- Key findings or expected contributions.
- Implications for trustworthy innovation, learning, or human development.

Allowed work types:
- Empirical studies.
- Conceptual analyses.
- Case studies.
- Review papers.
- Work-in-progress research.

Review:
- Double-blind review.

### Short Paper Submission

Purpose:
- Required for peer review.
- Accepted short papers may be presented at the conference and published in the conference proceedings.

Length:
- 4-8 pages.
- References are excluded from the page count.

Format:
- Microsoft Word or PDF/LaTeX.
- Times New Roman.
- 12-point font.
- Double-spaced.
- Clear section headings.
- APA reference format required.

Content expectation:
- The short paper may be work in progress, but it must contain enough detail for peer review.
- It must expand on the submitted abstract.

Evaluation criteria:
- Relevance to the conference theme.
- Clarity and coherence.
- Originality and contribution.
- Methodological rigor, if applicable.
- Interdisciplinary and societal significance.

## Blind Review Requirements

- Do not include author names in the abstract or paper document.
- Do not include affiliations in the abstract or paper document.
- Remove identifying information from document file properties.
- Enter author information separately in EasyChair.

## Conference Proceedings

- SNAS plans to publish proceedings through George Mason's MARS repository.
- To be included, authors must submit a final revised short paper or completed article after reviewer feedback.
- Final proceedings papers must follow the formatting guidance provided to accepted authors.
- At least one author must register before the registration deadline for the accepted paper to be included.
- Accepted papers in proceedings will receive a DOI.

Proceedings formatting currently listed:
- Microsoft Word or PDF/LaTeX.
- Times New Roman.
- 12-point font.
- Double-spaced.
- 4-8 pages, excluding references.

## Presentation Details

Possible presentation formats:
- 15-20 minute oral presentation.
- Moderated panel discussion.
- Poster session.

Detailed instructions will be provided after acceptance.

## Registration Fees

- Non-student registration: $200.
- SNAS member registration: $100.
- Student registration: $100.
- Students from host institution, GMU: $50.

Only registered attendees may participate. SNAS members with active memberships may present accepted work or attend at the reduced fee.

## Doctoral Research Grant

- Grant amount: up to $500.
- Purpose: travel and lodging reimbursement.
- Eligibility: current U.S. doctoral students.
- Application: separate application required by email to info@snascholars.org, in addition to the conference submission.
- Award depends on both acceptance of the conference abstract and approval of the grant application.
- Reimbursement requires proof of student status and expense receipts.

## Topic Fit Checklist

The paper should clearly connect to at least one of these areas:

- Trustworthy AI and responsible innovation.
- Transparency, explainability, and accountability in intelligent systems.
- Algorithmic bias, fairness, and inclusive design.
- Governance or regulation for emerging technologies.
- AI risk assessment, safety, or resilience.
- Cybersecurity, privacy, digital trust, or system integrity.
- Misinformation, deepfakes, or digital manipulation.
- Surveillance, civil liberties, or ethical data governance.
- Blockchain, distributed systems, or trust architectures.
- AI-enhanced education or adaptive learning.
- Digital literacy, AI literacy, or workforce transformation.
- Human-centered educational technology.
- Human-machine collaboration and augmented intelligence.
- Psychology of AI interaction.
- Cognitive, emotional, or social implications of automation.
- Human identity, agency, or self-perception in digitally mediated environments.
- AI in healthcare, diagnostics, personalized medicine, or clinical decision support.
- Ethical health data analytics.
- Public-sector innovation or societal resilience.
- Future of work in AI-driven economies.
- Social inequality and technological access.
- Institutional trust in automation.
- Sustainable innovation ecosystems.

## Immediate Risk Notes

- The abstract deadline listed on the conference page is July 15, 2026. Since this checklist was prepared on July 16, 2026, verify in EasyChair immediately whether late/new submissions are still accepted.
- The EasyChair page says new paper submission for SNAS 2026 is open, but actual submission fields and closing behavior require logging in.
- If the system requires a separate abstract before paper upload, contact the organizers immediately at info@snascholars.org and ask whether a short paper can still be submitted.

## Recommended Local Files to Create Next

- `abstract.md` - 300-word double-blind abstract.
- `paper_draft.md` or `paper_draft.docx` - short paper working draft.
- `references.bib` or `references.md` - APA reference tracker.
- `submission_metadata.md` - title, authors, affiliations, keywords, EasyChair notes, and submission confirmation.
- `blind_review_checklist.md` - pre-submission anonymity and formatting check.
