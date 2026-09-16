# SNAS 2026 Camera-Ready: 21 → 8 Pages Compression Plan

**Goal:** Reduce the camera-ready manuscript from 21 pages to 8 body pages (references excluded) by densifying prose and consolidating floats, preserving every scientific claim, number, and reviewer-requested addition.

**Approach:** Six phases, each ending in a rebuild and a measured page count. Early phases are information-preserving (redundancy, scaffolding, float layout). Later phases require explicit content decisions, which are flagged for the author rather than made unilaterally.

**Source of truth:** `paper/snas/SNAS_2026_FaithBench_short_paper.tex`

**Verification after every phase:** `.\build_latex.ps1`, then `python experiments/page_budget.py`, then `python experiments/validate_all.py`.

---

## Global Constraints

- **Limit:** 8 body pages, references excluded. Taken from `SNAS_2026_submission_todo.md:199` ("4-8 pages, excluding references"), the original call. **Not restated in the camera-ready email or either 2026 template — confirm with the chair before Phase 4.**
- **Format is fixed.** The official SNAS template governs: single-column `article`, 12pt, letter, 1in margins, `newtxtext`, `\onehalfspacing`, `apacite`. Do not reach for page savings by changing margins, font size, or line spacing. The Word template's Normal style is double-spaced (`w:line="480"`), so `\onehalfspacing` is already more generous to us than the organizers' own Word template. Tightening further is a visible format deviation.
- **Do not touch the two preamble guards** `\let\Bbbk\relax` and `\let\openbox\relax`. Removing them makes the document fail to compile.
- **Every number stays traceable.** All reported statistics are regenerated from the public artifacts. Compression may not alter a single figure, percentage, or count.
- **Reviewer-requested additions are protected.** Review 1 asked for in-text citations, definitions at first use (especially Florence-2), interpreted results, and the repository link. These survive compression; they may be said *shorter*, never removed.
- **Abstract stays ≤300 words** and must remain byte-identical across the manuscript, `SNAS_2026_FaithBench_abstract_blind.tex`, and `SUBMISSION_TEXTS.md`. `validate_manuscript_consistency.py` enforces this and will fail the build if you edit one copy only.

---

## The Budget

Measured from the current 21-page build.

| Item | Current | Notes |
|---|---|---|
| Body prose | 6,079 words | excludes float contents and headings |
| Float contents | 182 words | 3 figures, 5 tables |
| Float vertical space | ~2.0 pages | derived from per-page word deficits |
| Title block + abstract + keywords | ~0.9 page | abstract is 293 words |
| References | ~0.8 page | excluded from the limit |

> **Calibration correction, measured after Phase 3.** The 500-words-per-page figure below was optimistic. Measured against real builds, a full text page holds **~430 PDF-words**, and source words are **0.76×** PDF-words once headings and float contents are excluded. The true source-word budget for 8 body pages is therefore **~2,100**, not 2,735. Phases 1–3 took the paper from 20 to 15 body pages and 6,079 to 4,331 source words — all of it information-preserving — which means the remaining gap must come from **deleting content, not compressing it**. The per-section targets below are consequently ~25% too generous; treat them as upper bounds.

An uninterrupted text page in this format holds **~500 words**. So:

```
8.0 pages   body budget
-0.9        title block + abstract + keywords
-1.3        floats, after Phase 2 consolidation
=5.8 pages  for prose  ->  ~2,900 PDF-words  ->  ~2,400 source-words
```

**Current prose 6,079 → target ~2,700. That is a 56% cut.**

This is the number that matters, and it is worth being blunt about: a cut of this size is not reachable by rewriting sentences alone. Phases 1–3 are genuinely information-preserving and should land around 11–12 pages. Phases 4–5 require deciding what leaves the paper. The public repository is the destination for what goes, so information is *relocated*, not lost — but the paper will say less than it does today.

### Per-section allocation

Targets are source-word counts as reported by `experiments/page_budget.py`.

| Section | Now | Target | Cut | Rationale |
|---|---:|---:|---:|---|
| Abstract | 293 | 200 | −93 | Tighten; keep all five headline numbers |
| 1 Introduction | 1,187 | 400 | −787 | Largest section and the most redundant; states the three-properties framing three separate times |
| 2 Benchmark + 2.1 Images | 220 | 120 | −100 | Schema detail → data card in repo |
| 2.2 The Evaluated Pipeline | 352 | 180 | −172 | Keep the Florence-2 definition Review 1 asked for; cut the model-selection justification |
| 2.3 From Image to Score | 127 | 60 | −67 | Duplicates Figure 1; let the figure carry it |
| 2.4 The Audit Label Layer | 583 | 220 | −363 | Provenance procedure → repo; keep the AI-pass disclosure verbatim |
| 3 Metrics intro | 37 | 20 | −17 | |
| 3.1 Answer Metrics (RQ1) | 131 | 70 | −61 | Standard metrics need no exposition |
| 3.2 Evidence Metrics (RQ2) | 156 | 80 | −76 | Keep the IoU definition |
| 3.3 Intervention Metrics (RQ3) | 553 | 200 | −353 | Protocol detail → repo; keep the size-matched control logic, which is the paper's methodological contribution |
| 4 Results intro | 21 | 15 | −6 | |
| 4.1 Answer Correctness (RQ1) | 174 | 130 | −44 | **Protected** — findings |
| 4.2 Evidence Quality (RQ2) | 211 | 140 | −71 | **Protected** — findings |
| 4.3 Evidence Dependence (RQ3) | 315 | 180 | −135 | **Protected** — headline result |
| 4.4 Qualitative Cases | 124 | 60 | −64 | Compress to one example |
| 5 Discussion and Implications | 519 | 220 | −299 | Cut restatement of results; keep the two-literatures connection |
| 6 Threats to Validity | 643 | 200 | −443 | Convert prose to a dense enumerated list |
| 7 Ethical Considerations | 163 | 90 | −73 | Keep the surveillance and misuse limits |
| 8 Conclusion | 244 | 110 | −134 | Conclusions restate; they do not need to re-argue |
| Reproducibility Statement | 101 | 40 | −61 | Reduce to the link plus the "regenerated not transcribed" claim |
| **Total** | **6,154** | **2,735** | **−3,419** | |

---

## Phase 0: Measurement Harness

No prose changes. Builds the instrument every later phase is judged by.

**Files:** Create `experiments/page_budget.py`

- [ ] **Step 1: Write the script**

```python
"""Report the page budget for the SNAS camera-ready manuscript.

Prints total pages, where the references start (the body-page count that the
venue limit applies to), and per-section source-word counts so a compression
pass can see which section is over its target.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BS = chr(92)
ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "snas" / "SNAS_2026_FaithBench_short_paper.tex"
PDF = ROOT / "output" / "pdf" / "SNAS_2026_FaithBench_short_paper.pdf"

BODY_PAGE_LIMIT = 8

# Source-word targets from the compression plan.
TARGETS = {
    "(title/abstract/keywords)": 200,
    "Introduction": 400,
    "  Images and Safety Rules": 120,
    "  The Evaluated Pipeline": 180,
    "  From Image to Score": 60,
    "  The Audit Label Layer": 220,
    "Metrics and Experimental Setup": 20,
    "  Answer Metrics (RQ1)": 70,
    "  Evidence Metrics (RQ2)": 80,
    "  Intervention Metrics (RQ3)": 200,
    "Results": 15,
    "  Answer Correctness (RQ1)": 130,
    "  Evidence Quality (RQ2)": 140,
    "  Evidence Dependence (RQ3)": 180,
    "  Qualitative Cases": 60,
    "Discussion and Implications": 220,
    "Threats to Validity and Limitations": 200,
    "Ethical Considerations": 90,
    "Conclusion": 110,
    "Reproducibility Statement": 40,
}

CMD = re.compile(re.escape(BS) + r"[a-zA-Z@]+(\[[^\]]*\])?(\{[^{}]*\})?")
PUNCT = re.compile(r"[{}$&" + re.escape(BS) + r"]")


def section_words() -> list[tuple[str, int, int]]:
    """Return (section, prose words, float words) in document order."""
    body = TEX.read_text(encoding="utf-8").split(BS + "begin{document}")[1]
    cur = "(title/abstract/keywords)"
    buf: dict[str, list[int]] = {}
    order: list[str] = []
    infloat = 0

    for line in body.split("\n"):
        head = re.match(r"\s*" + re.escape(BS) + r"(sub)?section\*?\{(.*?)\}", line)
        if head:
            cur = ("  " + head.group(2)) if head.group(1) else head.group(2)
            if cur not in buf:
                buf[cur] = [0, 0]
                order.append(cur)
            continue
        if cur not in buf:
            buf[cur] = [0, 0]
            order.append(cur)
        if re.search(r"begin\{(figure|table)", line):
            infloat += 1
        if re.search(r"end\{(figure|table)", line):
            infloat -= 1
            continue
        text = PUNCT.sub(" ", CMD.sub("", re.sub(r"%.*", "", line)))
        words = len([w for w in text.split() if any(c.isalpha() for c in w)])
        buf[cur][1 if infloat > 0 else 0] += words

    return [(k, buf[k][0], buf[k][1]) for k in order if sum(buf[k]) > 0]


def reference_start_page() -> int | None:
    """Page on which the reference list begins, or None if it cannot be found."""
    out = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True)
    if out.returncode != 0:
        return None
    pages = out.stdout.decode("utf-8", errors="replace").split("\f")
    for i, page in enumerate(pages, 1):
        if re.search(r"^\s*References\s*$", page, re.M):
            return i
    return None


def main() -> int:
    rows = section_words()

    print(f"{'SECTION':<40}{'WORDS':>7}{'TARGET':>8}{'OVER':>7}")
    print("-" * 62)
    total = target_total = 0
    for name, prose, _ in rows:
        target = TARGETS.get(name, 0)
        total += prose
        target_total += target
        over = prose - target
        flag = f"{over:+d}" if target else "-"
        print(f"{name:<40}{prose:>7}{target or '-':>8}{flag:>7}")
    print("-" * 62)
    print(f"{'TOTAL':<40}{total:>7}{target_total:>8}{total - target_total:>+7}")

    if not PDF.exists():
        print("\nNo PDF yet; run .\\build_latex.ps1 first.")
        return 0

    import pypdf

    pages = len(pypdf.PdfReader(str(PDF)).pages)
    refs = reference_start_page()
    print(f"\nTotal pages: {pages}")
    if refs is None:
        print("Could not locate the reference list; body page count unknown.")
        return 0

    body = refs - 1
    verdict = "OK" if body <= BODY_PAGE_LIMIT else f"OVER by {body - BODY_PAGE_LIMIT}"
    print(f"References start on page {refs}, so body = {body} pages "
          f"(limit {BODY_PAGE_LIMIT}): {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it against the current 21-page build**

Run: `python experiments/page_budget.py`
Expected: total ~6,079 words, `TOTAL` line showing roughly +3,400 over target, and `body = 20 pages (limit 8): OVER by 12`.

- [ ] **Step 3: Commit**

```bash
git add experiments/page_budget.py
git commit -m "Add a page-budget instrument for the camera-ready compression"
```

---

## Phase 1: Redundancy (lossless)

Delete only text that says something the paper already says elsewhere. No claim, number, definition, or citation leaves the paper. If a cut requires judgement about value, it belongs in Phase 4, not here.

**Files:** Modify `paper/snas/SNAS_2026_FaithBench_short_paper.tex`

- [ ] **Step 1: Introduction — collapse the triple framing.** The correctness / evidence-relevance / intervention-sensitivity triad is introduced three times: once as a general claim, once as the italicised definition paragraph, once again as RQ1/RQ2/RQ3. Keep the RQ list, which is the version Review 1 asked for, and delete the other two passes. Fold any surviving nuance into the RQ bullets.
- [ ] **Step 2: Introduction — delete the contributions list.** All four bullets restate the abstract and the RQ list. The paper loses no information; it stops saying it a fourth time.
- [ ] **Step 3: Introduction — cut the general-audience scaffolding.** The explanations of what a VLM is and why textual rules beat fixed classifiers are background for a specialist venue. Keep one sentence of motivation.
- [ ] **Step 4: Section 2.3 — let Figure 1 do its job.** "From Image to Score" narrates the figure step by step. Reduce to the two sentences that say something the diagram cannot.
- [ ] **Step 5: Discussion — remove results restatement.** Section 5 re-reports numbers already in Section 4. Cut the restatement; keep the interpretation and the two-literatures connection.
- [ ] **Step 6: Conclusion — stop re-arguing.** Keep the contribution, the headline finding, and the forward-looking sentence.
- [ ] **Step 7: Rebuild and measure.**

Run: `.\build_latex.ps1; python experiments/page_budget.py; python experiments/validate_all.py`
Expected: ~16 pages. All validators pass. **If `validate_manuscript_consistency.py` fails, the abstract was edited in one copy only — fix before continuing.**

- [ ] **Step 8: Commit**

```bash
git add paper/snas/SNAS_2026_FaithBench_short_paper.tex
git commit -m "Cut restated framing and contributions from the camera-ready"
```

---

## Phase 2: Floats and layout (lossless)

Recovers roughly 0.7 page without touching a word of prose.

**Files:** Modify `paper/snas/SNAS_2026_FaithBench_short_paper.tex`

- [ ] **Step 1: Merge Table 4 into Table 3.** Table 3 is the headline results table; Table 4 is the safety-relevant error breakdown on the same 120 rows. One table with a second block removes a caption, a float gap, and a cross-reference.
- [ ] **Step 2: Retire Table 1.** It maps each research question to its experiment, metric, and result — navigational, not evidential, and redundant once the RQ list and section headings carry the same mapping. Delete the float; keep the mapping in the RQ bullets.
- [ ] **Step 3: Constrain figure widths.** All three figures use `width=\linewidth`. Set `width=0.82\textwidth` for Figures 2 and 3, which are charts with generous internal whitespace. Leave Figure 1 at full width; it is the architecture diagram and has the most detail.
- [ ] **Step 4: Tighten float separation.** Add to the preamble, after `\raggedbottom`:

```latex
% Compression: keep floats from opening large vertical gaps.
\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\floatsep}{6pt plus 2pt minus 2pt}
\setlength{\intextsep}{6pt plus 2pt minus 2pt}
```

- [ ] **Step 5: Rebuild, measure, and inspect every float.**

Run: `.\build_latex.ps1; python experiments/page_budget.py`
Expected: ~14–15 pages, zero overfull hboxes.
Then read the pages carrying Figures 1–3 and Tables 2, 3, 5 and confirm nothing is clipped or crowded. Check the log: `grep -c 'Overfull' tmp/pdfs/SNAS_2026_FaithBench_short_paper.log` must print `0`.

- [ ] **Step 6: Commit**

```bash
git add paper/snas/SNAS_2026_FaithBench_short_paper.tex
git commit -m "Consolidate tables and tighten float spacing"
```

---

## Phase 3: Sentence densification (lossless)

Section-by-section rewriting. Same claims, fewer words. Work one section per step so each is separately reviewable, and check the per-section line in `page_budget.py` after each.

The moves that pay, in rough order of yield:

- Merge paired sentences sharing a subject into one clause.
- Replace "It is worth stating plainly that X" / "That requirement separates" / "The broader point is" with the assertion itself.
- Convert enumerated prose into `itemize` only where the list is genuinely parallel; prose is usually denser than a list for two items.
- Delete hedging that repeats a caveat already stated once. The single-system limitation is stated in the abstract, the introduction, the results, and the limitations section. Once in the abstract and once in limitations is sufficient.
- Cut connective sentences that only announce what the next section does.

- [ ] **Step 1: Section 2.4, The Audit Label Layer.** 583 → 220. Keep the AI-pass provenance disclosure word for word: the repo's own risk note requires "two independent audit passes plus returned adjudication" or "adjudicated audit labels with AI-pass provenance", and the paper must not imply human annotators. Move the procedural detail to the repo's data card.
- [ ] **Step 2: Section 3.3, Intervention Metrics.** 553 → 200. Preserve the size-matched control argument in full; it is the methodological contribution. Cut the implementation narration.
- [ ] **Step 3: Section 6, Threats to Validity.** 643 → 200. Convert to a dense enumerated list, one sentence per threat.
- [ ] **Step 4: Section 5, Discussion.** 519 → 220.
- [ ] **Step 5: Section 2.2, The Evaluated Pipeline.** 352 → 180. The Florence-2 definition stays; Review 1 named it specifically.
- [ ] **Step 6: Section 4.3, Evidence Dependence.** 315 → 180. Findings section — cut narration, keep every number.
- [ ] **Step 7: Remaining sections to target.** 2.1, 3.1, 3.2, 4.1, 4.2, 4.4, 7, 8, and the Reproducibility Statement.
- [ ] **Step 8: Rebuild and measure.**

Run: `.\build_latex.ps1; python experiments/page_budget.py; python experiments/validate_all.py`
Expected: ~11–12 pages, most sections at or near target.

- [ ] **Step 9: Commit**

```bash
git add paper/snas/SNAS_2026_FaithBench_short_paper.tex
git commit -m "Densify prose across all sections toward the page budget"
```

---

## Phase 4: Structural reduction (judgement required)

**Confirm the 8-page limit with the chair before starting this phase.** Everything from here costs the paper something. If the limit turns out not to apply, stop after Phase 3 — an 11-page paper that says everything beats an 8-page paper that does not.

- [ ] **Step 1: Flatten Section 2's subsections.** Four subsections across ~580 words carry four headings and four spacing blocks. Merge into one Benchmark section with paragraph lead-ins.
- [ ] **Step 2: Fold the Reproducibility Statement into Ethical Considerations** as a closing paragraph, or into a footnote on the first page.
- [ ] **Step 3: Reduce the abstract to ~200 words.** Keep all five headline numbers (18.3%, 98.8%, 0.058, 39.2% vs 9.2%, 30.0 points). Update all three copies together, then run the consistency check.
- [ ] **Step 4: Decide on Figure 2.** It shows the composition of the 120-row adjudicated set. The same information can be two sentences. Removing it recovers ~0.3 page. **Author decision.**
- [ ] **Step 5: Rebuild and measure.**

Run: `.\build_latex.ps1; python experiments/page_budget.py; python experiments/validate_all.py`
Expected: ~9 pages.

- [ ] **Step 6: Commit**

```bash
git add paper/snas/SNAS_2026_FaithBench_short_paper.tex
git commit -m "Flatten section structure and tighten the abstract"
```

---

## Phase 5: Final triage (author decisions)

Whatever gap remains after Phase 4 is closed by choosing what the paper stops saying. Do not make these calls unilaterally. Present each as an explicit choice with its page value, then apply the ones approved.

Candidates, in the order I would sacrifice them:

1. **Section 4.4, Qualitative Cases** (~0.25 page). Illustrative, not evidential. The repo carries the examples.
2. **The three blind baselines** — manifest-seed, majority-violation, caption-keyword (~0.3 page). Methodologically valuable as a floor, but the table can carry them without the prose.
3. **Section 2.1's schema detail** (~0.2 page). The data card in the repo is the canonical description.
4. **Table 5, scale-up by rule family** (~0.2 page). The scale-up split is secondary to the 120-row audit.
5. **The faithfulness caveat paragraph** in the introduction (~0.2 page). Intellectually the most careful passage in the paper, which is exactly why it should be the last thing cut.

- [ ] **Step 1: Present the remaining gap and this list to the author; get explicit approval per item.**
- [ ] **Step 2: Apply approved cuts.**
- [ ] **Step 3: Rebuild and confirm body ≤ 8 pages.**
- [ ] **Step 4: Commit**

---

## Phase 6: Verification

- [ ] **Step 1: Clean rebuild from an empty temp directory.**

```powershell
Remove-Item -Recurse -Force .\tmp\pdfs -ErrorAction SilentlyContinue
.\build_latex.ps1
```

- [ ] **Step 2: Confirm the build is clean.**

Run: `grep -c 'Overfull' tmp/pdfs/SNAS_2026_FaithBench_short_paper.log` → expect `0`
Run: `grep -ci 'undefined' tmp/pdfs/SNAS_2026_FaithBench_short_paper.log` → expect `0`

- [ ] **Step 3: Confirm the budget.**

Run: `python experiments/page_budget.py` → expect `body = 8 pages (limit 8): OK`

- [ ] **Step 4: Confirm nothing scientific drifted.**

Run: `python experiments/validate_all.py` → all validators and 37 tests pass.

- [ ] **Step 5: Verify every citation still resolves.** All 11 bib keys must still be cited; a section cut can orphan a reference. Check that `grep -o 'citep{[^}]*}' paper/snas/SNAS_2026_FaithBench_short_paper.tex` still covers every key in `references.bib`, and remove any entry that is no longer cited.

- [ ] **Step 6: Read the full PDF.** Every page, looking for orphaned headings, widow lines, clipped floats, and paragraphs that lost their connective tissue during densification.

- [ ] **Step 7: Confirm the reported numbers by eye** against `results/tables/` — the compression touched the sentences around them.

---

## Risks

- **Densification damages readability.** Review 1's core complaint was that the manuscript was *incoherent*. Compressing hard can reintroduce exactly that. Phase 6 Step 6 is the guard, and it is not optional.
- **The limit may not apply.** Phases 4 and 5 destroy work that cannot be cheaply recovered. Confirm first.
- **The abstract has three copies.** Any abstract edit that skips the other two fails the build.
- **Cuts can orphan citations.** Review 1 explicitly asked for in-text citations; dropping a section can silently strip one. Phase 6 Step 5 catches it.
