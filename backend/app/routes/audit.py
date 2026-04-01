from fastapi import APIRouter
from app.services.ocr_services import extract_receipt_data
from app.services.policy_matcher import get_policy_rules
from app.services.decision import evaluate_expense

router = APIRouter()

@router.get("/audit")
def audit_expense():
    # For now using a sample file path
    file_path = "sample_receipt.jpg"

    expense = extract_receipt_data(file_path)
    rules = get_policy_rules(expense["category"])
    result = evaluate_expense(expense, rules)

    return {
        "expense": expense,
        "rules": rules,
        "result": result
    }