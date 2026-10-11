from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    session
)

from datetime import date

from config import Config
from models import db


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)


    # =========================================================
    # IMPORT MODELS
    # =========================================================

    from models.student import Student
    from models.course import Course
    from models.attendance import Attendance


    # =========================================================
    # IMPORT ROUTES
    # =========================================================

    from routes.auth import auth_bp
    from routes.students import students_bp
    from routes.courses import courses_bp
    from routes.attendance import attendance_bp


    # =========================================================
    # REGISTER ROUTES
    # =========================================================

    app.register_blueprint(auth_bp)

    app.register_blueprint(
        students_bp,
        url_prefix="/students"
    )

    app.register_blueprint(
        courses_bp,
        url_prefix="/courses"
    )

    app.register_blueprint(
        attendance_bp,
        url_prefix="/attendance"
    )


    # =========================================================
    # HOME
    # =========================================================

    @app.route("/")
    def index():

        if session.get("logged_in"):
            return redirect(url_for("dashboard"))

        return redirect(url_for("auth.login"))


    # =========================================================
    # DASHBOARD
    # =========================================================

    @app.route("/dashboard")
    def dashboard():

        if not session.get("logged_in"):
            return redirect(url_for("auth.login"))


        # -----------------------------------------------------
        # TODAY'S DATE
        # -----------------------------------------------------

        today = date.today()


        # -----------------------------------------------------
        # BASIC STATISTICS
        # -----------------------------------------------------

        total_students = Student.query.count()

        total_courses = Course.query.count()


        # -----------------------------------------------------
        # TODAY'S ATTENDANCE
        # -----------------------------------------------------

        present_today = Attendance.query.filter_by(
            date=today,
            status="Present"
        ).count()


        absent_today = Attendance.query.filter_by(
            date=today,
            status="Absent"
        ).count()


        # -----------------------------------------------------
        # ATTENDANCE RATE
        # -----------------------------------------------------

        total_attendance_today = (
            present_today + absent_today
        )


        if total_attendance_today > 0:

            attendance_rate = round(
                (
                    present_today
                    / total_attendance_today
                ) * 100
            )

        else:

            attendance_rate = 0


        # -----------------------------------------------------
        # RECENT ATTENDANCE
        # -----------------------------------------------------

        recent_attendance = Attendance.query.order_by(
            Attendance.date.desc(),
            Attendance.marked_at.desc()
        ).limit(8).all()


        # -----------------------------------------------------
        # DASHBOARD PAGE
        # -----------------------------------------------------

        return render_template(
            "dashboard.html",

            username=session.get("username"),

            today=today,

            total_students=total_students,

            total_courses=total_courses,

            present_today=present_today,

            absent_today=absent_today,

            attendance_rate=attendance_rate,

            recent_attendance=recent_attendance
        )


    # =========================================================
    # CREATE DATABASE TABLES + DEFAULT COURSES
    # =========================================================

    with app.app_context():

        db.create_all()


        default_courses = [

            {
                "name": "Bachelor of Computer Science",
                "code": "BCS",
                "description": (
                    "A programme focused on computer science, "
                    "programming and software development."
                )
            },

            {
                "name": "Bachelor of Information Technology",
                "code": "BIT",
                "description": (
                    "A programme covering information technology "
                    "and information systems."
                )
            },

            {
                "name": "Diploma in Computer Science",
                "code": "DCS",
                "description": (
                    "A diploma programme covering programming, "
                    "databases and computer systems."
                )
            },

            {
                "name": "Diploma in Information Technology",
                "code": "DIT",
                "description": (
                    "A diploma programme covering information "
                    "technology and software development."
                )
            },

            {
                "name": "Software Engineering",
                "code": "SE",
                "description": (
                    "A programme focused on software engineering "
                    "and application development."
                )
            },

            {
                "name": "Cyber Security",
                "code": "CYB",
                "description": (
                    "A programme focused on cybersecurity and "
                    "information protection."
                )
            }

        ]


        # -----------------------------------------------------
        # INSERT DEFAULT COURSES IF THEY DON'T EXIST
        # -----------------------------------------------------

        for course_data in default_courses:

            existing_course = Course.query.filter_by(
                code=course_data["code"]
            ).first()


            if not existing_course:

                course = Course(

                    name=course_data["name"],

                    code=course_data["code"],

                    description=course_data["description"]

                )

                db.session.add(course)


        db.session.commit()


    return app


# =============================================================
# CREATE APPLICATION
# =============================================================

app = create_app()


# =============================================================
# RUN APPLICATION
# =============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )