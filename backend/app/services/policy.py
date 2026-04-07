def get_policy_rules():
    return {
        "limits": {
            "Meals": 2000,
            "Transport": 3000,
            "Lodging": 7000
        },
        "prohibited_keywords": [
            "alcohol",
            "beer",
            "wine",
            "whiskey",
            "cigarette",
            "tobacco"
        ]
    }