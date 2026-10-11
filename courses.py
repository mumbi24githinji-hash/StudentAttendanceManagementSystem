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
from models.course import Course


courses_bp = Blueprint("courses", __name__)


def login_required():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    return None


@courses_bp.route("/")
def list_courses():

    auth_check = login_required()

    if auth_check:
        return auth_check

    search = request.args.get("search", "").strip()

    if search:

        courses = Course.query.filter(
            db.or_(
                Course.name.ilike(f"%{search}%"),
                Course.code.ilike(f"%{search}%"),
                Course.description.ilike(f"%{search}%")
            )
        ).order_by(
            Course.name.asc()
        ).all()

    else:

        courses = Course.query.order_by(
            Course.name.asc()
        ).all()

    return render_template(
        "courses/list.html",
        courses=courses,
        search=search
    )


@courses_bp.route("/add", methods=["GET", "POST"])
def add_course():

    auth_check = login_required()

    if auth_check:
        return auth_check

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        code = request.form.get(
            "code",
            ""
        ).strip().upper()

        description = request.form.get(
            "description",
            ""
        ).strip()


        # Validate required fields

        if not name or not code:

            flash(
                "Course name and course code are required.",
                "danger"
            )

            return render_template(
                "courses/add.html"
            )


        # Check duplicate course code

        existing_course = Course.query.filter_by(
            code=code
        ).first()

        if existing_course:

            flash(
                "A course with this code already exists.",
                "danger"
            )

            return render_template(
                "courses/add.html"
            )


        # Create course

        course = Course(
            name=name,
            code=code,
            description=description if description else None
        )


        db.session.add(course)

        db.session.commit()


        flash(
            f"{name} was added successfully.",
            "success"
        )


        return redirect(
            url_for("courses.list_courses")
        )


    return render_template(
        "courses/add.html"
    )


@courses_bp.route(
    "/edit/<int:course_id>",
    methods=["GET", "POST"]
)
def edit_course(course_id):

    auth_check = login_required()

    if auth_check:
        return auth_check


    course = Course.query.get_or_404(course_id)


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        code = request.form.get(
            "code",
            ""
        ).strip().upper()

        description = request.form.get(
            "description",
            ""
        ).strip()


        if not name or not code:

            flash(
                "Course name and course code are required.",
                "danger"
            )

            return render_template(
                "courses/edit.html",
                course=course
            )


        # Check whether another course already uses the code

        duplicate_course = Course.query.filter(
            Course.code == code,
            Course.id != course.id
        ).first()


        if duplicate_course:

            flash(
                "Another course already uses this course code.",
                "danger"
            )

            return render_template(
                "courses/edit.html",
                course=course
            )


        course.name = name
        course.code = code
        course.description = (
            description
            if description
            else None
        )


        db.session.commit()


        flash(
            "Course information updated successfully.",
            "success"
        )


        return redirect(
            url_for("courses.list_courses")
        )


    return render_template(
        "courses/edit.html",
        course=course
    )


@courses_bp.route(
    "/delete/<int:course_id>",
    methods=["POST"]
)
def delete_course(course_id):

    auth_check = login_required()

    if auth_check:
        return auth_check


    course = Course.query.get_or_404(course_id)


    # Don't allow deleting a course that still has students

    if course.students:

        flash(
            "This course cannot be deleted because students are assigned to it. "
            "Move or delete the students first.",
            "danger"
        )

        return redirect(
            url_for("courses.list_courses")
        )


    course_name = course.name


    db.session.delete(course)

    db.session.commit()


    flash(
        f"{course_name} was deleted successfully.",
        "success"
    )


    return redirect(
        url_for("courses.list_courses")
    )