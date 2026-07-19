"""Provider-neutral model-output harness for ConstructionSafety-FaithBench."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from faithbench.scoring import normalize_answer

MODEL_OUTPUT_FIELDS = [
    "image_id",
    "rule_id",
    "model_id",
    "prompt_id",
    "answer",
    "evidence_objects",
    "evidence_regions_xyxy",
    "rationale",
    "confidence",
    "raw_response",
    "provenance",
]


@dataclass(frozen=True)
class ModelInput:
    """One benchmark image-rule prompt request."""

    image_id: str
    rule_id: str
    question: str
    expected_answer_seed: str
    image_width: int
    image_height: int
    manifest_row: dict[str, str]


@dataclass(frozen=True)
class ModelOutput:
    """Normalized model response record."""

    image_id: str
    rule_id: str
    model_id: str
    prompt_id: str
    answer: str
    evidence_objects: list[str]
    evidence_regions_xyxy: list[list[int]]
    rationale: str
    confidence: float | None
    raw_response: str
    provenance: str

    def to_row(self) -> dict[str, str]:
        """Serialize output for JSONL/CSV writing."""
        return {
            "image_id": self.image_id,
            "rule_id": self.rule_id,
            "model_id": self.model_id,
            "prompt_id": self.prompt_id,
            "answer": normalize_answer(self.answer),
            "evidence_objects": json.dumps(self.evidence_objects, separators=(",", ":")),
            "evidence_regions_xyxy": json.dumps(self.evidence_regions_xyxy, separators=(",", ":")),
            "rationale": self.rationale,
            "confidence": "" if self.confidence is None else str(float(self.confidence)),
            "raw_response": self.raw_response,
            "provenance": self.provenance,
        }


class ModelAdapter(Protocol):
    """Minimal adapter interface for any VLM or baseline."""

    model_id: str
    prompt_id: str

    def predict(self, item: ModelInput) -> ModelOutput:
        """Return a normalized output for one image-rule request."""


class MajorityViolationBaseline:
    """Image-blind baseline that always predicts violation."""

    model_id = "baseline/majority_violation_v1"
    prompt_id = "image_blind_prior"

    def predict(self, item: ModelInput) -> ModelOutput:
        return ModelOutput(
            image_id=item.image_id,
            rule_id=item.rule_id,
            model_id=self.model_id,
            prompt_id=self.prompt_id,
            answer="violation",
            evidence_objects=[],
            evidence_regions_xyxy=[],
            rationale="Image-blind majority-class baseline.",
            confidence=None,
            raw_response='{"answer":"violation"}',
            provenance="deterministic_baseline_no_image_access",
        )


class ManifestSeedBaseline:
    """Weak-label baseline that echoes the pilot manifest answer seed."""

    model_id = "baseline/manifest_seed_v1"
    prompt_id = "manifest_seed"

    def predict(self, item: ModelInput) -> ModelOutput:
        answer = normalize_answer(item.expected_answer_seed)
        return ModelOutput(
            image_id=item.image_id,
            rule_id=item.rule_id,
            model_id=self.model_id,
            prompt_id=self.prompt_id,
            answer=answer,
            evidence_objects=[],
            evidence_regions_xyxy=[],
            rationale="Echoes the weak label from the pilot manifest; not a deployable model.",
            confidence=None,
            raw_response=json.dumps({"answer": answer}, separators=(",", ":")),
            provenance="weak_label_manifest_seed",
        )


class CaptionKeywordBaseline:
    """Caption-only baseline for leakage and shortcut checks."""

    model_id = "baseline/caption_keyword_v1"
    prompt_id = "caption_only_keywords"

    def predict(self, item: ModelInput) -> ModelOutput:
        caption = item.manifest_row.get("image_caption", "")
        answer, rationale = caption_keyword_answer(item.rule_id, caption)
        return ModelOutput(
            image_id=item.image_id,
            rule_id=item.rule_id,
            model_id=self.model_id,
            prompt_id=self.prompt_id,
            answer=answer,
            evidence_objects=[],
            evidence_regions_xyxy=[],
            rationale=rationale,
            confidence=None,
            raw_response=json.dumps({"caption": caption, "answer": answer}, separators=(",", ":")),
            provenance="caption_only_no_image_pixels",
        )


class AnnotationBootstrapAdapter:
    """Baseline that echoes completed model-assisted annotation rows."""

    model_id = "baseline/model_assisted_annotation_v1"
    prompt_id = "annotation_bootstrap"

    def __init__(self, annotations_by_key: dict[tuple[str, str], dict[str, str]]):
        self.annotations_by_key = annotations_by_key

    def predict(self, item: ModelInput) -> ModelOutput:
        annotation = self.annotations_by_key[(item.image_id, item.rule_id)]
        evidence_objects = [
            value.strip()
            for value in annotation["evidence_objects"].split(",")
            if value.strip()
        ]
        evidence_regions = json.loads(annotation["evidence_regions_xyxy"])
        answer = normalize_answer(annotation["answer_label"])
        return ModelOutput(
            image_id=item.image_id,
            rule_id=item.rule_id,
            model_id=self.model_id,
            prompt_id=self.prompt_id,
            answer=answer,
            evidence_objects=evidence_objects,
            evidence_regions_xyxy=evidence_regions,
            rationale=annotation["free_text_notes"],
            confidence=None,
            raw_response=json.dumps(annotation, separators=(",", ":")),
            provenance="model_assisted_annotation_echo_not_independent_model",
        )


def load_model_inputs(manifest_path: Path, rules_by_id: dict[str, object]) -> list[ModelInput]:
    """Load benchmark manifest rows as model-input requests."""
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    items = []
    for row in rows:
        rule = rules_by_id[row["rule_id"]]
        items.append(
            ModelInput(
                image_id=row["image_id"],
                rule_id=row["rule_id"],
                question=rule.question,
                expected_answer_seed=row["expected_answer_seed"],
                image_width=int(row["image_width"]),
                image_height=int(row["image_height"]),
                manifest_row=row,
            )
        )
    return items


def load_annotations_by_key(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    """Load JSONL annotations keyed by image and rule."""
    annotations: dict[tuple[str, str], dict[str, str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            key = (row["image_id"], row["rule_id"])
            if key in annotations:
                raise ValueError(f"Duplicate annotation key: {key}")
            annotations[key] = row
    return annotations


def adapter_by_name(name: str, *, annotations_path: Path | None = None) -> ModelAdapter:
    """Create a built-in deterministic model adapter."""
    if name == "majority_violation":
        return MajorityViolationBaseline()
    if name == "manifest_seed":
        return ManifestSeedBaseline()
    if name == "caption_keyword":
        return CaptionKeywordBaseline()
    if name == "annotation_bootstrap":
        if annotations_path is None:
            raise ValueError("annotation_bootstrap requires annotations_path")
        return AnnotationBootstrapAdapter(load_annotations_by_key(annotations_path))
    raise KeyError(f"Unknown model adapter: {name}")


def caption_keyword_answer(rule_id: str, caption: str) -> tuple[str, str]:
    """Return a rule-specific caption-only keyword prediction."""
    text = caption.lower()
    negative_terms = [
        "without",
        "not wearing",
        "no hard hat",
        "no helmet",
        "missing",
        "unprotected",
        "unsafe",
        "near excavator",
        "close to excavator",
        "edge without",
        "opening not protected",
    ]
    if any(term in text for term in negative_terms):
        return "violation", "Caption contains violation-like wording."
    if rule_id == "ppe_hard_hat":
        if any(term in text for term in ["hard hat", "helmet", "head protection"]):
            return "compliant", "Caption mentions head protection without violation wording."
        if "worker" in text:
            return "uncertain", "Caption mentions workers but no head-protection evidence."
    if rule_id == "fall_harness":
        if any(term in text for term in ["harness", "fall protection", "lanyard"]):
            return "compliant", "Caption mentions fall-protection equipment without violation wording."
        if any(term in text for term in ["height", "roof", "scaffold", "ladder"]):
            return "uncertain", "Caption suggests height context but no harness evidence."
    if rule_id == "guardrail_edge":
        if any(term in text for term in ["guardrail", "barrier", "protected"]):
            return "compliant", "Caption mentions edge protection without violation wording."
        if any(term in text for term in ["edge", "opening", "pit", "rebar cage"]):
            return "uncertain", "Caption suggests edge/opening context but no protection evidence."
    if rule_id == "struck_by_equipment":
        if any(term in text for term in ["excavator", "crane", "loader", "truck", "equipment"]):
            if "worker" in text or "workers" in text:
                return "uncertain", "Caption mentions workers and heavy equipment but no distance evidence."
            return "compliant", "Caption mentions equipment without worker-proximity evidence."
    return "uncertain", "Caption lacks enough rule-specific evidence."


def run_adapter(adapter: ModelAdapter, items: list[ModelInput]) -> list[dict[str, str]]:
    """Run an adapter on model inputs and return serialized rows."""
    rows = []
    for item in items:
        row = adapter.predict(item).to_row()
        validate_output_row(row)
        rows.append(row)
    return rows


def validate_output_row(row: dict[str, str]) -> None:
    """Validate one serialized model-output row."""
    missing = [field for field in MODEL_OUTPUT_FIELDS if field not in row]
    if missing:
        raise ValueError(f"Missing model output fields: {missing}")
    answer = normalize_answer(row["answer"])
    if answer == "invalid" and row["answer"] != "invalid":
        raise ValueError(f"Invalid answer label: {row['answer']}")
    objects = json.loads(row["evidence_objects"])
    boxes = json.loads(row["evidence_regions_xyxy"])
    if not isinstance(objects, list):
        raise ValueError("evidence_objects must be a JSON list")
    if not isinstance(boxes, list):
        raise ValueError("evidence_regions_xyxy must be a JSON list")


def write_model_outputs(rows: list[dict[str, str]], *, jsonl_path: Path, csv_path: Path) -> None:
    """Write normalized model outputs as JSONL and CSV."""
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MODEL_OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
