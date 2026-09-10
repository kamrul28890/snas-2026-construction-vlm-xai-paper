"""Regenerate the IEEE two-column manuscript from the SNAS-format manuscript.

The SNAS file is the single source of truth for prose. This script rebuilds the
IEEE variant from it so the two cannot drift apart: it swaps the preamble and
author block, converts APA citations to IEEE numbered references ordered by
first appearance, and adjusts float widths for a two-column measure.

Run after editing SNAS_2026_FaithBench_short_paper.tex:

    python experiments/build_ieee_variant.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "paper" / "snas" / "SNAS_2026_FaithBench_short_paper.tex"
DST = ROOT / "paper" / "snas" / "SNAS_2026_FaithBench_camera_ready_ieee.tex"

# APA citation string -> bib key(s). Order here is irrelevant; IEEE numbering is
# derived from order of first appearance in the body.
CITES = [
    (r"\(U\.S\. Bureau of Labor Statistics, 2026\)", "bls2024"),
    (r"\(Occupational Safety and Health Administration, n\.d\.\)", "osha"),
    (r"\(Chen \\& Zou, 2025\)", "chen2025"),
    (r"\(Li et al\., 2025\)", "li2025"),
    (r"\(Villa et al\., 2025\)", "villa2025"),
    (r"\(Jain \\& Wallace, 2019; Wu et al\., 2024\)", "jain2019,wu2024"),
    (r"\(Wu et al\., 2024\)", "wu2024"),
    (r"\(Phillips et al\., 2021\)", "phillips2021"),
    (r"\(Xiao et al\., 2024\)", "xiao2024"),
    (
        r"\(National Institute of Standards and Technology, 2023; Howard \\& Schulte, 2024\)",
        "nist2023,howard2024",
    ),
]

BIB = {
    "bls2024": r"U.S. Bureau of Labor Statistics, \emph{Census of Fatal Occupational Injuries Summary, 2024}, U.S. Department of Labor, Feb. 2026. [Online]. Available: https://www.bls.gov/news.release/cfoi.nr0.htm",
    "osha": r"Occupational Safety and Health Administration, ``Construction focus four training,'' U.S. Department of Labor. [Online]. Available: https://www.osha.gov/training/outreach/construction/focus-four",
    "chen2025": r"X. Chen and Z. Zou, ``Are large pre-trained vision language models effective construction safety inspectors?'' \emph{arXiv:2508.11011}, 2025.",
    "li2025": r"K. Li, G. Vosselman, and M. Y. Yang, ``Multimodal rationales for explainable visual question answering,'' in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW)}, 2025, pp. 191--201.",
    "villa2025": r"A. Villa, J. C. Le\'{o}n Alc\'{a}zar, A. Soto, and B. Ghanem, ``Behind the magic, MERLIM: Multi-modal evaluation benchmark for large image-language models,'' in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW)}, 2025.",
    "jain2019": r"S. Jain and B. C. Wallace, ``Attention is not explanation,'' in \emph{Proc. NAACL-HLT}, 2019, pp. 3543--3556.",
    "wu2024": r"J. Wu, W. Kang, H. Tang, Y. Hong, and Y. Yan, ``On the faithfulness of vision transformer explanations,'' in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)}, 2024, pp. 10936--10945.",
    "phillips2021": r"P. J. Phillips, C. A. Hahn, P. C. Fontana, A. N. Yates, K. Greene, D. A. Broniatowski, and M. A. Przybocki, ``Four principles of explainable artificial intelligence,'' National Institute of Standards and Technology, NISTIR 8312, 2021.",
    "xiao2024": r"B. Xiao, H. Wu, W. Xu, X. Dai, H. Hu, Y. Lu, M. Zeng, C. Liu, and L. Yuan, ``Florence-2: Advancing a unified representation for a variety of vision tasks,'' in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)}, 2024, pp. 4818--4829.",
    "nist2023": r"National Institute of Standards and Technology, \emph{Artificial Intelligence Risk Management Framework (AI RMF 1.0)}, 2023.",
    "howard2024": r"J. Howard and P. A. Schulte, ``Exploring approaches to keep an AI-enabled workplace safe for workers,'' National Institute for Occupational Safety and Health, 2024.",
}

# Floats wide enough to need both columns. Everything else is set single-column,
# which keeps whitespace down and the body inside the page budget.
FULL_WIDTH = ("fig:pipeline", "fig:audit", "fig:intervention")

# Column specs retuned for the narrower two-column measure.
COLUMN_REWRITES = [
    ("L{0.9in}L{1.7in}L{1.6in}L{0.8in}", "L{0.62in}L{1.15in}L{1.05in}L{0.52in}"),
    ("L{1.35in}rrrr", "L{0.95in}rrrr"),
]

PREAMBLE = r"""% SNAS 2026 camera-ready short paper - IEEE conference format.
% GENERATED FILE. Edit SNAS_2026_FaithBench_short_paper.tex and re-run
% experiments/build_ieee_variant.py; direct edits here will be overwritten.
% Compile with pdflatex (three passes, for float placement).
\documentclass[conference]{IEEEtran}
\IEEEoverridecommandlockouts

\usepackage{cite}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\PassOptionsToPackage{hyphens}{url}
\usepackage[hidelinks]{hyperref}
\urlstyle{same}

% Let floats occupy more of a page before LaTeX defers them, which avoids the
% large whitespace gaps that full-width floats otherwise leave in two columns.
\renewcommand{\topfraction}{0.92}
\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.07}
\renewcommand{\floatpagefraction}{0.75}
\renewcommand{\dbltopfraction}{0.92}
\renewcommand{\dblfloatpagefraction}{0.75}

\hypersetup{
  pdftitle={@@TITLE_META@@},
  pdfauthor={Md Kamruzzaman, Eashraque Jahan, Mustafa Abdallah},
  pdfsubject={SNAS 2026 camera-ready short paper},
  pdfkeywords={trustworthy AI, explainable AI, vision-language models, construction safety, evidence sensitivity}
}

\begin{document}

\title{@@TITLE_TEX@@}

\author{
\IEEEauthorblockN{Md Kamruzzaman}
\IEEEauthorblockA{\textit{Purdue University}\\
West Lafayette, IN, USA\\
kamrul28890@gmail.com}
\and
\IEEEauthorblockN{Eashraque Jahan}
\IEEEauthorblockA{\textit{University of Denver}\\
Denver, CO, USA\\
easha003eee@du.edu}
\and
\IEEEauthorblockN{Mustafa Abdallah}
\IEEEauthorblockA{\textit{Purdue University}\\
West Lafayette, IN, USA\\
abdalla0@purdue.edu}
}

\maketitle

\begin{abstract}
ABSTRACT_PLACEHOLDER
\end{abstract}

\begin{IEEEkeywords}
KEYWORDS_PLACEHOLDER
\end{IEEEkeywords}

"""


def widen(match: re.Match) -> str:
    env, inner = match.group(1), match.group(3)
    star = "*" if any(label in inner for label in FULL_WIDTH) else ""
    return f"\\begin{{{env}{star}}}[tb]{inner}\\end{{{env}{star}}}"


def main() -> None:
    text = SRC.read_text(encoding="utf-8")

    title = re.search(
        r"\\begin\{center\}\s*\\textbf\{(.*?)\}\s*\\end\{center\}", text, re.S
    ).group(1)
    title = " ".join(title.split())

    abstract = re.search(
        r"\\textbf\{Abstract\}\s*\\end\{center\}\s*(.*?)\s*\\noindent\\textit\{Keywords:\}",
        text,
        re.S,
    ).group(1).strip()

    keywords = re.search(r"\\noindent\\textit\{Keywords:\}\s*(.*?)\n\s*\n", text, re.S)
    keywords = keywords.group(1).strip().replace(";", ",") if keywords else ""

    body = text[text.index(r"\section{Introduction}") : text.index(r"\section*{References}")]

    # Citations -> \cite{}
    body = re.sub(r"\(Chen \\& Zou,\s*\n?\s*2025\)", r"\\cite{chen2025}", body)
    for pattern, key in CITES:
        body = re.sub(pattern, r"\\cite{" + key + "}", body)

    order: list[str] = []
    for match in re.finditer(r"\\cite\{([^}]+)\}", body):
        for key in match.group(1).split(","):
            if key not in order:
                order.append(key)

    missing = [k for k in order if k not in BIB]
    if missing:
        raise SystemExit(f"no bibliography entry for: {missing}")
    uncited = [k for k in BIB if k not in order]
    if uncited:
        raise SystemExit(f"bibliography entry never cited: {uncited}")

    # Floats
    body = re.sub(
        r"\\begin\{(figure|table)\}(\[[^\]]*\])?(.*?)\\end\{\1\}", widen, body, flags=re.S
    )

    # Single-spacing wrappers are redundant in IEEE; tighten small tables further.
    body = body.replace(r"{\setstretch{1.0}\small", "{\\footnotesize")
    body = body.replace(r"{\setstretch{1.0}", "{\\footnotesize")
    body = body.replace(r"\linewidth", r"\textwidth")
    body = body.replace(r"\label{bodyend}", "").replace(r"\clearpage", "")
    for old, new in COLUMN_REWRITES:
        body = body.replace(old, new)

    # Full-width figures span the page; the rest fit one column.
    def fix_graphic(match: re.Match) -> str:
        block = match.group(0)
        if "figure*" in block:
            return block
        return block.replace(r"width=\textwidth", r"width=\columnwidth")

    body = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", fix_graphic, body, flags=re.S)

    # The centred URL block reads better inline in a narrow column.
    body = re.sub(
        r"available at:\s*\n\s*\n\\begin\{center\}\s*\{?\\?f?o?o?t?n?o?t?e?s?i?z?e?\s*"
        r"(\\url\{[^}]+\})\\par\}\s*\\end\{center\}\s*\n\s*\n\\noindent ",
        lambda m: f"available at\n{m.group(1)}.\n",
        body,
    )

    out = PREAMBLE.replace("ABSTRACT_PLACEHOLDER", abstract)
    out = out.replace("KEYWORDS_PLACEHOLDER", keywords)
    out = out.replace("@@TITLE_META@@", title)
    # Break the running title across two lines at a sensible point.
    words = title.split()
    mid = len(words) // 2
    out = out.replace("@@TITLE_TEX@@", " ".join(words[:mid]) + r"\\" + " ".join(words[mid:]))

    out += body.strip() + "\n\n\\begin{thebibliography}{99}\n"
    for key in order:
        out += f"\\bibitem{{{key}}} {BIB[key]}\n\n"
    out += "\\end{thebibliography}\n\n\\end{document}\n"

    DST.write_text(out, encoding="utf-8")
    print(f"wrote {DST.relative_to(ROOT).as_posix()}")
    print(f"citations in IEEE order ({len(order)}): {', '.join(order)}")


if __name__ == "__main__":
    main()
