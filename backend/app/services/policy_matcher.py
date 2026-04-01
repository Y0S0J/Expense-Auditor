def get_policy_rules(category):
    rules = {
        "Meals": {
            "limit": 2000,
            "no_alcohol": True
        },
        "Transport": {
            "limit": 3000
        }
    }
    return rules.get(category, {})