from __future__ import annotations

import math
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from faithbench.annotation import ANNOTATOR_ID, model_assisted_annotation, normalized_box_to_abs
from faithbench.geometry import clip_box, normalized_centroid_drift, same_size_random_box
from faithbench.interventions import (
    build_intervention_specs_from_manifest,
    load_manifest_rows,
    matched_random_occlusion_spec,
    targeted_occlusion_spec,
)
from faithbench.intervention_metrics import summarize_intervention_outputs, validate_intervention_row
from faithbench.manifest import LEGACY_RULE_MAP, build_pilot_manifest, evidence_size_band
from faithbench.metrics import load_annotations, load_jsonl, load_manifest_by_key, score_model_outputs
from faithbench.model_harness import (
    MODEL_OUTPUT_FIELDS,
    adapter_by_name,
    caption_keyword_answer,
    load_annotations_by_key,
    load_model_inputs,
    run_adapter,
    validate_output_row,
)
from faithbench.schema import load_prompts, load_rules
from faithbench.scaleup import choose_rule_for_row, classify_source_row, select_scaleup_candidates
from faithbench.scoring import compare_evidence, normalize_answer
from faithbench.statistics import bootstrap_ci, holm_adjust, paired_bootstrap_difference
from experiments.analyze_score_slices import build_slices
from experiments.build_human_audit_batch import build_batch, priority_for
from experiments.score_human_audit_status import summarize as summarize_human_audit_status


def test_rules_and_prompts_load_and_render():
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    prompts = load_prompts(ROOT / "benchmark" / "prompts" / "safety_rule_prompts.json")
    assert len(rules.rules) == 4
    assert len(prompts.prompts) >= 3
    rendered = prompts.by_id("direct_vqa_v1").render(question=rules.by_id("ppe_hard_hat").question)
    assert "head protection" in rendered.lower()
    assert "json" in rendered.lower()


def test_clip_box_preserves_one_pixel_inside_image():
    assert clip_box((-10, -5, 0, 0), (100, 50)) == (0, 0, 1, 1)


def test_same_size_random_box_preserves_dimensions_and_low_overlap():
    random_box, overlap = same_size_random_box((200, 100), (10, 20, 40, 60), seed=42, image_id="0000007")
    assert random_box[2] - random_box[0] == 30
    assert random_box[3] - random_box[1] == 40
    assert overlap <= 0.05


def test_normalized_centroid_drift_uses_image_diagonal():
    drift = normalized_centroid_drift((0, 0, 10, 10), (3, 4, 13, 14), (3, 4))
    assert math.isclose(drift, 1.0)


def test_compare_evidence_makes_disappearance_explicit():
    comparison = compare_evidence((0, 0, 10, 10), None, image_size=(100, 100))
    assert comparison.baseline_present is True
    assert comparison.perturbed_present is False
    assert comparison.disappeared is True
    assert math.isnan(comparison.iou)


def test_compare_evidence_marks_large_relocation():
    comparison = compare_evidence((0, 0, 10, 10), (80, 80, 90, 90), image_size=(100, 100))
    assert comparison.iou == 0.0
    assert comparison.centroid_drift > 0.2
    assert comparison.relocated is True


def test_normalize_answer_aliases_and_invalids():
    assert normalize_answer("safe") == "compliant"
    assert normalize_answer("hazard") == "violation"
    assert normalize_answer("not compliant") == "violation"
    assert normalize_answer("cannot determine") == "uncertain"
    assert normalize_answer("maybe") == "invalid"


def test_intervention_specs_are_stable_and_descriptive():
    targeted = targeted_occlusion_spec(image_id="0001", rule_id="ppe_hard_hat", target_box=(1, 2, 3, 4))
    random = matched_random_occlusion_spec(
        image_id="0001",
        rule_id="ppe_hard_hat",
        image_size=(100, 80),
        target_box=(1, 2, 3, 4),
        seed=7,
    )
    assert targeted.intervention_type == "targeted_occlusion"
    assert targeted.mask_target_iou == 1.0
    assert random.intervention_type == "matched_random_occlusion"
    assert random.seed == 7


def test_statistics_are_reproducible():
    first = bootstrap_ci([0, 1, 1, 0], n_boot=1000, seed=7)
    second = bootstrap_ci([0, 1, 1, 0], n_boot=1000, seed=7)
    assert first == second
    assert paired_bootstrap_difference([2, 3], [1, 1], n_boot=1000, seed=4)["point"] == 1.5
    assert holm_adjust([0.04, 0.001, 0.03]) == [0.06, 0.003, 0.06]


def test_legacy_rule_mapping_covers_all_pilot_rules():
    assert LEGACY_RULE_MAP == {
        "rule_1": "ppe_hard_hat",
        "rule_2": "fall_harness",
        "rule_3": "guardrail_edge",
        "rule_4": "struck_by_equipment",
    }


def test_evidence_size_band_uses_fixed_thresholds():
    assert evidence_size_band("") == "missing"
    assert evidence_size_band(0.0005) == "tiny"
    assert evidence_size_band(0.005) == "small"
    assert evidence_size_band(0.05) == "medium"
    assert evidence_size_band(0.5) == "large"


def test_build_pilot_manifest_to_temporary_directory(tmp_path):
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    result = build_pilot_manifest(
        sample_audit_path=ROOT / "analysis" / "outputs" / "sample_audit.csv",
        dataset_summary_path=ROOT / "analysis" / "outputs" / "dataset_summary.csv",
        rules=rules,
        manifest_path=tmp_path / "pilot_manifest.csv",
        annotation_jsonl_path=tmp_path / "pilot_annotation_template.jsonl",
        annotation_csv_path=tmp_path / "pilot_annotation_template.csv",
        summary_path=tmp_path / "pilot_manifest_summary.json",
    )
    assert result.row_count == 163
    assert result.annotation_count == 163
    with result.manifest_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["rule_id"] == "ppe_hard_hat"
    assert rows[0]["expected_answer_seed"] == "violation"
    with result.summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    assert summary["class_counts"]["struck_by_risk"] == 13
    assert summary["priority_counts"]["missing_evidence"] == 13


def test_checked_in_pilot_manifest_matches_summary():
    manifest_path = ROOT / "benchmark" / "splits" / "pilot_manifest.csv"
    summary_path = ROOT / "benchmark" / "splits" / "pilot_manifest_summary.json"
    annotation_path = ROOT / "benchmark" / "annotations" / "pilot_annotation_template.jsonl"
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    with annotation_path.open("r", encoding="utf-8") as handle:
        annotation_rows = [json.loads(line) for line in handle if line.strip()]
    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    assert len(manifest_rows) == summary["row_count"] == 163
    assert len(annotation_rows) == summary["annotation_template_count"] == 163
    assert {row["rule_id"] for row in manifest_rows} == set(LEGACY_RULE_MAP.values())


def test_normalized_source_boxes_convert_to_absolute_pixels():
    assert normalized_box_to_abs([0.1, 0.2, 0.5, 0.6], 100, 200) == [10, 40, 50, 120]


def test_model_assisted_annotation_uses_source_violation_when_available():
    manifest_row = {
        "image_id": "0000007",
        "rule_id": "ppe_hard_hat",
        "question": "Is each visible worker wearing required head protection?",
        "expected_answer_seed": "violation",
        "image_width": "100",
        "image_height": "50",
        "has_worker_box": "true",
        "has_object_box": "true",
        "target_box_xyxy": "[1, 2, 3, 4]",
        "annotation_priority": "standard",
        "notes": "",
    }
    dataset_row = {
        "image_caption": "Two workers are visible.",
        "quality_of_info": "poor info",
        "rule_1_violation": {
            "bounding_box": [[0.1, 0.2, 0.5, 0.6]],
            "reason": "A worker is missing head protection.",
        },
    }
    annotation = model_assisted_annotation(manifest_row, dataset_row)
    assert annotation["annotator_id"] == ANNOTATOR_ID
    assert annotation["answer_label"] == "violation"
    assert annotation["evidence_regions_xyxy"] == "[[10,10,50,30]]"
    assert annotation["image_quality_issue"] == "yes"
    assert "not human ground truth" in annotation["free_text_notes"]


def test_checked_in_model_assisted_annotations_are_complete_and_labeled():
    annotation_path = ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl"
    summary_path = ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotation_summary.json"
    with annotation_path.open("r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    assert len(rows) == summary["row_count"] == 163
    assert summary["answer_counts"] == {"violation": 113, "compliant": 50}
    assert "not human/domain-expert ground truth" in summary["provenance"]
    for row in rows:
        assert row["annotator_id"] == ANNOTATOR_ID
        assert row["answer_label"] in {"compliant", "violation"}
        assert row["applies_to_image"] in {"yes", "no", "uncertain"}
        assert row["ambiguous"] in {"yes", "no"}
        assert row["evidence_regions_xyxy"].startswith("[")


def test_checked_in_scaleup_annotations_are_complete_and_labeled():
    annotation_path = ROOT / "benchmark" / "annotations" / "scaleup_model_assisted_annotations.jsonl"
    summary_path = ROOT / "benchmark" / "annotations" / "scaleup_model_assisted_annotation_summary.json"
    if not annotation_path.exists():
        return
    with annotation_path.open("r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    with summary_path.open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    assert len(rows) == summary["row_count"] == 588
    assert "not human/domain-expert ground truth" in summary["provenance"]
    assert summary["answer_counts"] == {"compliant": 250, "violation": 338}


def test_model_output_schema_file_lists_required_fields():
    schema_path = ROOT / "benchmark" / "model_output_schema.json"
    with schema_path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    assert schema["required_fields"] == MODEL_OUTPUT_FIELDS
    assert "invalid" in schema["answer_values"]


def test_model_harness_runs_annotation_bootstrap_adapter():
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    items = load_model_inputs(
        ROOT / "benchmark" / "splits" / "pilot_manifest.csv",
        {rule.rule_id: rule for rule in rules.rules},
    )
    annotations = load_annotations_by_key(
        ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl"
    )
    adapter = adapter_by_name(
        "annotation_bootstrap",
        annotations_path=ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl",
    )
    rows = run_adapter(adapter, items[:3])
    assert len(rows) == 3
    assert len(annotations) == 163
    assert rows[0]["answer"] == "violation"
    assert rows[0]["model_id"] == "baseline/model_assisted_annotation_v1"
    validate_output_row(rows[0])


def test_image_blind_majority_baseline_emits_no_evidence():
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    items = load_model_inputs(
        ROOT / "benchmark" / "splits" / "pilot_manifest.csv",
        {rule.rule_id: rule for rule in rules.rules},
    )
    rows = run_adapter(adapter_by_name("majority_violation"), items[:1])
    assert rows[0]["answer"] == "violation"
    assert rows[0]["evidence_objects"] == "[]"
    assert rows[0]["provenance"] == "deterministic_baseline_no_image_access"


def test_caption_keyword_baseline_predicts_from_caption_only():
    answer, rationale = caption_keyword_answer(
        "ppe_hard_hat",
        "A worker is not wearing a hard hat near concrete forms.",
    )
    assert answer == "violation"
    assert "Caption" in rationale
    answer, _ = caption_keyword_answer("struck_by_equipment", "An excavator is parked on soil.")
    assert answer == "compliant"


def test_intervention_specs_from_manifest_create_targeted_and_controls():
    rows = load_manifest_rows(ROOT / "benchmark" / "splits" / "pilot_manifest.csv")[:2]
    specs = build_intervention_specs_from_manifest(rows, random_seeds=[42, 43])
    assert len(specs) == 6
    assert specs[0].intervention_type == "targeted_occlusion"
    assert specs[1].intervention_type == "matched_random_occlusion"
    assert specs[1].seed == 42
    assert specs[0].to_row()["mask_target_iou"] == "1.0"


def test_intervention_output_summary_reports_paired_differences():
    baseline = [
        {
            "image_id": "0000001",
            "rule_id": "ppe_hard_hat",
            "answer": "compliant",
            "evidence_regions_xyxy": "[[10,10,20,20]]",
        }
    ]
    interventions = [
        {
            "intervention_id": "0000001:ppe_hard_hat:targeted",
            "image_id": "0000001",
            "rule_id": "ppe_hard_hat",
            "intervention_type": "targeted_occlusion",
            "seed": "",
            "target_box_xyxy": "[10,10,20,20]",
            "mask_box_xyxy": "[10,10,20,20]",
            "mask_target_iou": "1.0",
            "model_id": "m",
            "prompt_id": "p",
            "answer": "violation",
            "evidence_regions_xyxy": "[[30,10,40,20]]",
            "worker_boxes_xyxy": "[]",
            "object_boxes_xyxy": "[[30,10,40,20]]",
            "confidence": "1.0",
            "graded_score": "0.0",
            "raw_response": "{}",
            "provenance": "test",
        },
        {
            "intervention_id": "0000001:ppe_hard_hat:matched_random:42",
            "image_id": "0000001",
            "rule_id": "ppe_hard_hat",
            "intervention_type": "matched_random_occlusion",
            "seed": "42",
            "target_box_xyxy": "",
            "mask_box_xyxy": "[40,40,50,50]",
            "mask_target_iou": "0.0",
            "model_id": "m",
            "prompt_id": "p",
            "answer": "compliant",
            "evidence_regions_xyxy": "[[11,10,21,20]]",
            "worker_boxes_xyxy": "[]",
            "object_boxes_xyxy": "[[11,10,21,20]]",
            "confidence": "1.0",
            "graded_score": "1.0",
            "raw_response": "{}",
            "provenance": "test",
        },
    ]
    for row in interventions:
        validate_intervention_row(row)
    summary, details = summarize_intervention_outputs(
        intervention_rows=interventions,
        baseline_rows=baseline,
        manifest_by_key={("0000001", "ppe_hard_hat"): {"image_width": "100", "image_height": "100"}},
    )
    metrics = {row["metric_id"]: row for row in summary}
    assert metrics["targeted_answer_flip_rate"]["value"] == "1.0"
    assert metrics["matched_random_answer_flip_rate"]["value"] == "0.0"
    assert metrics["paired_answer_flip_rate_difference"]["value"] == "1.0"
    assert len(details) == 2


def test_score_model_outputs_compares_answers_and_evidence():
    rows = load_jsonl(ROOT / "results" / "frozen_model_outputs" / "pilot_annotation_bootstrap.jsonl")
    summary = score_model_outputs(
        model_output_rows=rows,
        annotations_by_key=load_annotations(
            ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl"
        ),
        manifest_by_key=load_manifest_by_key(ROOT / "benchmark" / "splits" / "pilot_manifest.csv"),
    )
    metrics = {row["metric_id"]: row for row in summary.summary_rows}
    assert metrics["accuracy"]["value"] == "1.0"
    assert metrics["macro_f1"]["value"] == "1.0"
    assert int(metrics["accuracy"]["n"]) == 163
    assert len(summary.example_rows) == 163


def test_majority_violation_baseline_scores_below_seed_labels():
    rows = load_jsonl(ROOT / "results" / "frozen_model_outputs" / "pilot_majority_violation.jsonl")
    summary = score_model_outputs(
        model_output_rows=rows,
        annotations_by_key=load_annotations(
            ROOT / "benchmark" / "annotations" / "pilot_model_assisted_annotations.jsonl"
        ),
        manifest_by_key=load_manifest_by_key(ROOT / "benchmark" / "splits" / "pilot_manifest.csv"),
    )
    metrics = {row["metric_id"]: row for row in summary.summary_rows}
    assert float(metrics["accuracy"]["value"]) < 1.0
    assert metrics["evidence_presence_rate"]["value"] == "0.0"


def test_score_slice_analyzer_groups_by_rule_and_ambiguity():
    rows = [
        {
            "rule_id": "ppe_hard_hat",
            "answer_correct": "true",
            "invalid_output": "false",
            "has_predicted_evidence": "true",
            "has_reference_evidence": "true",
            "best_evidence_iou": "0.5",
            "best_evidence_centroid_drift": "0.1",
            "annotation_ambiguous": "no",
            "annotation_applies_to_image": "yes",
        },
        {
            "rule_id": "fall_harness",
            "answer_correct": "false",
            "invalid_output": "false",
            "has_predicted_evidence": "false",
            "has_reference_evidence": "false",
            "best_evidence_iou": "",
            "best_evidence_centroid_drift": "",
            "annotation_ambiguous": "yes",
            "annotation_applies_to_image": "uncertain",
        },
    ]
    slices = build_slices(rows)
    keyed = {(row["slice_type"], row["slice_value"]): row for row in slices}
    assert keyed[("overall", "all")]["accuracy"] == "0.5"
    assert keyed[("rule_id", "ppe_hard_hat")]["mean_best_evidence_iou"] == "0.5"
    assert keyed[("annotation_ambiguous", "yes")]["evidence_presence_rate"] == "0.0"


def test_human_audit_batch_prioritizes_disagreement_rows():
    score_row = {
        "image_id": "0000001",
        "rule_id": "ppe_hard_hat",
        "truth_answer": "violation",
        "predicted_answer": "compliant",
        "answer_correct": "false",
        "annotation_ambiguous": "no",
        "annotation_applies_to_image": "yes",
        "has_reference_evidence": "true",
        "has_predicted_evidence": "true",
        "best_evidence_iou": "0.05",
        "best_evidence_centroid_drift": "0.2",
    }
    score, reason = priority_for(score_row)
    assert score == 170
    assert "florence_disagrees_with_bootstrap" in reason
    rows = build_batch(
        scores=[score_row],
        manifest_rows=[
            {
                "image_id": "0000001",
                "rule_id": "ppe_hard_hat",
                "image_width": "100",
                "image_height": "80",
                "image_caption": "A worker is visible.",
                "source_violation_boxes_xyxy": "[[1,2,3,4]]",
            }
        ],
        annotation_rows=[
            {
                "image_id": "0000001",
                "rule_id": "ppe_hard_hat",
                "evidence_regions_xyxy": "[[1,2,3,4]]",
            }
        ],
        questions_by_rule={"ppe_hard_hat": "Is each visible worker wearing required head protection?"},
        batch_size=1,
        per_rule_cap=1,
    )
    assert rows[0]["audit_id"] == "audit_001_0001"
    assert rows[0]["annotator_1_answer_label"] == ""
    assert rows[0]["priority_score"] == "170"


def test_human_audit_status_handles_unfilled_and_completed_rows():
    rows = [
        {
            "annotator_1_answer_label": "",
            "annotator_2_answer_label": "",
            "adjudicated_answer_label": "",
        },
        {
            "annotator_1_answer_label": "violation",
            "annotator_2_answer_label": "violation",
            "adjudicated_answer_label": "violation",
        },
    ]
    summary = summarize_human_audit_status(rows)
    metrics = {row["metric_id"]: row for row in summary}
    assert metrics["row_count"]["value"] == "2.0"
    assert metrics["dual_annotation_completion_rate"]["value"] == "0.5"
    assert metrics["raw_answer_agreement"]["value"] == "1.0"


def test_scaleup_classification_and_rule_choice():
    row = {
        "rule_1_violation": None,
        "rule_2_violation": {"reason": "missing harness", "bounding_box": [[0, 0, 1, 1]]},
        "rule_3_violation": None,
        "rule_4_violation": None,
    }
    primary_class, violated = classify_source_row(row)
    assert primary_class == "fall_hazard"
    assert violated == ["rule_2_violation"]
    rule_id, note = choose_rule_for_row(
        primary_class="compliant",
        violated_fields=[],
        compliant_index=0,
        has_excavator=False,
    )
    assert rule_id == "ppe_hard_hat"
    assert note == "compliant_context_metadata_unconfirmed"


def test_scaleup_candidate_selection_with_fake_rows():
    class FakeImage:
        size = (100, 80)

    rows = [
        {
            "image_id": "1",
            "image": FakeImage(),
            "image_caption": "A worker is visible.",
            "quality_of_info": "rich info",
            "rule_1_violation": None,
            "rule_2_violation": None,
            "rule_3_violation": None,
            "rule_4_violation": None,
            "excavator": [],
        },
        {
            "image_id": "2",
            "image": FakeImage(),
            "image_caption": "A worker lacks a hard hat.",
            "quality_of_info": "rich info",
            "rule_1_violation": {"reason": "missing hard hat", "bounding_box": [[0.1, 0.1, 0.2, 0.2]]},
            "rule_2_violation": None,
            "rule_3_violation": None,
            "rule_4_violation": None,
            "excavator": [],
        },
    ]
    rules = load_rules(ROOT / "benchmark" / "rules.json")
    selected = select_scaleup_candidates(rows, rules=rules, per_class=1, seed=7)
    assert len(selected) == 2
    assert {row["expected_answer_seed"] for row in selected} == {"compliant", "violation"}
    violation = next(row for row in selected if row["expected_answer_seed"] == "violation")
    assert violation["rule_id"] == "ppe_hard_hat"
    assert violation["source_violation_boxes_xyxy"] == "[[10,8,20,16]]"
