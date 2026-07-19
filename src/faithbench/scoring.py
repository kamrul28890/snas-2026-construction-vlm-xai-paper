"""Scoring helpers for answer-evidence faithfulness."""

from __future__ import annotations

import math
from dataclasses import dataclass

from faithbench.geometry import Box, box_iou, normalized_centroid_drift


@dataclass(frozen=True)
class EvidenceComparison:
    """Comparison between baseline and perturbed evidence."""

    baseline_present: bool
    perturbed_present: bool
    iou: float
    centroid_drift: float
    disappeared: bool
    relocated: bool


def compare_evidence(
    baseline_box: Box | None,
    perturbed_box: Box | None,
    *,
    image_size: tuple[int, int],
    iou_threshold: float = 0.3,
    centroid_threshold: float = 0.2,
) -> EvidenceComparison:
    """Compare two evidence boxes while making disappearance explicit."""
    baseline_present = baseline_box is not None
    perturbed_present = perturbed_box is not None
    disappeared = baseline_present and not perturbed_present
    if baseline_box is None or perturbed_box is None:
        return EvidenceComparison(
            baseline_present=baseline_present,
            perturbed_present=perturbed_present,
            iou=math.nan,
            centroid_drift=math.nan,
            disappeared=disappeared,
            relocated=False,
        )
    iou = box_iou(baseline_box, perturbed_box)
    drift = normalized_centroid_drift(baseline_box, perturbed_box, image_size)
    return EvidenceComparison(
        baseline_present=True,
        perturbed_present=True,
        iou=iou,
        centroid_drift=drift,
        disappeared=False,
        relocated=iou < iou_threshold and drift > centroid_threshold,
    )


def normalize_answer(value: object) -> str:
    """Normalize model answer strings into the benchmark answer set."""
    normalized = str(value or "").strip().lower()
    aliases = {
        "safe": "compliant",
        "hazard": "violation",
        "hazardous": "violation",
        "unsafe": "violation",
        "non-compliant": "violation",
        "noncompliant": "violation",
        "not compliant": "violation",
        "cannot determine": "uncertain",
        "unknown": "uncertain",
        "n/a": "invalid",
        "": "invalid",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized in {"compliant", "violation", "uncertain", "invalid"}:
        return normalized
    return "invalid"
