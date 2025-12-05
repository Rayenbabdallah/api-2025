import uuid
from db import db


class SpecializationModel(db.Model):
    __tablename__ = "specializations"

    id = db.Column(db.Integer, primary_key=True)
    specialization_id = db.Column(db.String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(80), unique=True, nullable=False)

    course_items = db.relationship(
        "CourseItemModel",
        back_populates="specialization",
        cascade="all, delete-orphan"
    )
