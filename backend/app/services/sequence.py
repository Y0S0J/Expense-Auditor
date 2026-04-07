import datetime
import sqlite3

from app.database import get_connection


def generate_sequence_code():
    now = datetime.datetime.now().strftime("%Y%m%d")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM claims WHERE sequence_code LIKE ?", (f"CLM-{now}%",))
    count = cursor.fetchone()[0] + 1

    conn.close()

    return f"CLM-{now}-{count:04d}"