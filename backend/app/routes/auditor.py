from fastapi import APIRouter
from app.database import get_connection

router = APIRouter()


@router.get("/auditor/flagged")
def get_flagged():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM claims WHERE status='Flagged'")
    rows = cursor.fetchall()

    conn.close()
    return rows


@router.post("/auditor/decision")
def auditor_decision(sequence_code: str, decision: str, reason: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE claims
    SET status=?, auditor_reason=?
    WHERE sequence_code=?
    """, (decision, reason, sequence_code))

    conn.commit()
    conn.close()

    return {"message": "Decision recorded"}