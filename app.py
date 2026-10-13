from flask import Flask, request, jsonify, session, redirect, send_from_directory
import sqlite3
import os
from datetime import date

# ============================================================
# STUDENT ATTENDANCE MANAGEMENT SYSTEM
# Flask + SQLite Backend
# ============================================================

app = Flask(__name__)

# Flask session secret key
app.secret_key = "student_attendance_system_secret_key_2026"

# ============================================================
# DATABASE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "attendance.db")


def get_db():
    """Create and return a SQLite database connection."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database():
    """Create all required database tables."""

    connection = get_db()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # STUDENTS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            year TEXT NOT NULL,
            gender TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # ATTENDANCE TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL
                CHECK(status IN ('Present', 'Absent')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(student_id)
            REFERENCES students(id)
            ON DELETE CASCADE,

            UNIQUE(student_id, attendance_date)
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def student_to_dict(student):
    """Convert a student database row into JSON data."""

    return {
        "id": student["id"],
        "regNo": student["reg_no"],
        "name": student["name"],
        "course": student["course"],
        "year": student["year"],
        "gender": student["gender"]
    }


def attendance_to_dict(record):
    """Convert an attendance database row into JSON data."""

    return {
        "id": record["id"],
        "studentId": record["student_id"],
        "regNo": record["reg_no"],
        "studentName": record["name"],
        "date": record["attendance_date"],
        "status": record["status"]
    }


def is_logged_in():
    """Check whether the administrator is logged in."""

    return session.get("logged_in", False)


# ============================================================
# LOGIN
# ============================================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    # Default administrator account
    if username == "admin" and password == "admin123":

        session["logged_in"] = True
        session["username"] = username

        return jsonify({
            "success": True,
            "message": "Login successful."
        })

    return jsonify({
        "success": False,
        "message": "Invalid username or password."
    }), 401


# ============================================================
# LOGOUT
# ============================================================

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })


# ============================================================
# CHECK LOGIN SESSION
# ============================================================

@app.route("/api/session", methods=["GET"])
def check_session():

    return jsonify({
        "logged_in": is_logged_in(),
        "username": session.get("username", "")
    })


# ============================================================
# PAGE ROUTES
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        BASE_DIR,
        "index.html"
    )


@app.route("/index.html")
def index_page():

    return send_from_directory(
        BASE_DIR,
        "index.html"
    )


@app.route("/login.html")
def login_page():

    return send_from_directory(
        BASE_DIR,
        "login.html"
    )


@app.route("/dashboard.html")
def dashboard_page():

    if not is_logged_in():
        return redirect("/login.html")

    return send_from_directory(
        BASE_DIR,
        "dashboard.html"
    )


@app.route("/students.html")
def students_page():

    if not is_logged_in():
        return redirect("/login.html")

    return send_from_directory(
        BASE_DIR,
        "students.html"
    )


@app.route("/attendance.html")
def attendance_page():

    if not is_logged_in():
        return redirect("/login.html")

    return send_from_directory(
        BASE_DIR,
        "attendance.html"
    )


@app.route("/reports.html")
def reports_page():

    if not is_logged_in():
        return redirect("/login.html")

    return send_from_directory(
        BASE_DIR,
        "reports.html"
    )


# ============================================================
# CSS
# ============================================================

@app.route("/style.css")
def style_css():

    return send_from_directory(
        BASE_DIR,
        "style.css"
    )


# ============================================================
# JAVASCRIPT
# ============================================================

@app.route("/script.js")
def script_js():

    return send_from_directory(
        BASE_DIR,
        "script.js"
    )


# ============================================================
# IMAGES
# ============================================================

@app.route("/images/<path:filename>")
def images(filename):

    images_folder = os.path.join(
        BASE_DIR,
        "images"
    )

    return send_from_directory(
        images_folder,
        filename
    )


# ============================================================
# GET STUDENTS
# ============================================================

@app.route("/api/students", methods=["GET"])
def get_students():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    search = request.args.get(
        "search",
        ""
    ).strip()

    connection = get_db()

    if search:

        search_value = f"%{search}%"

        students = connection.execute("""
            SELECT *
            FROM students
            WHERE reg_no LIKE ?
               OR name LIKE ?
               OR course LIKE ?
            ORDER BY name ASC
        """, (
            search_value,
            search_value,
            search_value
        )).fetchall()

    else:

        students = connection.execute("""
            SELECT *
            FROM students
            ORDER BY name ASC
        """).fetchall()

    connection.close()

    return jsonify({
        "success": True,
        "students": [
            student_to_dict(student)
            for student in students
        ]
    })


# ============================================================
# ADD STUDENT
# ============================================================

@app.route("/api/students", methods=["POST"])
def add_student():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json(silent=True) or {}

    reg_no = str(data.get("regNo", "")).strip()
    name = str(data.get("name", "")).strip()
    course = str(data.get("course", "")).strip()
    year = str(data.get("year", "")).strip()
    gender = str(data.get("gender", "")).strip()

    # Validate input
    if not reg_no:
        return jsonify({
            "success": False,
            "message": "Registration number is required."
        }), 400

    if not name:
        return jsonify({
            "success": False,
            "message": "Student name is required."
        }), 400

    if not course:
        return jsonify({
            "success": False,
            "message": "Course is required."
        }), 400

    if not year:
        return jsonify({
            "success": False,
            "message": "Year is required."
        }), 400

    if not gender:
        return jsonify({
            "success": False,
            "message": "Gender is required."
        }), 400

    connection = get_db()

    try:

        cursor = connection.execute("""
            INSERT INTO students
            (
                reg_no,
                name,
                course,
                year,
                gender
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            reg_no,
            name,
            course,
            year,
            gender
        ))

        student_id = cursor.lastrowid

        connection.commit()

        student = connection.execute("""
            SELECT *
            FROM students
            WHERE id = ?
        """, (student_id,)).fetchone()

        connection.close()

        return jsonify({
            "success": True,
            "message": "Student added successfully.",
            "student": student_to_dict(student)
        }), 201

    except sqlite3.IntegrityError:

        connection.rollback()
        connection.close()

        return jsonify({
            "success": False,
            "message": "A student with this registration number already exists."
        }), 409

    except Exception as error:

        connection.rollback()
        connection.close()

        return jsonify({
            "success": False,
            "message": f"Unable to add student: {error}"
        }), 500
        
        # ============================================================
# UPDATE STUDENT
# ============================================================

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):

    if not session.get("logged_in"):
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json(silent=True) or {}

    reg_no = data.get("regNo", "").strip()
    name = data.get("name", "").strip()
    course = data.get("course", "").strip()
    year = data.get("year", "").strip()
    gender = data.get("gender", "").strip()

    if not all([
        reg_no,
        name,
        course,
        year,
        gender
    ]):
        return jsonify({
            "success": False,
            "message": "Please fill in all student fields."
        }), 400

    conn = get_db()

    try:

        student = conn.execute("""
            SELECT *
            FROM students
            WHERE id = ?
        """, (student_id,)).fetchone()

        if not student:

            conn.close()

            return jsonify({
                "success": False,
                "message": "Student not found."
            }), 404

        # Check whether another student already
        # uses this registration number.
        existing = conn.execute("""
            SELECT id
            FROM students
            WHERE reg_no = ?
            AND id != ?
        """, (
            reg_no,
            student_id
        )).fetchone()

        if existing:

            conn.close()

            return jsonify({
                "success": False,
                "message":
                    "Another student already uses this registration number."
            }), 409

        conn.execute("""
            UPDATE students
            SET
                reg_no = ?,
                name = ?,
                course = ?,
                year = ?,
                gender = ?
            WHERE id = ?
        """, (
            reg_no,
            name,
            course,
            year,
            gender,
            student_id
        ))

        conn.commit()

        updated_student = conn.execute("""
            SELECT *
            FROM students
            WHERE id = ?
        """, (student_id,)).fetchone()

        conn.close()

        return jsonify({
            "success": True,
            "message": "Student updated successfully.",
            "student":
                student_to_dict(updated_student)
        })

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "success": False,
            "message":
                "Registration number already exists."
        }), 409

    except Exception as error:

        conn.rollback()
        conn.close()

        return jsonify({
            "success": False,
            "message":
                f"Unable to update student: {error}"
        }), 500


# ============================================================
# DELETE STUDENT
# ============================================================

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = get_db()

    student = connection.execute("""
        SELECT *
        FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    if student is None:

        connection.close()

        return jsonify({
            "success": False,
            "message": "Student not found."
        }), 404

    connection.execute("""
        DELETE FROM students
        WHERE id = ?
    """, (student_id,))

    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Student deleted successfully."
    })


# ============================================================
# GET ATTENDANCE
# ============================================================

@app.route("/api/attendance", methods=["GET"])
def get_attendance():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    selected_date = request.args.get(
        "date",
        date.today().isoformat()
    ).strip()

    connection = get_db()

    records = connection.execute("""
        SELECT
            attendance.id,
            attendance.student_id,
            attendance.attendance_date,
            attendance.status,
            students.reg_no,
            students.name
        FROM attendance
        INNER JOIN students
            ON attendance.student_id = students.id
        WHERE attendance.attendance_date = ?
        ORDER BY students.name ASC
    """, (selected_date,)).fetchall()

    connection.close()

    return jsonify({
        "success": True,
        "records": [
            attendance_to_dict(record)
            for record in records
        ]
    })


# ============================================================
# SAVE ATTENDANCE
# ============================================================

@app.route("/api/attendance", methods=["POST"])
def save_attendance():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json(silent=True) or {}

    attendance_date = str(
        data.get("date", "")
    ).strip()

    records = data.get(
        "records",
        []
    )

    if not attendance_date:

        return jsonify({
            "success": False,
            "message": "Attendance date is required."
        }), 400

    if not isinstance(records, list) or len(records) == 0:

        return jsonify({
            "success": False,
            "message": "No attendance records were provided."
        }), 400

    connection = get_db()

    saved_count = 0

    try:

        for record in records:

            if not isinstance(record, dict):
                continue

            student_id = record.get(
                "studentId"
            )

            status = record.get(
                "status"
            )

            if not student_id:
                continue

            if status not in [
                "Present",
                "Absent"
            ]:
                continue

            connection.execute("""
                INSERT INTO attendance
                (
                    student_id,
                    attendance_date,
                    status
                )
                VALUES (?, ?, ?)

                ON CONFLICT(
                    student_id,
                    attendance_date
                )
                DO UPDATE SET
                    status = excluded.status
            """, (
                student_id,
                attendance_date,
                status
            ))

            saved_count += 1

        connection.commit()
        connection.close()

        return jsonify({
            "success": True,
            "message":
                f"{saved_count} attendance record(s) saved successfully."
        })

    except Exception as error:

        connection.rollback()
        connection.close()

        return jsonify({
            "success": False,
            "message":
                f"Unable to save attendance: {error}"
        }), 500


# ============================================================
# DASHBOARD DATA
# ============================================================

@app.route("/api/dashboard", methods=["GET"])
def dashboard_data():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    today = date.today().isoformat()

    connection = get_db()

    # Total number of students
    total_students = connection.execute("""
        SELECT COUNT(*)
        FROM students
    """).fetchone()[0]

    # Present today
    present = connection.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
        AND status = 'Present'
    """, (today,)).fetchone()[0]

    # Absent today
    absent = connection.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
        AND status = 'Absent'
    """, (today,)).fetchone()[0]

    # Total attendance records for today
    total_today = present + absent

    # Attendance percentage
    if total_today > 0:

        attendance_rate = round(
            (present / total_today) * 100
        )

    else:

        attendance_rate = 0

    # Recent attendance
    recent = connection.execute("""
        SELECT
            attendance.id,
            attendance.student_id,
            attendance.attendance_date,
            attendance.status,
            students.reg_no,
            students.name
        FROM attendance
        INNER JOIN students
            ON attendance.student_id = students.id
        ORDER BY
            attendance.attendance_date DESC,
            attendance.id DESC
        LIMIT 10
    """).fetchall()

    connection.close()

    return jsonify({

        "success": True,

        "totalStudents": total_students,

        "present": present,

        "absent": absent,

        "attendanceRate": attendance_rate,

        "recentAttendance": [
            attendance_to_dict(record)
            for record in recent
        ]

    })


# ============================================================
# REPORTS
# ============================================================

@app.route("/api/reports", methods=["GET"])
def reports():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = get_db()

    students = connection.execute("""
        SELECT *
        FROM students
        ORDER BY name ASC
    """).fetchall()

    report_data = []

    total_records = 0
    total_present = 0

    for student in students:

        # Total attendance records
        total = connection.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE student_id = ?
        """, (
            student["id"],
        )).fetchone()[0]

        # Present records
        present = connection.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE student_id = ?
            AND status = 'Present'
        """, (
            student["id"],
        )).fetchone()[0]

        # Absent records
        absent = connection.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE student_id = ?
            AND status = 'Absent'
        """, (
            student["id"],
        )).fetchone()[0]

        # Percentage
        if total > 0:

            percentage = round(
                (present / total) * 100
            )

        else:

            percentage = 0

        # Performance classification
        if percentage >= 75:

            performance = "Excellent"

        elif percentage >= 50:

            performance = "Average"

        else:

            performance = "Poor"

        total_records += total
        total_present += present

        report_data.append({

            "id": student["id"],

            "regNo": student["reg_no"],

            "name": student["name"],

            "course": student["course"],

            "year": student["year"],

            "gender": student["gender"],

            "total": total,

            "present": present,

            "absent": absent,

            "percentage": percentage,

            "performance": performance

        })

    # Overall attendance percentage
    if total_records > 0:

        overall_rate = round(
            (total_present / total_records) * 100
        )

    else:

        overall_rate = 0

    connection.close()

    return jsonify({

        "success": True,

        "totalStudents": len(students),

        "totalRecords": total_records,

        "overallRate": overall_rate,

        "reports": report_data

    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "message": "Student Attendance Management System is running.",
        "database": DATABASE
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({
        "success": False,
        "message": "The requested page or API endpoint was not found."
    }), 404


@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "success": False,
        "message": "An internal server error occurred."
    }), 500


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_database()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print(" STUDENT ATTENDANCE MANAGEMENT SYSTEM")
    print("=" * 60)
    print()
    print(" Backend  : Flask")
    print(" Database : SQLite")
    print()
    print(" Browser:")
    print(" http://127.0.0.1:5000")
    print()
    print(" Username : admin")
    print(" Password : admin123")
    print()
    print(" Press CTRL+C to stop the server.")
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )