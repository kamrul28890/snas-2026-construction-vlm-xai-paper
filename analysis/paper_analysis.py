"""Pure statistical and geometry helpers for the SNAS paper analysis."""

from __future__ import annotations

import hashlib
import math
import random
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
from scipy.stats import rankdata, wilcoxon


def as_bool(value) -> bool:
    """Parse booleans written by pandas without treating non-empty strings as true."""
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return False
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no", "", "nan"}:
        return False
    raise ValueError(f"Cannot parse boolean value: {value!r}")


def bootstrap_ci(
    values: Iterable[float],
    statistic: Callable[[np.ndarray], float] = np.mean,
    *,
    n_boot: int = 10_000,
    ci: float = 0.95,
    seed: int = 20_260_716,
) -> dict[str, float | int]:
    """Return a reproducible percentile-bootstrap interval after dropping NaNs."""
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"point": math.nan, "lo": math.nan, "hi": math.nan, "n": 0, "ci": ci}
    point = float(statistic(arr))
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, arr.size, size=(n_boot, arr.size))
    estimates = np.apply_along_axis(statistic, 1, arr[indices])
    alpha = (1.0 - ci) / 2.0
    lo, hi = np.quantile(estimates, [alpha, 1.0 - alpha])
    return {"point": point, "lo": float(lo), "hi": float(hi), "n": int(arr.size), "ci": ci}


def paired_bootstrap_difference(
    a: Iterable[float],
    b: Iterable[float],
    *,
    n_boot: int = 10_000,
    ci: float = 0.95,
    seed: int = 20_260_716,
) -> dict[str, float | int]:
    """Bootstrap the paired mean difference a - b using images as the resampling unit."""
    aa = np.asarray(list(a), dtype=float)
    bb = np.asarray(list(b), dtype=float)
    keep = np.isfinite(aa) & np.isfinite(bb)
    diff = aa[keep] - bb[keep]
    return bootstrap_ci(diff, n_boot=n_boot, ci=ci, seed=seed)


def wilcoxon_with_effect(a: Iterable[float], b: Iterable[float]) -> dict[str, float | int]:
    """Two-sided Wilcoxon test with matched-pairs rank-biserial correlation."""
    aa = np.asarray(list(a), dtype=float)
    bb = np.asarray(list(b), dtype=float)
    keep = np.isfinite(aa) & np.isfinite(bb)
    diff = aa[keep] - bb[keep]
    nonzero = diff[diff != 0]
    if nonzero.size == 0:
        return {"statistic": math.nan, "p_value": 1.0, "effect_size": 0.0, "n": int(diff.size)}
    result = wilcoxon(nonzero, alternative="two-sided", zero_method="wilcox")
    ranks = rankdata(np.abs(nonzero))
    positive = float(ranks[nonzero > 0].sum())
    negative = float(ranks[nonzero < 0].sum())
    effect = (positive - negative) / (positive + negative)
    return {
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "effect_size": float(effect),
        "n": int(diff.size),
    }


def holm_adjust(p_values: Iterable[float]) -> list[float]:
    """Return Holm step-down adjusted p-values in the input order."""
    values = np.asarray(list(p_values), dtype=float)
    if values.size == 0:
        return []
    order = np.argsort(values)
    adjusted_sorted = np.empty(values.size, dtype=float)
    running_max = 0.0
    for rank, index in enumerate(order):
        running_max = max(running_max, (values.size - rank) * values[index])
        adjusted_sorted[rank] = min(1.0, running_max)
    adjusted = np.empty(values.size, dtype=float)
    adjusted[order] = adjusted_sorted
    return adjusted.tolist()


def box_iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    """Intersection over union for two absolute-pixel boxes."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    intersection = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    area_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0)
    area_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0)
    union = area_a + area_b - intersection
    return intersection / union if union else 0.0


def clip_box(
    box: tuple[float, float, float, float], image_size: tuple[int, int]
) -> tuple[int, int, int, int]:
    """Round and clip a box to valid image coordinates, preserving at least one pixel."""
    width, height = image_size
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    x0 = min(max(x0, 0), max(width - 1, 0))
    y0 = min(max(y0, 0), max(height - 1, 0))
    x1 = min(max(x1, x0 + 1), width)
    y1 = min(max(y1, y0 + 1), height)
    return x0, y0, x1, y1


def same_size_random_box(
    image_size: tuple[int, int],
    target_box: tuple[float, float, float, float],
    *,
    seed: int,
    image_id: str,
    max_target_iou: float = 0.05,
    max_attempts: int = 200,
) -> tuple[tuple[int, int, int, int], float]:
    """Place a target-sized rectangle randomly, preferring negligible target overlap."""
    width, height = image_size
    target = clip_box(target_box, image_size)
    box_width = target[2] - target[0]
    box_height = target[3] - target[1]
    x_max = max(0, width - box_width)
    y_max = max(0, height - box_height)
    numeric_id = int("".join(ch for ch in str(image_id) if ch.isdigit()) or "0")
    rng = random.Random(seed * 1_000_003 + numeric_id)
    best_box = (0, 0, box_width, box_height)
    best_iou = box_iou(target, best_box)
    for _ in range(max_attempts):
        x0 = rng.randint(0, x_max) if x_max else 0
        y0 = rng.randint(0, y_max) if y_max else 0
        candidate = (x0, y0, x0 + box_width, y0 + box_height)
        overlap = box_iou(target, candidate)
        if overlap < best_iou:
            best_box, best_iou = candidate, overlap
        if overlap <= max_target_iou:
            return candidate, overlap
    return best_box, best_iou


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 checksum for an artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
