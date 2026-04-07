from fastapi import APIRouter
from app.database import get_connection
from app.services.notification import create_notification

router = APIRouter()


@router.get("/auditor/flagged")
def get_flagged_claims():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM claims
    WHERE status = 'FLAGGED'
    ORDER BY updated_at DESC, id DESC
    """)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


@router.post("/auditor/decision")
def auditor_decision(sequence_code: str, decision: str, reason: str):
    decision = decision.upper().strip()

    if decision not in ["APPROVED", "DECLINED", "RESUBMIT"]:
        return {"error": "Decision must be APPROVED, DECLINED, or RESUBMIT"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sequence_code, employee_id, status
    FROM claims
    WHERE sequence_code = ?
    """, (sequence_code,))
    claim = cursor.fetchone()

    if not claim:
        conn.close()
        return {"error": "Claim not found"}

    if claim["status"] != "FLAGGED":
        conn.close()
        return {"error": "Only flagged claims can be reviewed by an auditor"}

    new_status = "PENDING_SUBMISSION" if decision == "RESUBMIT" else decision

    cursor.execute("""
    UPDATE claims
    SET status = ?,
        auditor_reason = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE sequence_code = ?
    """, (new_status, reason, sequence_code))

    conn.commit()
    conn.close()

    if decision == "RESUBMIT":
        create_notification(
            user_role="employee",
            user_id=claim["employee_id"],
            claim_sequence_code=sequence_code,
            message=f"Your flagged claim {sequence_code} requires resubmission. Please correct the amount/details and submit again. Auditor note: {reason}"
        )
    else:
        create_notification(
            user_role="employee",
            user_id=claim["employee_id"],
            claim_sequence_code=sequence_code,
            message=f"Your flagged claim {sequence_code} has been {decision} by the auditor. Auditor note: {reason}"
        )

    return {
        "message": "Auditor decision recorded successfully.",
        "sequence_code": sequence_code,
        "new_status": new_status
    }