from datetime import datetime
from . import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    registration_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    first_name = db.Column(
        db.String(100),
        nullable=False
    )

    last_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=True
    )

    gender = db.Column(
        db.String(20),
        nullable=True
    )

    year = db.Column(
        db.Integer,
        nullable=True
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    course = db.relationship(
        "Course",
        back_populates="students"
    )

    attendance_records = db.relationship(
        "Attendance",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student {self.registration_number}>"