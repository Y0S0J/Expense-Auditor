def get_policy_rules():
    return {
        "limits": {
            "Meals": 2000,
            "Transport": 3000,
            "Lodging": 7000
        },
        "prohibited_keywords": {
            "alcohol_generic": [
                "alcohol",
                "beer",
                "wine",
                "whiskey",
                "whisky",
                "vodka",
                "rum",
                "gin",
                "brandy",
                "scotch",
                "lager",
                "stout",
                "liquor",
                "cocktail",
                "champagne",
                "tequila"
            ],
            "alcohol_brands": [
                "heineken",
                "budweiser",
                "corona",
                "carlsberg",
                "kingfisher",
                "tuborg",
                "guinness",
                "jack daniels",
                "johnnie walker",
                "johnny walker",
                "chivas",
                "chivas regal",
                "black label",
                "red label",
                "absolut",
                "smirnoff",
                "bacardi",
                "captain morgan",
                "ballantine",
                "jameson"
            ],
            "smoking_generic": [
                "cigarette",
                "cigarettes",
                "tobacco",
                "smoke",
                "smoking"
            ],
            "smoking_brands": [
                "marlboro",
                "gold flake",
                "wills",
                "camel",
                "dunhill"
            ]
        }
    }