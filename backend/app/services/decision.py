def evaluate_expense(expense, rules):
    claimed_amount = expense.get("claimed_amount")
    detected_amount = expense.get("detected_amount")
    claimed_date = expense.get("claimed_date")
    receipt_date = expense.get("receipt_date")
    category = expense.get("category")
    purpose = (expense.get("business_purpose") or "").lower()

    if detected_amount is None:
        return {
            "status": "Flagged",
            "reason": "Could not reliably detect amount from receipt."
        }

    if abs(claimed_amount - detected_amount) > 1:
        return {
            "status": "Flagged",
            "reason": f"Claimed amount ({claimed_amount}) does not match receipt amount ({detected_amount})."
        }

    if receipt_date and claimed_date and receipt_date != claimed_date:
        return {
            "status": "Flagged",
            "reason": "Claimed date does not match receipt date."
        }

    limit = rules.get(category)
    if limit and claimed_amount > limit:
        return {
            "status": "Declined",
            "reason": f"Amount exceeds {category} limit ({limit})."
        }

    for word in rules.get("prohibited_keywords", []):
        if word in purpose:
            return {
                "status": "Declined",
                "reason": f"Contains prohibited item: {word}"
            }

    return {
        "status": "Approved",
        "reason": "Claim matches policy and receipt."
    }