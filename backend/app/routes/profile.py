from fastapi import APIRouter
from app.database import get_connection

router = APIRouter()


@router.get("/profile/employee/{employee_id}")
def get_employee_profile(employee_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT employee_id, name, email, boss_id
    FROM employees
    WHERE employee_id = ?
    """, (employee_id,))
    employee = cursor.fetchone()

    if not employee:
        conn.close()
        return {"error": "Employee not found"}

    cursor.execute("""
    SELECT *
    FROM claims
    WHERE employee_id = ?
    ORDER BY created_at DESC, id DESC
    """, (employee_id,))
    claims = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
    SELECT *
    FROM notifications
    WHERE user_role = 'employee' AND user_id = ?
    ORDER BY created_at DESC, id DESC
    """, (employee_id,))
    notifications = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "employee": dict(employee),
        "claims": claims,
        "notifications": notifications
    }


@router.get("/notifications/{role}/{user_id}")
def get_notifications(role: str, user_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM notifications
    WHERE user_role = ? AND user_id = ?
    ORDER BY created_at DESC, id DESC
    """, (role, user_id))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows