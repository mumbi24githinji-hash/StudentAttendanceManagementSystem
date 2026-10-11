from datetime import datetime
from . import db


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    code = db.Column(db.String(50), unique=True, nullable=False)

    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    students = db.relationship(
        "Student",
        back_populates="course",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Course {self.code}>"