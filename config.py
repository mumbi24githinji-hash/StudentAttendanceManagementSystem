import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = "student-attendance-management-secret-key"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "database", "attendance.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False