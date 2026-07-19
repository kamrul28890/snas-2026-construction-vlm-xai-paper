"""Run Florence-2 on frozen visual intervention specs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.annotation import RULE_EVIDENCE_OBJECTS
from faithbench.intervention_metrics import validate_intervention_row, write_rows
from faithbench.scoring import normalize_answer

NORMALIZED_TO_LEGACY_RULE = {
    "ppe_hard_hat": "rule_1",
    "fall_harness": "rule_2",
    "guardrail_edge": "rule_3",
    "struck_by_equipment": "rule_4",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--interventions",
        type=Path,
        default=ROOT / "benchmark" / "interventions" / "pilot_interventions.jsonl",
    )
    parser.add_argument("--output-stem", default="pilot_florence_interventions")
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=ROOT.parent / "Explainable-AI-Mustafa-Abdallah",
    )
    parser.add_argument("--limit", type=int, default=0, help="Optional debug limit; 0 means all rows.")
    parser.add_argument("--decoding", choices=["beam", "greedy"], default="beam")
    parser.add_argument("--mask-mode", choices=["black", "blur", "inpaint"], default="black")
    return parser.parse_args()


def read_interventions(path: Path, *, limit: int = 0) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    return rows[:limit] if limit else rows


def load_images(source_repo: Path, image_ids: set[str]) -> dict[str, object]:
    source_module = source_repo / "pilot" / "src"
    if not source_module.is_dir():
        raise FileNotFoundError(f"XAI pilot source not found: {source_module}")
    sys.path.insert(0, str(source_module))
    from xai_pilot.data import load_construction_site

    images = {}
    for row in load_construction_site(split="test", streaming=True):
        image_id = str(row["image_id"]).zfill(7)
        if image_id in image_ids:
            images[image_id] = row["image"].convert("RGB")
            if len(images) == len(image_ids):
                break
    missing = sorted(image_ids - set(images))
    if missing:
        raise RuntimeError(f"Missing {len(missing)} images: {missing[:5]}")
    return images


def boxes_to_int(boxes: list[tuple[float, float, float, float]]) -> list[list[int]]:
    return [[int(round(v)) for v in box] for box in boxes]


def main() -> int:
    args = parse_args()
    source_repo = args.source_repo.resolve()
    source_module = source_repo / "pilot" / "src"
    sys.path.insert(0, str(source_module))

    from xai_pilot import config
    from xai_pilot.inference import answer_rule
    from xai_pilot.model import load_florence2
    from xai_pilot.regions import mask_region

    config.DECODING = args.decoding
    specs = read_interventions(args.interventions, limit=args.limit)
    images = load_images(source_repo, {row["image_id"] for row in specs})
    model, processor = load_florence2()

    output_rows: list[dict[str, str]] = []
    for index, spec in enumerate(specs, 1):
        mask_box = tuple(json.loads(spec["mask_box_xyxy"]))
        masked_image = mask_region(images[spec["image_id"]], mask_box, mode=args.mask_mode)
        legacy_rule = NORMALIZED_TO_LEGACY_RULE[spec["rule_id"]]
        result = answer_rule(model, processor, masked_image, legacy_rule)
        answer = normalize_answer(result.answer)
        evidence_regions = boxes_to_int(result.object_boxes)
        raw = {
            "legacy_rule_id": legacy_rule,
            "source_answer": result.answer,
            "worker_boxes": boxes_to_int(result.worker_boxes),
            "object_boxes": evidence_regions,
            "confidence": result.confidence,
            "graded_score": result.graded_score,
            "inference_ms": result.inference_ms,
            "decoding": args.decoding,
            "mask_mode": args.mask_mode,
        }
        output = {
            "intervention_id": spec["intervention_id"],
            "image_id": spec["image_id"],
            "rule_id": spec["rule_id"],
            "intervention_type": spec["intervention_type"],
            "seed": spec["seed"],
            "target_box_xyxy": spec["target_box_xyxy"],
            "mask_box_xyxy": spec["mask_box_xyxy"],
            "mask_target_iou": spec["mask_target_iou"],
            "model_id": "microsoft/Florence-2-base-ft:grounding_pipeline",
            "prompt_id": f"florence_grounding_{args.decoding}_{args.mask_mode}_mask",
            "answer": answer,
            "evidence_regions_xyxy": json.dumps(evidence_regions, separators=(",", ":")),
            "worker_boxes_xyxy": json.dumps(boxes_to_int(result.worker_boxes), separators=(",", ":")),
            "object_boxes_xyxy": json.dumps(evidence_regions, separators=(",", ":")),
            "confidence": str(float(result.confidence)),
            "graded_score": str(float(result.graded_score)),
            "raw_response": json.dumps(raw, separators=(",", ":")),
            "provenance": "local_florence2_grounding_pipeline_intervention",
        }
        validate_intervention_row(output)
        output_rows.append(output)
        if index % 25 == 0 or index == len(specs):
            print(f"{index}/{len(specs)} intervention rows complete")

    out_dir = ROOT / "results" / "intervention_outputs"
    write_rows(
        output_rows,
        jsonl_path=out_dir / f"{args.output_stem}.jsonl",
        csv_path=out_dir / f"{args.output_stem}.csv",
    )
    summary = {
        "output_stem": args.output_stem,
        "row_count": len(output_rows),
        "source_interventions": str(args.interventions),
        "model_id": "microsoft/Florence-2-base-ft:grounding_pipeline",
        "prompt_id": f"florence_grounding_{args.decoding}_{args.mask_mode}_mask",
        "decoding": args.decoding,
        "mask_mode": args.mask_mode,
        "answer_counts": {},
        "intervention_type_counts": {},
    }
    for row in output_rows:
        summary["answer_counts"][row["answer"]] = summary["answer_counts"].get(row["answer"], 0) + 1
        key = row["intervention_type"]
        summary["intervention_type_counts"][key] = summary["intervention_type_counts"].get(key, 0) + 1
    with (out_dir / f"{args.output_stem}_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    print(f"Wrote {len(output_rows)} intervention rows to {out_dir / (args.output_stem + '.jsonl')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
