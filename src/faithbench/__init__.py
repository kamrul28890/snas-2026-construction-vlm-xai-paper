"""Reusable benchmark helpers for ConstructionSafety-FaithBench."""

from faithbench.annotation import build_model_assisted_annotations, model_assisted_annotation
from faithbench.geometry import box_iou, clip_box, normalized_centroid_drift, same_size_random_box
from faithbench.manifest import LEGACY_RULE_MAP, build_pilot_manifest, evidence_size_band
from faithbench.metrics import score_model_outputs
from faithbench.model_harness import (
    ModelInput,
    ModelOutput,
    adapter_by_name,
    load_model_inputs,
    run_adapter,
    validate_output_row,
    write_model_outputs,
)
from faithbench.schema import BenchmarkRules, PromptSet, load_prompts, load_rules
from faithbench.scaleup import classify_source_row, select_scaleup_candidates
from faithbench.scoring import EvidenceComparison, compare_evidence
from faithbench.statistics import bootstrap_ci, holm_adjust, paired_bootstrap_difference

__all__ = [
    "BenchmarkRules",
    "EvidenceComparison",
    "LEGACY_RULE_MAP",
    "ModelInput",
    "ModelOutput",
    "PromptSet",
    "adapter_by_name",
    "box_iou",
    "build_model_assisted_annotations",
    "build_pilot_manifest",
    "bootstrap_ci",
    "classify_source_row",
    "clip_box",
    "compare_evidence",
    "evidence_size_band",
    "holm_adjust",
    "load_prompts",
    "load_rules",
    "load_model_inputs",
    "model_assisted_annotation",
    "normalized_centroid_drift",
    "paired_bootstrap_difference",
    "run_adapter",
    "same_size_random_box",
    "score_model_outputs",
    "select_scaleup_candidates",
    "validate_output_row",
    "write_model_outputs",
]
