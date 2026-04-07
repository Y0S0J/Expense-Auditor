from fastapi import APIRouter
from app.database import get_connection

router = APIRouter()


@router.post("/login/employee")
def login_employee(employee_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees WHERE employee_id=?", (employee_id,))
    user = cursor.fetchone()

    conn.close()

    if not user:
        return {"error": "Employee not found"}

    return {
        "message": "Login successful",
        "employee_id": employee_id
    }


@router.post("/login/auditor")
def login_auditor(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM auditors WHERE username=? AND password=?",
        (username, password)
    )
    user = cursor.fetchone()

    conn.close()

    if not user:
        return {"error": "Invalid credentials"}

    return {
        "message": "Login successful",
        "role": "auditor"
    }