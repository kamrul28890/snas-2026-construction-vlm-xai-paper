"""Reusable benchmark helpers for ConstructionSafety-FaithBench."""

from faithbench.annotation import build_model_assisted_annotations, model_assisted_annotation
from faithbench.geometry import box_iou, clip_box, normalized_centroid_drift, same_size_random_box
from faithbench.manifest import LEGACY_RULE_MAP, build_pilot_manifest, evidence_size_band
from faithbench.schema import BenchmarkRules, PromptSet, load_prompts, load_rules
from faithbench.scoring import EvidenceComparison, compare_evidence
from faithbench.statistics import bootstrap_ci, holm_adjust, paired_bootstrap_difference

__all__ = [
    "BenchmarkRules",
    "EvidenceComparison",
    "LEGACY_RULE_MAP",
    "PromptSet",
    "box_iou",
    "build_model_assisted_annotations",
    "build_pilot_manifest",
    "bootstrap_ci",
    "clip_box",
    "compare_evidence",
    "evidence_size_band",
    "holm_adjust",
    "load_prompts",
    "load_rules",
    "model_assisted_annotation",
    "normalized_centroid_drift",
    "paired_bootstrap_difference",
    "same_size_random_box",
]
