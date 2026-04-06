import re
from typing import Dict, Any


def _find_limit(policy_text: str, keywords: list[str]):
    lines = policy_text.splitlines()

    for line in lines:
        line_lower = line.lower()
        if any(k in line_lower for k in keywords):
            match = re.search(r"(?:rs\.?|inr|qar|usd|aed|\$)?\s*(\d{2,6})", line_lower)
            if match:
                return int(match.group(1))
    return None


def generate_rules_from_text(policy_text: str) -> Dict[str, Any]:
    text_lower = policy_text.lower()

    rules = {
        "Meals": {},
        "Transport": {},
        "Lodging": {},
        "General": {
            "prohibited_keywords": []
        }
    }

    meals_limit = _find_limit(text_lower, ["meal", "meals", "food", "dinner", "lunch"])
    transport_limit = _find_limit(text_lower, ["transport", "taxi", "cab", "travel"])
    lodging_limit = _find_limit(text_lower, ["lodging", "hotel", "accommodation", "stay"])

    if meals_limit is not None:
        rules["Meals"]["default_limit"] = meals_limit
    if transport_limit is not None:
        rules["Transport"]["default_limit"] = transport_limit
    if lodging_limit is not None:
        rules["Lodging"]["default_limit"] = lodging_limit

    prohibited = []
    for word in ["alcohol", "beer", "wine", "whiskey", "cigarette", "tobacco"]:
        if word in text_lower:
            prohibited.append(word)

    rules["General"]["prohibited_keywords"] = prohibited

    rules["raw_policy_summary"] = {
        "meals_limit_found": meals_limit,
        "transport_limit_found": transport_limit,
        "lodging_limit_found": lodging_limit,
        "prohibited_found": prohibited,
    }

    return rules