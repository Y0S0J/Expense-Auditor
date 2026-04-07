import re


def _extract_line_amount(line: str):
    values = re.findall(r"([0-9]+\.[0-9]{2})", line)
    if values:
        return max(float(v) for v in values)

    values = re.findall(r"\b([0-9]{2,6})\b", line)
    if values:
        nums = [float(v) for v in values]
        nums = [n for n in nums if not (1900 <= n <= 2100)]
        if nums:
            return max(nums)

    return 0.0


def _extract_keyword_item_values(raw_text, prohibited_keywords):
    if not raw_text:
        return []

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    found_items = []

    for line in lines:
        line_lower = line.lower()

        for group_name, keywords in prohibited_keywords.items():
            matched_keywords = [kw for kw in keywords if kw in line_lower]

            if matched_keywords:
                found_items.append({
                    "group": group_name,
                    "matched_keywords": matched_keywords,
                    "line": line,
                    "amount": _extract_line_amount(line)
                })
                break

    return found_items


def evaluate_expense(expense, rules):
    claimed_amount = float(expense.get("claimed_amount") or 0)
    detected_amount = expense.get("detected_amount")
    claimed_date = expense.get("claimed_date")
    receipt_date = expense.get("receipt_date")
    category = expense.get("category")
    approved_budget = expense.get("approved_budget")
    raw_text = expense.get("raw_text") or ""

    if detected_amount is None:
        return {
            "status": "FLAGGED",
            "reason": "The system could not reliably detect the final amount from the receipt.",
            "adjusted_amount": None,
            "deductions": []
        }

    detected_amount = float(detected_amount)

    prohibited_keywords = rules.get("prohibited_keywords", {})
    deductions = _extract_keyword_item_values(raw_text, prohibited_keywords)
    deducted_total = round(sum(item["amount"] for item in deductions), 2)
    adjusted_amount = round(detected_amount - deducted_total, 2)

    if adjusted_amount < 0:
        adjusted_amount = 0.0

    # If everything is prohibited or deducted value wipes out the claim
    if deductions and adjusted_amount <= 0:
        matched_words = []
        for item in deductions:
            matched_words.extend(item["matched_keywords"])
        matched_words = sorted(set(matched_words))
        matched_words_text = ", ".join(matched_words)

        return {
            "status": "DECLINED",
            "reason": (
                f"The receipt appears to contain only prohibited items ({matched_words_text}). "
                f"The claim is not reimbursable."
            ),
            "adjusted_amount": adjusted_amount,
            "deductions": deductions
        }

    # Date mismatch check
    if receipt_date and claimed_date and receipt_date != claimed_date:
        return {
            "status": "FLAGGED",
            "reason": f"Claimed date ({claimed_date}) does not match receipt date ({receipt_date}).",
            "adjusted_amount": adjusted_amount,
            "deductions": deductions
        }

    # Company category policy limit
    category_limit = rules.get("limits", {}).get(category)
    if category_limit is not None and adjusted_amount > float(category_limit):
        return {
            "status": "FLAGGED",
            "reason": f"Adjusted claim amount ({adjusted_amount}) exceeds company policy limit for {category} ({category_limit}).",
            "adjusted_amount": adjusted_amount,
            "deductions": deductions
        }

    # Boss-approved budget must never be exceeded
    if approved_budget is not None and adjusted_amount > float(approved_budget):
        return {
            "status": "FLAGGED",
            "reason": f"Adjusted claim amount ({adjusted_amount}) exceeds the boss-approved budget ({approved_budget}).",
            "adjusted_amount": adjusted_amount,
            "deductions": deductions
        }

    # If prohibited items exist, subtract them and compare
    if deductions:
        matched_words = []
        for item in deductions:
            matched_words.extend(item["matched_keywords"])

        matched_words = sorted(set(matched_words))
        matched_words_text = ", ".join(matched_words)

        if abs(claimed_amount - adjusted_amount) <= 1:
            return {
                "status": "APPROVED",
                "reason": (
                    f"Prohibited item values were excluded ({matched_words_text}), "
                    f"and the adjusted final amount ({adjusted_amount}) matches the employee claim."
                ),
                "adjusted_amount": adjusted_amount,
                "deductions": deductions
            }

        return {
            "status": "FLAGGED",
            "reason": (
                f"Prohibited item values were detected ({matched_words_text}). "
                f"After deducting them, the adjusted final amount is {adjusted_amount}, "
                f"which does not match the employee claim ({claimed_amount})."
            ),
            "adjusted_amount": adjusted_amount,
            "deductions": deductions
        }

    # No prohibited items → normal compare
    if abs(claimed_amount - detected_amount) <= 1:
        return {
            "status": "APPROVED",
            "reason": "The expense matches the receipt, approved budget, and company policy.",
            "adjusted_amount": detected_amount,
            "deductions": []
        }

    return {
        "status": "FLAGGED",
        "reason": f"Claimed amount ({claimed_amount}) does not match detected receipt amount ({detected_amount}).",
        "adjusted_amount": detected_amount,
        "deductions": []
    }