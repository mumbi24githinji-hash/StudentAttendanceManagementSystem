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


students_bp = Blueprint(
    "students",
    __name__
)


def login_required():

    if not session.get("logged_in"):

        return redirect(
            url_for("auth.login")
        )

    return None


@students_bp.route("/")
def list_students():

    auth_check = login_required()

    if auth_check:
        return auth_check

    search = request.args.get(
        "search",
        ""
    ).strip()


    if search:

        students = Student.query.filter(
            db.or_(
                Student.registration_number.ilike(
                    f"%{search}%"
                ),

                Student.first_name.ilike(
                    f"%{search}%"
                ),

                Student.last_name.ilike(
                    f"%{search}%"
                ),

                Student.email.ilike(
                    f"%{search}%"
                )
            )
        ).order_by(
            Student.created_at.desc()
        ).all()

    else:

        students = Student.query.order_by(
            Student.created_at.desc()
        ).all()


    return render_template(
        "students/list.html",
        students=students,
        search=search
    )


@students_bp.route(
    "/add",
    methods=["GET", "POST"]
)
def add_student():

    auth_check = login_required()

    if auth_check:
        return auth_check


    # Get all courses automatically
    courses = Course.query.order_by(
        Course.name.asc()
    ).all()


    if request.method == "POST":

        registration_number = request.form.get(
            "registration_number",
            ""
        ).strip()

        first_name = request.form.get(
            "first_name",
            ""
        ).strip()

        last_name = request.form.get(
            "last_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        year = request.form.get(
            "year",
            ""
        ).strip()

        course_id = request.form.get(
            "course_id",
            ""
        ).strip()


        # Validate required fields

        if not registration_number:

            flash(
                "Registration number is required.",
                "danger"
            )

            return render_template(
                "students/add.html",
                courses=courses
            )


        if not first_name:

            flash(
                "First name is required.",
                "danger"
            )

            return render_template(
                "students/add.html",
                courses=courses
            )


        if not last_name:

            flash(
                "Last name is required.",
                "danger"
            )

            return render_template(
                "students/add.html",
                courses=courses
            )


        if not course_id:

            flash(
                "Please select a course.",
                "danger"
            )

            return render_template(
                "students/add.html",
                courses=courses
            )


        # Check registration number

        existing_student = Student.query.filter_by(
            registration_number=registration_number
        ).first()


        if existing_student:

            flash(
                "A student with this registration number already exists.",
                "danger"
            )

            return render_template(
                "students/add.html",
                courses=courses
            )


        # Check email

        if email:

            existing_email = Student.query.filter_by(
                email=email
            ).first()


            if existing_email:

                flash(
                    "A student with this email already exists.",
                    "danger"
                )

                return render_template(
                    "students/add.html",
                    courses=courses
                )


        # Check selected course

        course = Course.query.get(
            int(course_id)
        )


        if not course:

            flash(
                "The selected course does not exist.",
                "danger"
            )

            return render_template(
                "students/add.html",
                courses=courses
            )


        # Create student

        student = Student(

            registration_number=registration_number,

            first_name=first_name,

            last_name=last_name,

            email=email if email else None,

            gender=gender if gender else None,

            year=int(year) if year else None,

            course_id=course.id
        )


        db.session.add(student)

        db.session.commit()


        flash(
            f"{first_name} {last_name} was added successfully.",
            "success"
        )


        return redirect(
            url_for(
                "students.list_students"
            )
        )


    return render_template(
        "students/add.html",
        courses=courses
    )


@students_bp.route(
    "/edit/<int:student_id>",
    methods=["GET", "POST"]
)
def edit_student(student_id):

    auth_check = login_required()

    if auth_check:
        return auth_check


    student = Student.query.get_or_404(
        student_id
    )


    courses = Course.query.order_by(
        Course.name.asc()
    ).all()


    if request.method == "POST":

        registration_number = request.form.get(
            "registration_number",
            ""
        ).strip()

        first_name = request.form.get(
            "first_name",
            ""
        ).strip()

        last_name = request.form.get(
            "last_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        year = request.form.get(
            "year",
            ""
        ).strip()

        course_id = request.form.get(
            "course_id",
            ""
        ).strip()


        if not registration_number or not first_name or not last_name:

            flash(
                "Registration number, first name and last name are required.",
                "danger"
            )

            return render_template(
                "students/edit.html",
                student=student,
                courses=courses
            )


        duplicate_registration = Student.query.filter(
            Student.registration_number == registration_number,
            Student.id != student.id
        ).first()


        if duplicate_registration:

            flash(
                "Another student already uses this registration number.",
                "danger"
            )

            return render_template(
                "students/edit.html",
                student=student,
                courses=courses
            )


        if email:

            duplicate_email = Student.query.filter(
                Student.email == email,
                Student.id != student.id
            ).first()


            if duplicate_email:

                flash(
                    "Another student already uses this email.",
                    "danger"
                )

                return render_template(
                    "students/edit.html",
                    student=student,
                    courses=courses
                )


        course = Course.query.get(
            int(course_id)
        )


        if not course:

            flash(
                "Please select a valid course.",
                "danger"
            )

            return render_template(
                "students/edit.html",
                student=student,
                courses=courses
            )


        student.registration_number = registration_number

        student.first_name = first_name

        student.last_name = last_name

        student.email = email if email else None

        student.gender = gender if gender else None

        student.year = int(year) if year else None

        student.course_id = course.id


        db.session.commit()


        flash(
            "Student information updated successfully.",
            "success"
        )


        return redirect(
            url_for(
                "students.list_students"
            )
        )


    return render_template(
        "students/edit.html",
        student=student,
        courses=courses
    )


@students_bp.route(
    "/delete/<int:student_id>",
    methods=["POST"]
)
def delete_student(student_id):

    auth_check = login_required()

    if auth_check:
        return auth_check


    student = Student.query.get_or_404(
        student_id
    )


    name = (
        f"{student.first_name} "
        f"{student.last_name}"
    )


    db.session.delete(student)

    db.session.commit()


    flash(
        f"{name} was deleted successfully.",
        "success"
    )


    return redirect(
        url_for(
            "students.list_students"
        )
    )