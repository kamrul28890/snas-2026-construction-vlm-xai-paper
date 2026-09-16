"""Report the page budget for the SNAS camera-ready manuscript.

The venue allows 8 body pages excluding references (confirmed with the program
chair on 2026-09-15). This prints where the reference list starts, which is what
turns a total page count into the body count the limit actually applies to, plus
per-section source-word counts against the targets in the compression plan so a
pass can see which section is still over.

Usage:
    python experiments/page_budget.py
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

# Source-word targets from docs/superpowers/plans/2026-09-15-snas-8-page-compression.md
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
    """Return (section, prose words, float words) in document order.

    Float contents are counted separately because a table of numbers is not
    prose a compression pass can rewrite.
    """
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
    try:
        out = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True)
    except FileNotFoundError:
        return None
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
        print(f"{name:<40}{prose:>7}{target or '-':>8}"
              f"{(f'{prose - target:+d}') if target else '-':>7}")
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
