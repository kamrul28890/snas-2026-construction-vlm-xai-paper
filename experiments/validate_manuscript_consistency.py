"""Check that the manuscript files agree with each other.

The title and abstract exist in four places: the SNAS manuscript, the generated
IEEE variant, the standalone abstract, and the copy-paste submission text. They
have drifted apart twice, once leaving a superseded abstract in the file meant
for pasting into the submission portal, and once leaving a retracted claim in
the title of two files after the paper itself had been retitled.

This checks that they match, that the abstract respects the venue word limit,
and that no file still carries the superseded title. Exits nonzero on failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "paper" / "snas"

SNAS = PAPER_DIR / "SNAS_2026_FaithBench_short_paper.tex"
IEEE = PAPER_DIR / "SNAS_2026_FaithBench_camera_ready_ieee.tex"
STANDALONE = PAPER_DIR / "SNAS_2026_FaithBench_abstract_blind.tex"
SUBMISSION = PAPER_DIR / "SUBMISSION_TEXTS.md"

ABSTRACT_WORD_LIMIT = 300

# Titles the project has moved away from. Any reappearance means a file was
# updated in isolation.
RETIRED_TITLE_FRAGMENTS = (
    "Auditing Visual-Evidence Faithfulness",
    "Beyond Stable Answers",
)


def normalize(text: str) -> str:
    text = text.replace("\\%", "%").replace("\\&", "&")
    text = text.replace("``", '"').replace("''", '"').replace('"', "")
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def extract(pattern: str, text: str, source: str) -> str:
    match = re.search(pattern, text, re.S)
    if not match:
        raise SystemExit(f"consistency check could not parse {source}")
    return match.group(1).strip()


def main() -> int:
    failures: list[str] = []

    snas = SNAS.read_text(encoding="utf-8")
    abstracts = {
        "SNAS manuscript": extract(
            r"\\textbf\{Abstract\}\s*\\end\{center\}\s*(.*?)\s*\\noindent\\textit\{Keywords:\}",
            snas, "SNAS manuscript"),
        "IEEE variant": extract(
            r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
            IEEE.read_text(encoding="utf-8"), "IEEE variant"),
        "standalone abstract": extract(
            r"\\textbf\{Abstract\}\s*\\end\{center\}\s*(.*?)\s*\\end\{document\}",
            STANDALONE.read_text(encoding="utf-8"), "standalone abstract"),
        "submission texts": extract(
            r"(Construction safety depends on small.*?its accuracy\.)",
            SUBMISSION.read_text(encoding="utf-8"), "submission texts"),
    }

    reference_name = "SNAS manuscript"
    reference = normalize(abstracts[reference_name])
    for name, text in abstracts.items():
        if normalize(text) != reference:
            failures.append(f"abstract in {name} differs from {reference_name}")

    words = len(reference.split())
    if words > ABSTRACT_WORD_LIMIT:
        failures.append(f"abstract is {words} words, over the {ABSTRACT_WORD_LIMIT}-word limit")

    title = extract(r"\\begin\{center\}\s*\\textbf\{(.*?)\}\s*\\end\{center\}", snas, "title")
    title_norm = normalize(title)
    for path in (IEEE, STANDALONE, SUBMISSION):
        if title_norm not in normalize(path.read_text(encoding="utf-8")):
            failures.append(f"title in {path.name} does not match the SNAS manuscript")

    for path in (SNAS, IEEE, STANDALONE, SUBMISSION):
        content = path.read_text(encoding="utf-8")
        for fragment in RETIRED_TITLE_FRAGMENTS:
            if fragment in content:
                failures.append(f"{path.name} still contains retired title text: {fragment!r}")

    if failures:
        print("Manuscript consistency check FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        print("\nIf the SNAS manuscript is correct, regenerate and resync:")
        print("  python experiments/build_ieee_variant.py")
        return 1

    print(f"Manuscript consistency OK (abstract {words} words, "
          f"identical across {len(abstracts)} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
