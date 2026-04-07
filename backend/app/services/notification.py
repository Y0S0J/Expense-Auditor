from app.database import get_connection


def create_notification(user_role: str, user_id: str, message: str, claim_sequence_code: str = None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO notifications (user_role, user_id, claim_sequence_code, message)
    VALUES (?, ?, ?, ?)
    """, (user_role, user_id, claim_sequence_code, message))

    conn.commit()
    conn.close()