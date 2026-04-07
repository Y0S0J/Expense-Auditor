import sqlite3

DB_NAME = "expense_auditor.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Employees
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE,
        name TEXT,
        password TEXT
    )
    """)

    # Auditors
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Claims
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sequence_code TEXT UNIQUE,
        employee_id TEXT,
        claim_type TEXT,
        planned_purpose TEXT,
        planned_date TEXT,

        actual_amount REAL,
        actual_date TEXT,
        actual_purpose TEXT,
        receipt_path TEXT,

        ocr_amount REAL,
        ocr_date TEXT,

        status TEXT,
        system_reason TEXT,
        auditor_reason TEXT
    )
    """)

    # Notifications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Add test employee
    cursor.execute("""
    INSERT OR IGNORE INTO employees (employee_id, name, password)
    VALUES ('E001', 'John', '1234')
    """)

    # Add test auditor
    cursor.execute("""
    INSERT OR IGNORE INTO auditors (username, password)
    VALUES ('admin', 'admin')
    """)

    conn.commit()
    conn.close()