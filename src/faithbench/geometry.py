"""Geometry helpers for evidence-region interventions and scoring."""

from __future__ import annotations

import math
import random

Box = tuple[float, float, float, float]
IntBox = tuple[int, int, int, int]


def box_area(box: Box) -> float:
    """Return non-negative box area."""
    x0, y0, x1, y1 = box
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def box_iou(a: Box, b: Box) -> float:
    """Intersection over union for two absolute-pixel boxes."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    intersection = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    union = box_area(a) + box_area(b) - intersection
    return intersection / union if union else 0.0


def clip_box(box: Box, image_size: tuple[int, int]) -> IntBox:
    """Round and clip a box to valid image coordinates, preserving one pixel."""
    width, height = image_size
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    x0 = min(max(x0, 0), max(width - 1, 0))
    y0 = min(max(y0, 0), max(height - 1, 0))
    x1 = min(max(x1, x0 + 1), width)
    y1 = min(max(y1, y0 + 1), height)
    return x0, y0, x1, y1


def box_centroid(box: Box) -> tuple[float, float]:
    """Return the center point of a box."""
    x0, y0, x1, y1 = box
    return (x0 + x1) / 2.0, (y0 + y1) / 2.0


def normalized_centroid_drift(a: Box, b: Box, image_size: tuple[int, int]) -> float:
    """Return centroid distance normalized by image diagonal."""
    ax, ay = box_centroid(a)
    bx, by = box_centroid(b)
    width, height = image_size
    diagonal = math.hypot(width, height)
    if diagonal == 0:
        return math.nan
    return math.hypot(ax - bx, ay - by) / diagonal


def same_size_random_box(
    image_size: tuple[int, int],
    target_box: Box,
    *,
    seed: int,
    image_id: str,
    max_target_iou: float = 0.05,
    max_attempts: int = 200,
) -> tuple[IntBox, float]:
    """Place a target-sized rectangle randomly, preferring negligible overlap."""
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

