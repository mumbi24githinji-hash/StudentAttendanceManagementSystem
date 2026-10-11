from flask import Blueprint, render_template, request, redirect, url_for, session, flash


auth_bp = Blueprint("auth", __name__)


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if session.get("logged_in"):
        return redirect(url_for("dashboard"))


    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["logged_in"] = True
            session["username"] = username

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")


    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))