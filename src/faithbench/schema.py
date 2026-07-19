"""Load and validate benchmark rule and prompt specifications."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SafetyRule:
    """A construction-safety rule used for model prompts and scoring."""

    rule_id: str
    rule_family: str
    short_name: str
    question: str
    compliant_condition: str
    violation_condition: str
    primary_evidence_objects: tuple[str, ...]
    counterfactual_target_objects: tuple[str, ...]
    known_ambiguities: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkRules:
    """Validated rule collection."""

    schema_version: str
    answer_labels: tuple[str, ...]
    rules: tuple[SafetyRule, ...]

    def by_id(self, rule_id: str) -> SafetyRule:
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        raise KeyError(f"Unknown rule_id: {rule_id}")


@dataclass(frozen=True)
class PromptTemplate:
    """Prompt template with a stable identifier."""

    prompt_id: str
    template: str

    def render(self, *, question: str) -> str:
        return self.template.format(question=question)


@dataclass(frozen=True)
class PromptSet:
    """Validated prompt-template collection."""

    schema_version: str
    prompts: tuple[PromptTemplate, ...]

    def by_id(self, prompt_id: str) -> PromptTemplate:
        for prompt in self.prompts:
            if prompt.prompt_id == prompt_id:
                return prompt
        raise KeyError(f"Unknown prompt_id: {prompt_id}")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_rules(path: str | Path) -> BenchmarkRules:
    """Load and minimally validate `benchmark/rules.json`."""
    data = _read_json(Path(path))
    rules = []
    seen = set()
    for raw in data["rules"]:
        rule_id = raw["rule_id"]
        if rule_id in seen:
            raise ValueError(f"Duplicate rule_id: {rule_id}")
        seen.add(rule_id)
        rules.append(
            SafetyRule(
                rule_id=rule_id,
                rule_family=raw["rule_family"],
                short_name=raw["short_name"],
                question=raw["question"],
                compliant_condition=raw["compliant_condition"],
                violation_condition=raw["violation_condition"],
                primary_evidence_objects=tuple(raw["primary_evidence_objects"]),
                counterfactual_target_objects=tuple(raw["counterfactual_target_objects"]),
                known_ambiguities=tuple(raw.get("known_ambiguities", [])),
            )
        )
    answer_labels = tuple(data["answer_labels"])
    required = {"compliant", "violation", "uncertain", "invalid"}
    missing = required - set(answer_labels)
    if missing:
        raise ValueError(f"Missing required answer labels: {sorted(missing)}")
    return BenchmarkRules(
        schema_version=data["schema_version"],
        answer_labels=answer_labels,
        rules=tuple(rules),
    )


def load_prompts(path: str | Path) -> PromptSet:
    """Load and minimally validate prompt templates."""
    data = _read_json(Path(path))
    prompts = []
    seen = set()
    for raw in data["prompts"]:
        prompt_id = raw["prompt_id"]
        if prompt_id in seen:
            raise ValueError(f"Duplicate prompt_id: {prompt_id}")
        seen.add(prompt_id)
        template = raw["template"]
        if "{question}" not in template:
            raise ValueError(f"Prompt {prompt_id} does not include {{question}}")
        prompts.append(PromptTemplate(prompt_id=prompt_id, template=template))
    return PromptSet(schema_version=data["schema_version"], prompts=tuple(prompts))

