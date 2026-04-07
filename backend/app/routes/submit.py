from fastapi import APIRouter, UploadFile, File
import shutil
import os

from app.database import get_connection
from app.services.ocr_services import extract_receipt_data
from app.services.policy import get_policy_rules
from app.services.decision import evaluate_expense

router = APIRouter()

UPLOAD_DIR = "app/data/receipts"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/claims/submit")
def submit_claim(
    sequence_code: str,
    category: str,
    amount: float,
    date: str,
    purpose: str,
    file: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ocr = extract_receipt_data(file_path)
    rules = get_policy_rules()

    expense = {
        "claimed_amount": amount,
        "claimed_date": date,
        "business_purpose": purpose,
        "category": category,
        "detected_amount": ocr.get("detected_amount"),
        "receipt_date": ocr.get("receipt_date"),
    }

    result = evaluate_expense(expense, rules)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE claims
    SET actual_amount=?, actual_date=?, actual_purpose=?, receipt_path=?,
        ocr_amount=?, ocr_date=?, status=?, system_reason=?
    WHERE sequence_code=?
    """, (
        amount, date, purpose, file_path,
        ocr.get("detected_amount"), ocr.get("receipt_date"),
        result["status"], result["reason"],
        sequence_code
    ))

    conn.commit()
    conn.close()

    return result