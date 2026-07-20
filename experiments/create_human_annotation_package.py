"""Create a clean human-annotation package with instructions, CSV, and images."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001.csv",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "output" / "human_annotation_package",
    )
    parser.add_argument("--package-name", default="human_audit_batch_001_package")
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=ROOT.parent / "Explainable-AI-Mustafa-Abdallah",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    package = (output_root / args.package_name).resolve()
    if ROOT not in package.parents:
        raise RuntimeError(f"Refusing to write outside workspace: {package}")
    if package.exists():
        shutil.rmtree(package)
    images_dir = package / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(args.batch)
    clean_rows, image_ids = build_clean_rows(rows)
    write_clean_csv(package / "human_audit_batch_001_for_annotator.csv", clean_rows)
    copy_instruction_files(package)
    write_readme(package)
    export_images(args.source_repo.resolve(), image_ids, images_dir)
    write_package_manifest(package, row_count=len(clean_rows), image_count=len(image_ids))
    zip_path = write_zip(package)
    print(json.dumps({"package_dir": str(package), "zip_path": str(zip_path), "rows": len(clean_rows), "images": len(image_ids)}, indent=2))
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_clean_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], set[str]]:
    clean_rows = []
    image_ids: set[str] = set()
    for row in rows:
        image_id = row["image_id"]
        image_ids.add(image_id)
        clean_rows.append(
            {
                "audit_id": row["audit_id"],
                "image_id": image_id,
                "image_file": f"images/{image_id}.jpg",
                "rule_id": row["rule_id"],
                "question": row["question"],
                "image_width": row["image_width"],
                "image_height": row["image_height"],
                "image_caption": row["image_caption"],
                "answer_label": "",
                "evidence_regions_xyxy": "",
                "ambiguous": "",
                "notes": "",
            }
        )
    return clean_rows, image_ids


def write_clean_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "audit_id",
        "image_id",
        "image_file",
        "rule_id",
        "question",
        "image_width",
        "image_height",
        "image_caption",
        "answer_label",
        "evidence_regions_xyxy",
        "ambiguous",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def copy_instruction_files(package: Path) -> None:
    source = ROOT / "benchmark" / "annotations"
    for name in ["human_annotation_prompt.md", "human_audit_protocol.md"]:
        shutil.copy2(source / name, package / name)


def write_readme(package: Path) -> None:
    (package / "README_START_HERE.md").write_text(
        "# Human Annotation Package\n\n"
        "Start with `human_annotation_prompt.md`. Fill only `human_audit_batch_001_for_annotator.csv`.\n\n"
        "Use the `image_file` column to open the corresponding image under `images/`.\n\n"
        "Return the completed CSV after filling these columns: `answer_label`, "
        "`evidence_regions_xyxy`, `ambiguous`, and `notes`.\n\n"
        "Do not add model predictions, bootstrap labels, or diagnostic scores. "
        "This package intentionally excludes them.\n",
        encoding="utf-8",
    )


def export_images(source_repo: Path, image_ids: set[str], images_dir: Path) -> None:
    sys.path.insert(0, str(source_repo / "pilot" / "src"))
    from xai_pilot.data import load_construction_site

    found: set[str] = set()
    for row in load_construction_site(split="test", streaming=True):
        image_id = str(row["image_id"]).zfill(7)
        if image_id not in image_ids:
            continue
        row["image"].convert("RGB").save(images_dir / f"{image_id}.jpg", quality=95)
        found.add(image_id)
        if len(found) == len(image_ids):
            break
    missing = sorted(image_ids - found)
    if missing:
        raise RuntimeError(f"Missing {len(missing)} images: {missing[:10]}")


def write_package_manifest(package: Path, *, row_count: int, image_count: int) -> None:
    manifest = {
        "package_id": package.name,
        "row_count": row_count,
        "image_count": image_count,
        "annotator_csv": "human_audit_batch_001_for_annotator.csv",
        "instructions": "human_annotation_prompt.md",
        "protocol": "human_audit_protocol.md",
        "image_folder": "images",
        "excluded_columns": [
            "model_assisted_answer_label",
            "florence_predicted_answer",
            "florence_answer_correct",
            "priority_score",
            "priority_reason",
            "source_violation_boxes_xyxy",
            "model_assisted_evidence_regions_xyxy",
        ],
    }
    (package / "package_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_zip(package: Path) -> Path:
    zip_path = package.parent / f"{package.name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(package.rglob("*")):
            if path.is_file():
                handle.write(path, path.relative_to(package.parent))
    return zip_path


if __name__ == "__main__":
    raise SystemExit(main())
