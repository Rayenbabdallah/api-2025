import uuid
from db import db

class CourseItemModel(db.Model):
    __tablename__ = "course_items" 

    id = db.Column(db.Integer, primary_key=True)
    course_item_id = db.Column(db.String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(50))
    specialization_id = db.Column(db.Integer, db.ForeignKey("specializations.id"), nullable=False)

    specialization = db.relationship(
        "SpecializationModel",
        back_populates="course_items",
    )

    def to_dict(self):
        return {"name": self.name, "type": self.type}
