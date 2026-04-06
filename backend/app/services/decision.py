def evaluate_expense(expense, rules):
    claimed_amount = expense.get("claimed_amount")
    detected_amount = expense.get("detected_amount")
    claimed_date = expense.get("claimed_date")
    receipt_date = expense.get("receipt_date")
    business_purpose = (expense.get("business_purpose") or "").lower()

    if detected_amount is None:
        return {
            "status": "Flagged",
            "reason": "Could not reliably read amount from the receipt."
        }

    if abs(claimed_amount - detected_amount) > 1:
        return {
            "status": "Flagged",
            "reason": f"Claimed amount ({claimed_amount}) does not match detected receipt amount ({detected_amount})."
        }

    if receipt_date and claimed_date and receipt_date != claimed_date:
        return {
            "status": "Flagged",
            "reason": f"Receipt date ({receipt_date}) does not match claimed date ({claimed_date})."
        }

    for word in rules.get("prohibited_keywords", []):
        if word in business_purpose:
            return {
                "status": "Rejected",
                "reason": f"Expense contains prohibited item: {word}."
            }

    limit = rules.get("default_limit")
    if limit is not None and claimed_amount > limit:
        return {
            "status": "Rejected",
            "reason": f"Claimed amount exceeds allowed policy limit of {limit}."
        }

    return {
        "status": "Approved",
        "reason": "Expense complies with the current policy rules."
    }