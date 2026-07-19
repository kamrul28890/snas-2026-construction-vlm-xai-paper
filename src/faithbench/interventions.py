"""Intervention specification objects for benchmark runners."""

from __future__ import annotations

from dataclasses import dataclass

from faithbench.geometry import Box, IntBox, same_size_random_box


@dataclass(frozen=True)
class InterventionSpec:
    """A frozen visual intervention request."""

    image_id: str
    rule_id: str
    intervention_id: str
    intervention_type: str
    target_box: IntBox | None
    mask_box: IntBox | None
    seed: int | None = None
    mask_target_iou: float | None = None
    expected_effect: str = "unspecified"


def targeted_occlusion_spec(
    *,
    image_id: str,
    rule_id: str,
    target_box: IntBox,
) -> InterventionSpec:
    """Create a targeted occlusion spec for the rule-relevant object."""
    return InterventionSpec(
        image_id=image_id,
        rule_id=rule_id,
        intervention_id=f"{image_id}:{rule_id}:targeted",
        intervention_type="targeted_occlusion",
        target_box=target_box,
        mask_box=target_box,
        seed=None,
        mask_target_iou=1.0,
        expected_effect="rule_relevant_evidence_removed",
    )


def matched_random_occlusion_spec(
    *,
    image_id: str,
    rule_id: str,
    image_size: tuple[int, int],
    target_box: Box,
    seed: int,
    max_target_iou: float = 0.05,
) -> InterventionSpec:
    """Create a same-size random occlusion spec for a target evidence box."""
    mask_box, overlap = same_size_random_box(
        image_size,
        target_box,
        seed=seed,
        image_id=image_id,
        max_target_iou=max_target_iou,
    )
    return InterventionSpec(
        image_id=image_id,
        rule_id=rule_id,
        intervention_id=f"{image_id}:{rule_id}:matched_random:{seed}",
        intervention_type="matched_random_occlusion",
        target_box=None,
        mask_box=mask_box,
        seed=seed,
        mask_target_iou=overlap,
        expected_effect="control_region_removed",
    )

