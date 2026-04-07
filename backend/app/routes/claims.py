from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.database import get_connection
from app.services.sequence import generate_sequence_code
from app.services.notification import create_notification
from app.services.ocr_services import extract_receipt_data
from app.services.policy import get_policy_rules
from app.services.decision import evaluate_expense

router = APIRouter()

UPLOAD_DIR = "app/data/receipts"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/claims/request")
def request_claim(employee_id: str, claim_type: str, purpose: str, date: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT employee_id, boss_id, name
    FROM employees
    WHERE employee_id = ?
    """, (employee_id,))
    employee = cursor.fetchone()

    if not employee:
        conn.close()
        return {"error": "Employee not found"}

    seq = generate_sequence_code()

    cursor.execute("""
    INSERT INTO claims (
        sequence_code,
        employee_id,
        boss_id,
        claim_type,
        planned_purpose,
        planned_date,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        seq,
        employee["employee_id"],
        employee["boss_id"],
        claim_type,
        purpose,
        date,
        "PENDING_BOSS_APPROVAL"
    ))

    conn.commit()
    conn.close()

    create_notification(
        user_role="boss",
        user_id=employee["boss_id"],
        claim_sequence_code=seq,
        message=f"New claim request {seq} from employee {employee_id} requires your approval."
    )

    return {
        "message": "Claim request created and sent to boss for approval.",
        "sequence_code": seq,
        "status": "PENDING_BOSS_APPROVAL"
    }


@router.get("/claims/history/{employee_id}")
def get_employee_history(employee_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM claims
    WHERE employee_id = ?
    ORDER BY created_at DESC, id DESC
    """, (employee_id,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


@router.get("/claims/pending-submission/{employee_id}")
def get_pending_submission_claims(employee_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sequence_code, claim_type, planned_purpose, planned_date, status
    FROM claims
    WHERE employee_id = ? AND status = 'PENDING_SUBMISSION'
    ORDER BY created_at DESC, id DESC
    """, (employee_id,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


@router.post("/claims/submit-details")
def submit_claim_details(
    sequence_code: str,
    category: str,
    amount: float,
    date: str,
    purpose: str,
    file: UploadFile = File(...)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM claims
    WHERE sequence_code = ?
    """, (sequence_code,))
    claim = cursor.fetchone()

    if not claim:
        conn.close()
        return {"error": "Claim not found"}

    if claim["status"] != "PENDING_SUBMISSION":
        conn.close()
        return {"error": "This claim is not eligible for submission"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ocr_data = extract_receipt_data(file_path)
    rules = get_policy_rules()

    expense = {
        "claimed_amount": amount,
        "claimed_date": date,
        "business_purpose": purpose,
        "category": category,
        "detected_amount": ocr_data.get("detected_amount"),
        "receipt_date": ocr_data.get("receipt_date")
    }

    result = evaluate_expense(expense, rules)

    cursor.execute("""
    UPDATE claims
    SET actual_amount = ?,
        actual_date = ?,
        actual_purpose = ?,
        receipt_path = ?,
        ocr_amount = ?,
        ocr_date = ?,
        status = ?,
        system_reason = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE sequence_code = ?
    """, (
        amount,
        date,
        purpose,
        file_path,
        ocr_data.get("detected_amount"),
        ocr_data.get("receipt_date"),
        result["status"],
        result["reason"],
        sequence_code
    ))

    conn.commit()
    conn.close()

    if result["status"] == "FLAGGED":
        create_notification(
            user_role="auditor",
            user_id="ALL_AUDITORS",
            claim_sequence_code=sequence_code,
            message=f"Flagged claim {sequence_code} requires auditor review."
        )

    create_notification(
        user_role="employee",
        user_id=claim["employee_id"],
        claim_sequence_code=sequence_code,
        message=f"Your submitted claim {sequence_code} has been marked as {result['status']}."
    )

    return {
        "sequence_code": sequence_code,
        "status": result["status"],
        "reason": result["reason"],
        "ocr_data": ocr_data
    }