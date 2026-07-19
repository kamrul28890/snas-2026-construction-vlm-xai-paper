"""Build a SHA-256 manifest for benchmark and paper artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INCLUDE_ROOTS = [
    "benchmark",
    "experiments",
    "paper/neurips",
    "results/frozen_model_outputs",
    "results/intervention_outputs",
    "results/tables",
    "src/faithbench",
    "tests",
]

EXCLUDE_SUFFIXES = {
    ".aux",
    ".bbl",
    ".blg",
    ".log",
    ".out",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_artifacts() -> list[Path]:
    paths: list[Path] = []
    for root in INCLUDE_ROOTS:
        base = ROOT / root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in EXCLUDE_SUFFIXES:
                continue
            paths.append(path)
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def main() -> int:
    artifacts = []
    for path in iter_artifacts():
        rel = path.relative_to(ROOT).as_posix()
        artifacts.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    manifest = {
        "manifest_version": "0.1.0",
        "description": "Frozen artifact manifest for the ConstructionSafety-FaithBench scaffold.",
        "artifact_count": len(artifacts),
        "include_roots": INCLUDE_ROOTS,
        "artifacts": artifacts,
    }
    output = ROOT / "results" / "release_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    print(f"Wrote {len(artifacts)} artifact hashes to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
