"""Intervention specification objects for benchmark runners."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

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

    def to_row(self) -> dict[str, str]:
        """Serialize intervention spec for JSONL/CSV writing."""
        return {
            "image_id": self.image_id,
            "rule_id": self.rule_id,
            "intervention_id": self.intervention_id,
            "intervention_type": self.intervention_type,
            "target_box_xyxy": "" if self.target_box is None else json.dumps(list(self.target_box), separators=(",", ":")),
            "mask_box_xyxy": "" if self.mask_box is None else json.dumps(list(self.mask_box), separators=(",", ":")),
            "seed": "" if self.seed is None else str(self.seed),
            "mask_target_iou": "" if self.mask_target_iou is None else str(float(self.mask_target_iou)),
            "expected_effect": self.expected_effect,
        }


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


def build_intervention_specs_from_manifest(
    manifest_rows: list[dict[str, str]],
    *,
    random_seeds: list[int],
    max_target_iou: float = 0.05,
) -> list[InterventionSpec]:
    """Create targeted and matched-random specs for rows with target boxes."""
    specs: list[InterventionSpec] = []
    for row in manifest_rows:
        if not row["target_box_xyxy"]:
            continue
        target_box = tuple(json.loads(row["target_box_xyxy"]))
        image_size = (int(row["image_width"]), int(row["image_height"]))
        specs.append(
            targeted_occlusion_spec(
                image_id=row["image_id"],
                rule_id=row["rule_id"],
                target_box=target_box,
            )
        )
        for seed in random_seeds:
            specs.append(
                matched_random_occlusion_spec(
                    image_id=row["image_id"],
                    rule_id=row["rule_id"],
                    image_size=image_size,
                    target_box=target_box,
                    seed=seed,
                    max_target_iou=max_target_iou,
                )
            )
    return specs


def load_manifest_rows(path: Path) -> list[dict[str, str]]:
    """Load benchmark manifest rows."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_intervention_specs(specs: list[InterventionSpec], *, jsonl_path: Path, csv_path: Path) -> None:
    """Write intervention specs as JSONL and CSV."""
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [spec.to_row() for spec in specs]
    fields = list(rows[0].keys()) if rows else [
        "image_id",
        "rule_id",
        "intervention_id",
        "intervention_type",
        "target_box_xyxy",
        "mask_box_xyxy",
        "seed",
        "mask_target_iou",
        "expected_effect",
    ]
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
