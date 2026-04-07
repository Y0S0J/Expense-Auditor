from datetime import datetime
from app.database import get_connection


def generate_sequence_code():
    today = datetime.now().strftime("%Y%m%d")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) as total FROM claims WHERE sequence_code LIKE ?",
        (f"CLM-{today}-%",)
    )
    count = cursor.fetchone()["total"] + 1
    conn.close()

    return f"CLM-{today}-{count:04d}"