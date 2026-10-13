import sqlite3
from pathlib import Path

# Create a database folder inside the project
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "attendance.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            year TEXT NOT NULL
        )
    """)

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    # Create default login account
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password)
        VALUES (?, ?)
    """, ("admin", "admin123"))

    conn.commit()
    conn.close()


def add_student(reg_no, name, course, year):
    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO students (reg_no, name, course, year)
            VALUES (?, ?, ?, ?)
        """, (reg_no, name, course, year))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_students():
    conn = get_connection()

    students = conn.execute("""
        SELECT * FROM students
        ORDER BY name ASC
    """).fetchall()

    conn.close()

    return students


def get_student(student_id):
    conn = get_connection()

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()

    return student


def delete_student(student_id):
    conn = get_connection()

    conn.execute("""
        DELETE FROM attendance
        WHERE student_id = ?
    """, (student_id,))

    conn.execute("""
        DELETE FROM students
        WHERE id = ?
    """, (student_id,))

    conn.commit()
    conn.close()


def record_attendance(student_id, date, status):
    conn = get_connection()

    # Check whether attendance already exists
    existing = conn.execute("""
        SELECT id FROM attendance
        WHERE student_id = ? AND date = ?
    """, (student_id, date)).fetchone()

    if existing:
        conn.execute("""
            UPDATE attendance
            SET status = ?
            WHERE student_id = ? AND date = ?
        """, (status, student_id, date))
    else:
        conn.execute("""
            INSERT INTO attendance (student_id, date, status)
            VALUES (?, ?, ?)
        """, (student_id, date, status))

    conn.commit()
    conn.close()


def get_attendance():
    conn = get_connection()

    records = conn.execute("""
        SELECT
            attendance.id,
            attendance.date,
            attendance.status,
            students.reg_no,
            students.name,
            students.course
        FROM attendance
        INNER JOIN students
        ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    """).fetchall()

    conn.close()

    return records


def get_student_attendance(student_id):
    conn = get_connection()

    records = conn.execute("""
        SELECT *
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student_id,)).fetchall()

    conn.close()

    return records


def get_attendance_percentage(student_id):
    conn = get_connection()

    total = conn.execute("""
        SELECT COUNT(*) AS count
        FROM attendance
        WHERE student_id = ?
    """, (student_id,)).fetchone()["count"]

    present = conn.execute("""
        SELECT COUNT(*) AS count
        FROM attendance
        WHERE student_id = ?
        AND status = 'Present'
    """, (student_id,)).fetchone()["count"]

    conn.close()

    if total == 0:
        return 0

    return round((present / total) * 100, 2)


def check_login(username, password):
    conn = get_connection()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE username = ?
        AND password = ?
    """, (username, password)).fetchone()

    conn.close()

    return user is not None