import sqlite3

DB_NAME = "expense_auditor.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bosses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boss_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        password TEXT NOT NULL,
        boss_id TEXT NOT NULL,
        FOREIGN KEY (boss_id) REFERENCES bosses(boss_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auditor_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sequence_code TEXT UNIQUE NOT NULL,
        employee_id TEXT NOT NULL,
        boss_id TEXT NOT NULL,

        claim_type TEXT NOT NULL,
        planned_purpose TEXT NOT NULL,
        planned_date TEXT NOT NULL,

        actual_amount REAL,
        actual_date TEXT,
        actual_purpose TEXT,
        receipt_path TEXT,

        ocr_amount REAL,
        ocr_date TEXT,

        status TEXT NOT NULL,
        system_reason TEXT,
        boss_reason TEXT,
        auditor_reason TEXT,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY (boss_id) REFERENCES bosses(boss_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_role TEXT NOT NULL,
        user_id TEXT NOT NULL,
        claim_sequence_code TEXT,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO bosses (boss_id, name, email, password)
    VALUES ('B001', 'Mary Manager', 'mary.manager@company.com', 'boss123')
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO employees (employee_id, name, email, password, boss_id)
    VALUES ('E001', 'John Employee', 'john.employee@company.com', 'emp123', 'B001')
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO auditors (auditor_id, name, email, password)
    VALUES ('A001', 'Alice Auditor', 'alice.auditor@company.com', 'audit123')
    """)

    conn.commit()
    conn.close()