import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from estimator.config import MODEL_VERSION, QUESTIONNAIRE_VERSION, SCHEMA_ROOT


@lru_cache(maxsize=1)
def load_questionnaire(version: str = QUESTIONNAIRE_VERSION) -> dict[str, Any]:
    path = SCHEMA_ROOT / "questionnaire" / f"v{version}.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_priors(version: str = "1.0") -> dict[str, Any]:
    path = SCHEMA_ROOT / "model" / f"v{version}" / "priors.yaml"
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache(maxsize=1)
def load_hypothesis_rule_map() -> dict[str, Any]:
    path = SCHEMA_ROOT / "hypothesis-rule-map.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_rule_priors(version: str = "1.0") -> dict[str, Any]:
    path = SCHEMA_ROOT / "model" / f"v{version}" / "rule-priors.yaml"
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def get_question_by_id(question_id: str, version: str = QUESTIONNAIRE_VERSION) -> dict[str, Any] | None:
    questionnaire = load_questionnaire(version)
    for question in questionnaire["questions"]:
        if question["id"] == question_id:
            return question
    return None


def list_all_question_ids(version: str = QUESTIONNAIRE_VERSION) -> list[str]:
    return [q["id"] for q in load_questionnaire(version)["questions"]]
