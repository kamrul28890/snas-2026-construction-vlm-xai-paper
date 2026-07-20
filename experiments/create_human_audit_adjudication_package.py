"""Create a focused adjudication package for audit-pass disagreements."""

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
        "--disagreements",
        type=Path,
        default=ROOT / "benchmark" / "annotations" / "human_audit_batch_001_ai_disagreements.csv",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "output" / "human_audit_adjudication_package",
    )
    parser.add_argument("--package-name", default="human_audit_batch_001_adjudication_package")
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=ROOT.parent / "Explainable-AI-Mustafa-Abdallah",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    args = parse_args()
    package = (args.output_root / args.package_name).resolve()
    if ROOT not in package.parents:
        raise RuntimeError(f"Refusing to write outside workspace: {package}")
    if package.exists():
        shutil.rmtree(package)
    package.mkdir(parents=True)
    images_dir = package / "images"
    images_dir.mkdir()

    batch_by_audit_id = {row["audit_id"]: row for row in read_csv(args.batch)}
    disagreement_rows = read_csv(args.disagreements)
    adjudication_rows = build_adjudication_rows(disagreement_rows, batch_by_audit_id)
    write_csv(package / "adjudication_form.csv", adjudication_rows, list(adjudication_rows[0].keys()))
    copy_context_files(package)
    write_readme(package)
    write_manifest(package, row_count=len(adjudication_rows))
    export_images(args.source_repo.resolve(), {row["image_id"] for row in adjudication_rows}, images_dir)
    zip_path = write_zip(package)
    print(json.dumps({"package_dir": str(package), "zip_path": str(zip_path), "rows": len(adjudication_rows)}, indent=2))
    return 0


def build_adjudication_rows(
    disagreement_rows: list[dict[str, str]],
    batch_by_audit_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows = []
    for disagreement in disagreement_rows:
        batch_row = batch_by_audit_id[disagreement["audit_id"]]
        image_id = batch_row["image_id"]
        rows.append(
            {
                "audit_id": batch_row["audit_id"],
                "image_id": image_id,
                "image_file": f"images/{image_id}.jpg",
                "rule_id": batch_row["rule_id"],
                "question": batch_row["question"],
                "image_width": batch_row["image_width"],
                "image_height": batch_row["image_height"],
                "image_caption": batch_row["image_caption"],
                "annotator_1_answer_label": batch_row["annotator_1_answer_label"],
                "annotator_1_evidence_regions_xyxy": batch_row["annotator_1_evidence_regions_xyxy"],
                "annotator_1_ambiguous": batch_row["annotator_1_ambiguous"],
                "annotator_1_notes": batch_row["annotator_1_notes"],
                "annotator_2_answer_label": batch_row["annotator_2_answer_label"],
                "annotator_2_evidence_regions_xyxy": batch_row["annotator_2_evidence_regions_xyxy"],
                "annotator_2_ambiguous": batch_row["annotator_2_ambiguous"],
                "annotator_2_notes": batch_row["annotator_2_notes"],
                "adjudicated_answer_label": "",
                "adjudicated_evidence_regions_xyxy": "",
                "adjudicated_ambiguous": "",
                "adjudication_notes": "",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def copy_context_files(package: Path) -> None:
    source = ROOT / "benchmark" / "annotations"
    mappings = {
        "human_annotation_prompt.md": "human_annotation_prompt.md",
        "human_audit_protocol.md": "human_audit_protocol.md",
        "human_audit_batch_001_ai_personas.md": "ai_annotator_personas.md",
        "human_audit_batch_001_ai_disagreement_analysis.md": "ai_disagreement_analysis.md",
        "human_audit_batch_001_ai_disagreements.csv": "ai_disagreements.csv",
    }
    for source_name, target_name in mappings.items():
        shutil.copy2(source / source_name, package / target_name)


def write_readme(package: Path) -> None:
    (package / "README_START_HERE.md").write_text(
        "# Human Audit Adjudication Package\n\n"
        "This package contains only the 12 rows where the two independent AI-generated audit passes disagreed.\n\n"
        "Open `adjudication_form.csv` and fill only these fields:\n\n"
        "- `adjudicated_answer_label`: `compliant`, `violation`, or `uncertain`.\n"
        "- `adjudicated_evidence_regions_xyxy`: JSON boxes supporting the final decision, or `[]`.\n"
        "- `adjudicated_ambiguous`: `yes` or `no`.\n"
        "- `adjudication_notes`: one short explanation of the decision.\n\n"
        "Use the image, rule/question, and both annotator notes. The source annotations are AI-generated and should be treated as competing recommendations, not ground truth.\n",
        encoding="utf-8",
    )


def write_manifest(package: Path, *, row_count: int) -> None:
    manifest = {
        "package_id": package.name,
        "row_count": row_count,
        "image_count": row_count,
        "adjudication_csv": "adjudication_form.csv",
        "image_folder": "images",
        "ground_truth_status": "pending_human_or_domain_adjudication",
        "source_disagreements": "benchmark/annotations/human_audit_batch_001_ai_disagreements.csv",
    }
    (package / "package_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


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
