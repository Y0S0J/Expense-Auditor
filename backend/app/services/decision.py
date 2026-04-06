def evaluate_expense(expense, rules):
    claimed_amount = expense.get("claimed_amount")
    detected_amount = expense.get("detected_amount")
    claimed_date = expense.get("claimed_date")
    receipt_date = expense.get("receipt_date")
    business_purpose = (expense.get("business_purpose") or "").lower()

    if detected_amount is None:
        return {
            "status": "Flagged",
            "reason": "The receipt amount could not be read clearly. Please review the uploaded receipt."
        }

    if abs(claimed_amount - detected_amount) > 1:
        return {
            "status": "Flagged",
            "reason": f"The claimed amount ({claimed_amount}) does not match the detected receipt amount ({detected_amount})."
        }

    if receipt_date and claimed_date and receipt_date != claimed_date:
        return {
            "status": "Flagged",
            "reason": f"The claimed date ({claimed_date}) does not match the receipt date ({receipt_date})."
        }

    for word in rules.get("prohibited_keywords", []):
        if word in business_purpose:
            return {
                "status": "Declined",
                "reason": f"The expense includes a prohibited item: {word}."
            }

    limit = rules.get("default_limit")
    if limit is not None and claimed_amount > limit:
        return {
            "status": "Declined",
            "reason": f"The claimed amount exceeds the allowed policy limit of {limit}."
        }

    return {
        "status": "Approved",
        "reason": "The expense matches the receipt and complies with the policy rules."
    }