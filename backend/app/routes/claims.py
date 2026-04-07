from fastapi import APIRouter
from app.database import get_connection
from app.services.sequence import generate_sequence_code

router = APIRouter()


@router.post("/claims/log")
def log_claim(employee_id: str, claim_type: str, purpose: str, date: str):
    conn = get_connection()
    cursor = conn.cursor()

    seq = generate_sequence_code()

    cursor.execute("""
    INSERT INTO claims (sequence_code, employee_id, claim_type, planned_purpose, planned_date, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (seq, employee_id, claim_type, purpose, date, "LOGGED"))

    conn.commit()
    conn.close()

    return {
        "sequence_code": seq,
        "message": "Claim logged successfully"
    }