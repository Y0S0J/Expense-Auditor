import json
import os
from app.config import GENERATED_RULES_PATH


def get_policy_rules(category: str):
    if not os.path.exists(GENERATED_RULES_PATH):
        return {}

    with open(GENERATED_RULES_PATH, "r", encoding="utf-8") as f:
        rules = json.load(f)

    category_rules = rules.get(category, {})
    general_rules = rules.get("General", {})

    merged = dict(category_rules)
    merged["prohibited_keywords"] = general_rules.get("prohibited_keywords", [])
    return merged