from datetime import date

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from models import db
from models.student import Student
from models.course import Course
from models.attendance import Attendance


attendance_bp = Blueprint(
    "attendance",
    __name__
)


# =========================================================
# LOGIN CHECK
# =========================================================

def login_required():

    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    return None


# =========================================================
# ATTENDANCE RECORDS
# =========================================================

@attendance_bp.route("/")
def attendance_records():

    auth_check = login_required()

    if auth_check:
        return auth_check


    selected_date = request.args.get(
        "date",
        ""
    ).strip()


    selected_course = request.args.get(
        "course_id",
        ""
    ).strip()


    query = Attendance.query.join(
        Student
    ).join(
        Course
    )


    # -----------------------------------------------------
    # DATE FILTER
    # -----------------------------------------------------

    if selected_date:

        try:

            selected_date_obj = date.fromisoformat(
                selected_date
            )

            query = query.filter(
                Attendance.date == selected_date_obj
            )

        except ValueError:

            selected_date = ""


    # -----------------------------------------------------
    # COURSE FILTER
    # -----------------------------------------------------

    if selected_course:

        try:

            query = query.filter(
                Student.course_id == int(selected_course)
            )

        except ValueError:

            selected_course = ""


    records = query.order_by(
        Attendance.date.desc(),
        Attendance.marked_at.desc()
    ).all()


    courses = Course.query.order_by(
        Course.name.asc()
    ).all()


    return render_template(
        "attendance/records.html",
        records=records,
        courses=courses,
        selected_date=selected_date,
        selected_course=selected_course
    )


# =========================================================
# MARK ATTENDANCE
# =========================================================

@attendance_bp.route(
    "/mark",
    methods=["GET", "POST"]
)
def mark_attendance():

    auth_check = login_required()

    if auth_check:
        return auth_check


    courses = Course.query.order_by(
        Course.name.asc()
    ).all()


    # =====================================================
    # DISPLAY ATTENDANCE FORM
    # =====================================================

    if request.method == "GET":

        selected_course = request.args.get(
            "course_id",
            ""
        ).strip()


        selected_date = request.args.get(
            "date",
            date.today().isoformat()
        ).strip()


        students = []


        if selected_course:

            try:

                students = Student.query.filter_by(
                    course_id=int(selected_course)
                ).order_by(
                    Student.first_name.asc(),
                    Student.last_name.asc()
                ).all()

            except ValueError:

                selected_course = ""


        return render_template(
            "attendance/mark.html",

            courses=courses,

            students=students,

            selected_course=selected_course,

            selected_date=selected_date
        )


    # =====================================================
    # SAVE ATTENDANCE
    # =====================================================

    selected_course = request.form.get(
        "course_id",
        ""
    ).strip()


    attendance_date = request.form.get(
        "date",
        ""
    ).strip()


    if not selected_course:

        flash(
            "Please select a course.",
            "danger"
        )

        return redirect(
            url_for(
                "attendance.mark_attendance"
            )
        )


    if not attendance_date:

        flash(
            "Please select an attendance date.",
            "danger"
        )

        return redirect(
            url_for(
                "attendance.mark_attendance",
                course_id=selected_course
            )
        )


    try:

        course_id = int(
            selected_course
        )

        attendance_date_obj = date.fromisoformat(
            attendance_date
        )

    except ValueError:

        flash(
            "Invalid course or date.",
            "danger"
        )

        return redirect(
            url_for(
                "attendance.mark_attendance"
            )
        )


    students = Student.query.filter_by(
        course_id=course_id
    ).order_by(
        Student.first_name.asc(),
        Student.last_name.asc()
    ).all()


    if not students:

        flash(
            "There are no students registered in this course.",
            "danger"
        )

        return redirect(
            url_for(
                "attendance.mark_attendance",
                course_id=course_id,
                date=attendance_date
            )
        )


    records_saved = 0


    for student in students:

        status = request.form.get(
            f"status_{student.id}",
            "Absent"
        )


        if status not in [
            "Present",
            "Absent"
        ]:

            status = "Absent"


        existing_record = Attendance.query.filter_by(
            student_id=student.id,
            date=attendance_date_obj
        ).first()


        if existing_record:

            existing_record.status = status

        else:

            attendance = Attendance(

                student_id=student.id,

                date=attendance_date_obj,

                status=status

            )

            db.session.add(
                attendance
            )


        records_saved += 1


    db.session.commit()


    flash(
        f"Attendance saved successfully for {records_saved} students.",
        "success"
    )


    return redirect(
        url_for(
            "attendance.attendance_records",

            date=attendance_date,

            course_id=course_id
        )
    )


# =========================================================
# ATTENDANCE REPORTS
# =========================================================

@attendance_bp.route("/reports")
def attendance_reports():

    auth_check = login_required()
    today = date.today()

    if auth_check:
        return auth_check


    selected_course = request.args.get(
        "course_id",
        ""
    ).strip()


    # -----------------------------------------------------
    # GET ALL COURSES
    # -----------------------------------------------------

    courses = Course.query.order_by(
        Course.name.asc()
    ).all()


    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    students_query = Student.query


    if selected_course:

        try:

            course_id = int(
                selected_course
            )

            students_query = students_query.filter_by(
                course_id=course_id
            )

        except ValueError:

            selected_course = ""


    students = students_query.order_by(
        Student.first_name.asc(),
        Student.last_name.asc()
    ).all()


    # -----------------------------------------------------
    # BUILD REPORT
    # -----------------------------------------------------

    reports = []


    for student in students:

        total_classes = Attendance.query.filter_by(
            student_id=student.id
        ).count()


        present_classes = Attendance.query.filter_by(
            student_id=student.id,
            status="Present"
        ).count()


        absent_classes = Attendance.query.filter_by(
            student_id=student.id,
            status="Absent"
        ).count()


        # -------------------------------------------------
        # CALCULATE PERCENTAGE
        # -------------------------------------------------

        if total_classes > 0:

            percentage = round(
                (
                    present_classes
                    / total_classes
                ) * 100,
                1
            )

        else:

            percentage = 0


        reports.append({

            "student": student,

            "total_classes": total_classes,

            "present_classes": present_classes,

            "absent_classes": absent_classes,

            "percentage": percentage

        })


    # -----------------------------------------------------
    # REPORT SUMMARY
    # -----------------------------------------------------

    total_students = len(reports)


    total_classes = sum(
        report["total_classes"]
        for report in reports
    )


    total_present = sum(
        report["present_classes"]
        for report in reports
    )


    total_absent = sum(
        report["absent_classes"]
        for report in reports
    )


    if total_classes > 0:

        overall_percentage = round(
            (
                total_present
                / total_classes
            ) * 100,
            1
        )

    else:

        overall_percentage = 0


    # -----------------------------------------------------
    # DISPLAY REPORT
    # -----------------------------------------------------

    return render_template(

        "attendance/reports.html",

        reports=reports,

        courses=courses,

        selected_course=selected_course,

        total_students=total_students,

        total_classes=total_classes,

        total_present=total_present,

        total_absent=total_absent,

        overall_percentage=overall_percentage

    )