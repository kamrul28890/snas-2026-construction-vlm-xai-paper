"""Run targeted and same-size random-location occlusion for the SNAS paper.

This script imports the existing XAI pilot read-only. It writes all new artifacts
to this paper workspace and never modifies the source research repository.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import pandas as pd
from PIL import Image

from paper_analysis import clip_box, same_size_random_box


DEFAULT_SEEDS = [42, 43, 44, 45, 46]


def parse_args() -> argparse.Namespace:
    paper_root = Path(__file__).resolve().parents[1]
    default_source = paper_root.parent / "Explainable-AI-Mustafa-Abdallah"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path, default=default_source)
    parser.add_argument("--output", type=Path, default=paper_root / "analysis" / "outputs" / "matched_random_occlusion.csv")
    parser.add_argument("--sample-audit", type=Path, default=paper_root / "analysis" / "outputs" / "sample_audit.csv")
    parser.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    parser.add_argument("--decoding", choices=["beam", "greedy"], default="beam")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def mask_box(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    """Apply the pilot's exclusive x1/y1 black-mask semantics exactly."""
    out = image.convert("RGB").copy()
    x0, y0, x1, y1 = box
    patch = Image.new("RGB", (x1 - x0, y1 - y0), (0, 0, 0))
    out.paste(patch, (x0, y0))
    return out


def dump_boxes(boxes) -> str:
    return json.dumps([[float(v) for v in box] for box in boxes], separators=(",", ":"))


def main() -> int:
    args = parse_args()
    source_repo = args.source_repo.resolve()
    pilot_root = source_repo / "pilot"
    source_module = pilot_root / "src"
    if not source_module.is_dir():
        raise FileNotFoundError(f"XAI pilot source not found: {source_module}")
    sys.path.insert(0, str(source_module))

    from xai_pilot import config
    from xai_pilot.data import load_construction_site
    from xai_pilot.inference import AnswerResult, answer_rule
    from xai_pilot.metrics.robustness import _robustness_from_results
    from xai_pilot.model import load_florence2

    config.DECODING = args.decoding
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    if not seeds:
        raise ValueError("At least one random-placement seed is required.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.sample_audit.parent.mkdir(parents=True, exist_ok=True)
    if args.force:
        args.output.unlink(missing_ok=True)
        args.sample_audit.unlink(missing_ok=True)

    predictions = pd.read_csv(
        pilot_root / "results" / "baseline_predictions.csv",
        dtype={"image_id": str, "assigned_rule_id": str, "primary_class": str},
    )
    predictions["image_id"] = predictions["image_id"].str.zfill(7)
    target_ids = set(predictions["image_id"])

    print(f"Loading {len(target_ids)} test images from the local ConstructionSite dataset...")
    images_by_id: dict[str, Image.Image] = {}
    for row in load_construction_site(split="test", streaming=True):
        image_id = str(row["image_id"]).zfill(7)
        if image_id in target_ids:
            images_by_id[image_id] = row["image"].convert("RGB")
        if len(images_by_id) == len(target_ids):
            break
    missing_images = sorted(target_ids - set(images_by_id))
    if missing_images:
        raise RuntimeError(f"Missing {len(missing_images)} sample images: {missing_images[:5]}")

    audit_rows = []
    parsed_rows = []
    for _, row in predictions.iterrows():
        image_id = row["image_id"]
        image = images_by_id[image_id]
        worker_boxes = json.loads(row["worker_boxes"])
        object_boxes = json.loads(row["object_boxes"])
        target_box = clip_box(tuple(object_boxes[0]), image.size) if object_boxes else None
        target_area = (
            (target_box[2] - target_box[0]) * (target_box[3] - target_box[1]) / (image.width * image.height)
            if target_box
            else math.nan
        )
        audit_rows.append(
            {
                "image_id": image_id,
                "primary_class": row["primary_class"],
                "assigned_rule_id": row["assigned_rule_id"],
                "image_width": image.width,
                "image_height": image.height,
                "has_worker_box": bool(worker_boxes),
                "has_object_box": bool(object_boxes),
                "target_box": json.dumps(target_box) if target_box else "",
                "target_area_fraction": target_area,
            }
        )
        parsed_rows.append((row, image, worker_boxes, object_boxes, target_box, target_area))
    pd.DataFrame(audit_rows).to_csv(args.sample_audit, index=False)

    existing = pd.DataFrame()
    completed: set[tuple[str, str, int]] = set()
    if args.output.exists():
        existing = pd.read_csv(args.output, dtype={"image_id": str})
        existing["image_id"] = existing["image_id"].str.zfill(7)
        completed = {
            (str(row.image_id), str(row.condition), int(row.seed))
            for row in existing.itertuples()
        }
        print(f"Resuming from {len(existing)} completed intervention rows.")

    print(f"Loading {config.MODEL_ID} with {args.decoding} decoding...")
    model, processor = load_florence2()
    new_rows: list[dict] = []
    start = time.perf_counter()

    for index, (row, image, worker_boxes, object_boxes, target_box, target_area) in enumerate(parsed_rows, 1):
        if target_box is None:
            continue
        baseline = AnswerResult(
            answer=row["answer"],
            boxes=[tuple(box) for box in worker_boxes + object_boxes],
            confidence=float(row["confidence"]),
            worker_boxes=[tuple(box) for box in worker_boxes],
            object_boxes=[tuple(box) for box in object_boxes],
        )
        interventions = [("targeted", -1, target_box, 1.0)]
        for seed in seeds:
            random_box, overlap = same_size_random_box(
                image.size,
                target_box,
                seed=seed,
                image_id=row["image_id"],
            )
            interventions.append(("random_matched", seed, random_box, overlap))

        for condition, seed, intervention_box, overlap in interventions:
            key = (row["image_id"], condition, int(seed))
            if key in completed:
                continue
            perturbed_image = mask_box(image, intervention_box)
            perturbed = answer_rule(model, processor, perturbed_image, row["assigned_rule_id"])
            comparison = _robustness_from_results(baseline, perturbed, image_size=image.size)
            mask_area = (
                (intervention_box[2] - intervention_box[0])
                * (intervention_box[3] - intervention_box[1])
                / (image.width * image.height)
            )
            new_rows.append(
                {
                    "image_id": row["image_id"],
                    "primary_class": row["primary_class"],
                    "assigned_rule_id": row["assigned_rule_id"],
                    "condition": condition,
                    "seed": seed,
                    "decoding": args.decoding,
                    "image_width": image.width,
                    "image_height": image.height,
                    "target_box": json.dumps(target_box),
                    "mask_box": json.dumps(intervention_box),
                    "target_area_fraction": target_area,
                    "mask_area_fraction": mask_area,
                    "mask_target_iou": overlap,
                    "baseline_answer": baseline.answer,
                    "perturbed_answer": perturbed.answer,
                    "answer_changed": comparison.answer_changed,
                    "genuine_answer_changed": comparison.answer_changed
                    and not comparison.flip_due_to_worker_loss,
                    "object_box_iou": comparison.object_box_iou,
                    "object_centroid_drift": comparison.object_centroid_drift,
                    "object_disappeared": comparison.object_disappeared,
                    "worker_lost": comparison.worker_lost,
                    "flip_due_to_worker_loss": comparison.flip_due_to_worker_loss,
                    "confidence_drop": comparison.confidence_drop,
                    "perturbed_worker_boxes": dump_boxes(perturbed.worker_boxes),
                    "perturbed_object_boxes": dump_boxes(perturbed.object_boxes),
                    "inference_ms": perturbed.inference_ms,
                }
            )

        if new_rows and (index % 10 == 0 or index == len(parsed_rows)):
            combined = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
            combined.to_csv(args.output, index=False)
            elapsed = time.perf_counter() - start
            print(f"{index}/{len(parsed_rows)} images; {len(combined)} rows; {elapsed / 60:.1f} min")

    combined = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
    combined = combined.sort_values(["image_id", "condition", "seed"]).reset_index(drop=True)
    combined.to_csv(args.output, index=False)
    expected = int(pd.DataFrame(audit_rows)["has_object_box"].sum()) * (1 + len(seeds))
    if len(combined) != expected:
        raise RuntimeError(f"Expected {expected} rows but wrote {len(combined)}.")
    print(f"Completed {len(combined)} intervention rows at {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
