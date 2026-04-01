def evaluate_expense(expense, rules):
    amount = expense["amount"]
    limit = rules.get("limit", None)

    if limit and amount > limit:
        return {
            "status": "Rejected",
            "reason": f"Amount exceeds limit of {limit}"
        }

    return {
        "status": "Approved",
        "reason": "Within policy limits"
    }