"""Characterize the targeted and matched-random occlusions.

Review 2 raised the concern that size-matched random masks may land
disproportionately on background, which would make the targeted-versus-random
comparison weaker than it appears. This script quantifies that directly from the
frozen intervention data so the manuscript can report what the control does and
does not isolate.

Writes results/tables/mask_characteristics.csv.
"""

from __future__ import annotations

import ast
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "analysis" / "outputs" / "matched_random_occlusion.csv"
OUT = ROOT / "results" / "tables" / "mask_characteristics.csv"

FIELDS = ("mask_area_fraction", "mask_target_iou", "worker_lost", "object_disappeared",
          "answer_changed")


def as_float(value: str) -> float | None:
    text = (value or "").strip().lower()
    if text in {"", "na", "nan", "none"}:
        return None
    if text in {"true", "false"}:
        return 1.0 if text == "true" else 0.0
    try:
        return float(text)
    except ValueError:
        return None


def parse_box(value: str) -> list[float] | None:
    if not value or value.strip().lower() in {"", "na", "nan", "none"}:
        return None
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return None
    if not parsed:
        return None
    if isinstance(parsed[0], list):
        parsed = parsed[0]
    return [float(x) for x in parsed] if len(parsed) == 4 else None


def mask_area_on_target(mask: list[float] | None, target: list[float] | None) -> float | None:
    """Fraction of the mask's own area that falls inside the target box."""
    if not mask or not target:
        return None
    ix1, iy1 = max(mask[0], target[0]), max(mask[1], target[1])
    ix2, iy2 = min(mask[2], target[2]), min(mask[3], target[3])
    intersection = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area = (mask[2] - mask[0]) * (mask[3] - mask[1])
    return intersection / area if area > 0 else None


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def main() -> None:
    rows = list(csv.DictReader(SRC.open(encoding="utf-8")))

    conditions: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        bucket = conditions.setdefault(row["condition"], {k: [] for k in FIELDS})
        for field in FIELDS:
            value = as_float(row.get(field, ""))
            if value is not None:
                bucket[field].append(value)
        overlap = mask_area_on_target(parse_box(row.get("mask_box", "")),
                                      parse_box(row.get("target_box", "")))
        bucket.setdefault("mask_area_on_target", []).append(overlap or 0.0)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["condition", "n", "mean_mask_area_fraction", "mean_mask_target_iou",
                         "mean_mask_area_on_target", "worker_loss_rate",
                         "evidence_disappearance_rate", "answer_change_rate"])
        for condition in sorted(conditions):
            b = conditions[condition]
            writer.writerow([
                condition,
                len(b["mask_area_fraction"]),
                f"{mean(b['mask_area_fraction']):.6f}",
                f"{mean(b['mask_target_iou']):.6f}",
                f"{mean(b['mask_area_on_target']):.6f}",
                f"{mean(b['worker_lost']):.6f}",
                f"{mean(b['object_disappeared']):.6f}",
                f"{mean(b['answer_changed']):.6f}",
            ])

    print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    for condition in sorted(conditions):
        b = conditions[condition]
        print(f"\n{condition} (n={len(b['mask_area_fraction'])})")
        print(f"  mask area, share of image   {mean(b['mask_area_fraction']):.4f}")
        print(f"  mask-target IoU             {mean(b['mask_target_iou']):.4f}")
        print(f"  mask area on target         {mean(b['mask_area_on_target']):.4f}")
        print(f"  removed worker detection    {mean(b['worker_lost']):.4f}")
        print(f"  answer changed              {mean(b['answer_changed']):.4f}")

    random_iou = [v for v in conditions.get("random_matched", {}).get("mask_target_iou", [])]
    if random_iou:
        share = sum(1 for v in random_iou if v <= 0.05) / len(random_iou)
        print(f"\nrandom masks with target IoU <= 0.05: {share:.4f}")

    report_control_degeneracy(rows)
    report_robustness(rows)


def median(values: list[float]) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def report_control_degeneracy(rows: list[dict[str, str]]) -> None:
    """Where the target box is very large, no disjoint same-size mask exists.

    The placement search then falls back to the lowest-overlap candidate, so the
    control stops being independent of the target. Quantify how often this
    happens and how the control behaves on those images versus the rest.
    """
    targeted = {r["image_id"]: r for r in rows if r["condition"] == "targeted"}
    areas = [as_float(r.get("mask_area_fraction", "")) or 0.0 for r in targeted.values()]
    degenerate = {i for i, r in targeted.items()
                  if (as_float(r.get("mask_area_fraction", "")) or 0.0) > 0.5}

    inside, outside = [], []
    for row in rows:
        if row["condition"] == "targeted":
            continue
        iou = as_float(row.get("mask_target_iou", ""))
        if iou is None:
            continue
        (inside if row["image_id"] in degenerate else outside).append(iou)

    print("\ntargeted mask area, share of image")
    print(f"  mean {mean(areas):.4f}   median {median(areas):.4f}")
    print(f"  covering more than half the image: {len(degenerate)} of {len(areas)}")
    if inside:
        print(f"\ncontrol on those {len(degenerate)} images: mean target IoU {mean(inside):.3f}, "
              f"share at or below 0.05 = {sum(1 for v in inside if v <= 0.05) / len(inside):.3f}")
    if outside:
        print(f"control on the other images:        mean target IoU {mean(outside):.3f}, "
              f"share at or below 0.05 = {sum(1 for v in outside if v <= 0.05) / len(outside):.3f}")


def report_robustness(rows: list[dict[str, str]]) -> None:
    """Repeat the primary paired comparison without the degenerate-control images.

    If the targeted-versus-random difference depends on images where the control
    could not be placed cleanly, the headline result would be an artifact of the
    placement fallback. Bootstrap settings match analysis/protocol.json.
    """
    import random as _random

    targeted = {r["image_id"]: r for r in rows if r["condition"] == "targeted"}
    controls: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        if row["condition"] != "targeted":
            controls.setdefault(row["image_id"], []).append(row)

    degenerate = {i for i, r in targeted.items()
                  if (as_float(r.get("mask_area_fraction", "")) or 0.0) > 0.5}

    def paired(image_ids: set[str]) -> tuple[list[float], float, float]:
        diffs, t_rates, c_rates = [], [], []
        for image_id in image_ids:
            t = as_float(targeted[image_id].get("answer_changed", ""))
            cs = [as_float(c.get("answer_changed", "")) for c in controls.get(image_id, [])]
            cs = [c for c in cs if c is not None]
            if t is None or not cs:
                continue
            diffs.append(t - mean(cs))
            t_rates.append(t)
            c_rates.append(mean(cs))
        return diffs, mean(t_rates), mean(c_rates)

    def ci(values: list[float], resamples: int = 10000, seed: int = 20260716) -> tuple[float, float]:
        rng = _random.Random(seed)
        means = sorted(mean([values[rng.randrange(len(values))] for _ in values])
                       for _ in range(resamples))
        return means[int(0.025 * resamples)], means[int(0.975 * resamples)]

    out = ROOT / "results" / "tables" / "control_robustness.csv"
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["subset", "n_images", "targeted_flip_rate",
                         "matched_random_flip_rate", "paired_difference", "ci_low", "ci_high"])
        print("\nprimary comparison, with and without degenerate-control images")
        for label, ids in (("all", set(targeted)),
                           ("excluding_degenerate_control", set(targeted) - degenerate)):
            diffs, t_rate, c_rate = paired(ids)
            lo, hi = ci(diffs)
            writer.writerow([label, len(diffs), f"{t_rate:.6f}", f"{c_rate:.6f}",
                             f"{mean(diffs):.6f}", f"{lo:.6f}", f"{hi:.6f}"])
            print(f"  {label:30} n={len(diffs):3}  targeted {t_rate:.3f}  "
                  f"random {c_rate:.3f}  diff {mean(diffs):.3f} [{lo:.3f}, {hi:.3f}]")
    print(f"\nwrote {out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
