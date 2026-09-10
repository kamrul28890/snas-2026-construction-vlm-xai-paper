"""Rewrite machine-specific absolute paths in generated JSON summaries.

Generated summaries record the paths they were written from. Those paths are
absolute, so publishing them would expose local directory layout, including
sibling project directories outside this repository. This script rewrites
in-repo paths as repository-relative and redacts everything else.

Run before publishing the reproducibility repository. It is idempotent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEARCH_GLOBS = (
    "benchmark/**/*.json",
    "results/**/*.json",
    "analysis/**/*.json",
)

EXTERNAL_PLACEHOLDER = "<external-annotation-package>"


def looks_absolute(value: str) -> bool:
    if len(value) > 2 and value[1] == ":" and value[2] in ("\\", "/"):
        return True
    return value.startswith("\\\\")


def sanitize(value: str) -> str:
    """Return a portable form of one absolute path string."""
    normalized = value.replace("\\", "/")
    root = str(ROOT).replace("\\", "/")
    if normalized.lower().startswith(root.lower()):
        relative = normalized[len(root) :].lstrip("/")
        return relative or "."
    # Path outside this repository: keep the trailing component for provenance,
    # drop everything that identifies the machine it came from.
    tail = normalized.rstrip("/").rsplit("/", 1)[-1]
    return f"{EXTERNAL_PLACEHOLDER}/{tail}"


def walk(node):
    """Recursively sanitize absolute path strings, returning (node, count)."""
    if isinstance(node, dict):
        changed = 0
        result = {}
        for key, value in node.items():
            result[key], delta = walk(value)
            changed += delta
        return result, changed
    if isinstance(node, list):
        changed = 0
        result = []
        for value in node:
            new_value, delta = walk(value)
            result.append(new_value)
            changed += delta
        return result, changed
    if isinstance(node, str) and looks_absolute(node):
        return sanitize(node), 1
    return node, 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report offending files without modifying them; exit 1 if any remain.",
    )
    args = parser.parse_args()

    offenders = 0
    for pattern in SEARCH_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            try:
                original = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

            updated, changed = walk(original)
            if not changed:
                continue

            offenders += 1
            relative = path.relative_to(ROOT).as_posix()
            if args.check:
                print(f"absolute paths present: {relative} ({changed})")
                continue

            path.write_text(
                json.dumps(updated, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"sanitized: {relative} ({changed})")

    if args.check and offenders:
        raise SystemExit(1)
    if not offenders:
        print("no absolute paths found")


if __name__ == "__main__":
    main()
