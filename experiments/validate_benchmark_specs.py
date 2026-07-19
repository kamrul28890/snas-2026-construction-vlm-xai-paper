"""Validate benchmark specification files without running model inference."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from faithbench.schema import load_prompts, load_rules


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    rules = load_rules(root / "benchmark" / "rules.json")
    prompts = load_prompts(root / "benchmark" / "prompts" / "safety_rule_prompts.json")
    print(f"Loaded {len(rules.rules)} safety rules.")
    print(f"Loaded {len(prompts.prompts)} prompt templates.")
    for rule in rules.rules:
        rendered = prompts.prompts[0].render(question=rule.question)
        if rule.question not in rendered:
            raise RuntimeError(f"Prompt rendering failed for {rule.rule_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
