from fastapi import APIRouter, Form
import os

from app.config import RECEIPT_DIR
from app.services.ocr_services import extract_receipt_data
from app.services.policy_matcher import get_policy_rules
from app.services.decision import evaluate_expense

router = APIRouter()


@router.post("/audit")
def audit_expense(
    filename: str = Form(...),
    category: str = Form(...),
    claimed_amount: float = Form(...),
    claimed_date: str = Form(...),
    business_purpose: str = Form(...)
):
    file_path = os.path.join(RECEIPT_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": "Receipt file not found. Please upload it first."}

    ocr_data = extract_receipt_data(file_path)
    rules = get_policy_rules(category)

    expense = {
        "filename": filename,
        "category": category,
        "claimed_amount": claimed_amount,
        "claimed_date": claimed_date,
        "business_purpose": business_purpose,
        "detected_amount": ocr_data.get("detected_amount"),
        "receipt_date": ocr_data.get("receipt_date"),
    }

    result = evaluate_expense(expense, rules)

    return {
        "expense": expense,
        "ocr_data": ocr_data,
        "applied_rules": rules,
        "result": result
    }