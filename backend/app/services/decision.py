def evaluate_expense(expense, rules):
    claimed_amount = expense.get("claimed_amount")
    detected_amount = expense.get("detected_amount")
    claimed_date = expense.get("claimed_date")
    receipt_date = expense.get("receipt_date")
    category = expense.get("category")
    purpose = (expense.get("business_purpose") or "").lower()

    if detected_amount is None:
        return {
            "status": "FLAGGED",
            "reason": "The system could not reliably detect the final amount from the receipt."
        }

    if abs(float(claimed_amount) - float(detected_amount)) > 1:
        return {
            "status": "FLAGGED",
            "reason": f"Claimed amount ({claimed_amount}) does not match detected receipt amount ({detected_amount})."
        }

    if receipt_date and claimed_date and receipt_date != claimed_date:
        return {
            "status": "FLAGGED",
            "reason": f"Claimed date ({claimed_date}) does not match receipt date ({receipt_date})."
        }

    limit = rules.get("limits", {}).get(category)
    if limit is not None and float(claimed_amount) > float(limit):
        return {
            "status": "DECLINED",
            "reason": f"The claimed amount exceeds the allowed policy limit for {category} ({limit})."
        }

    for word in rules.get("prohibited_keywords", []):
        if word in purpose:
            return {
                "status": "DECLINED",
                "reason": f"The claim contains a prohibited item: {word}."
            }

    return {
        "status": "APPROVED",
        "reason": "The expense matches the receipt and complies with company policy."
    }