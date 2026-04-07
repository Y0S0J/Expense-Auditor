from fastapi import APIRouter
from app.database import get_connection

router = APIRouter()


@router.post("/login/employee")
def login_employee(employee_id: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT employee_id, name, boss_id
    FROM employees
    WHERE employee_id = ? AND password = ?
    """, (employee_id, password))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"error": "Invalid employee credentials"}

    return {
        "message": "Login successful",
        "role": "employee",
        "employee_id": user["employee_id"],
        "name": user["name"],
        "boss_id": user["boss_id"]
    }


@router.post("/login/boss")
def login_boss(boss_id: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT boss_id, name
    FROM bosses
    WHERE boss_id = ? AND password = ?
    """, (boss_id, password))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"error": "Invalid boss credentials"}

    return {
        "message": "Login successful",
        "role": "boss",
        "boss_id": user["boss_id"],
        "name": user["name"]
    }


@router.post("/login/auditor")
def login_auditor(auditor_id: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT auditor_id, name
    FROM auditors
    WHERE auditor_id = ? AND password = ?
    """, (auditor_id, password))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"error": "Invalid auditor credentials"}

    return {
        "message": "Login successful",
        "role": "auditor",
        "auditor_id": user["auditor_id"],
        "name": user["name"]
    }