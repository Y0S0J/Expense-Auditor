from fastapi import APIRouter
from app.database import get_connection
from app.services.notification import create_notification

router = APIRouter()


@router.get("/boss/pending/{boss_id}")
def get_boss_pending_claims(boss_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sequence_code, employee_id, claim_type, planned_purpose, planned_date, status
    FROM claims
    WHERE boss_id = ? AND status = 'PENDING_BOSS_APPROVAL'
    ORDER BY created_at DESC, id DESC
    """, (boss_id,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


@router.post("/boss/decision")
def boss_decision(sequence_code: str, decision: str, reason: str = ""):
    decision = decision.upper().strip()

    if decision not in ["APPROVE", "DECLINE"]:
        return {"error": "Decision must be APPROVE or DECLINE"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sequence_code, employee_id, boss_id, status
    FROM claims
    WHERE sequence_code = ?
    """, (sequence_code,))
    claim = cursor.fetchone()

    if not claim:
        conn.close()
        return {"error": "Claim not found"}

    if claim["status"] != "PENDING_BOSS_APPROVAL":
        conn.close()
        return {"error": "This claim is not pending boss approval"}

    new_status = "PENDING_SUBMISSION" if decision == "APPROVE" else "DECLINED_BY_BOSS"

    cursor.execute("""
    UPDATE claims
    SET status = ?,
        boss_reason = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE sequence_code = ?
    """, (new_status, reason, sequence_code))

    conn.commit()
    conn.close()

    if new_status == "PENDING_SUBMISSION":
        create_notification(
            user_role="employee",
            user_id=claim["employee_id"],
            claim_sequence_code=sequence_code,
            message=f"Your claim request {sequence_code} was approved by your boss. You can now submit expense details after the event."
        )
    else:
        create_notification(
            user_role="employee",
            user_id=claim["employee_id"],
            claim_sequence_code=sequence_code,
            message=f"Your claim request {sequence_code} was declined by your boss."
        )

    return {
        "message": "Boss decision recorded successfully.",
        "sequence_code": sequence_code,
        "new_status": new_status
    }