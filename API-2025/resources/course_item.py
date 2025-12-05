from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import Course_ItemSchema, Course_ItemUpdateSchema
from models.course_item import CourseItemModel
from models.specialization import SpecializationModel
from db import db


blp = Blueprint("Course_Items", __name__, description="Operations on course_items")


@blp.route("/course_item/<string:course_item_id>")
class Course_Item(MethodView):
    @blp.response(200, Course_ItemSchema)
    def get(self, course_item_id):
        course_item = CourseItemModel.query.filter_by(course_item_id=course_item_id).first()
        if not course_item:
            abort(404, message="Course_Item not found.")
        return course_item

    @blp.response(200)
    def delete(self, course_item_id):
        course_item = CourseItemModel.query.filter_by(course_item_id=course_item_id).first()
        if not course_item:
            abort(404, message="Course_Item not found.")
        db.session.delete(course_item)
        db.session.commit()
        return {"message": "Course_item deleted."}

    @blp.arguments(Course_ItemUpdateSchema)
    @blp.response(200, Course_ItemSchema)
    def put(self, course_item_data, course_item_id):
        course_item = CourseItemModel.query.filter_by(course_item_id=course_item_id).first()
        if not course_item:
            abort(404, message="Course_Item not found.")

        for key, value in course_item_data.items():
            setattr(course_item, key, value)

        db.session.commit()
        return course_item



@blp.route("/course_item")
class ItemList(MethodView):
    @blp.response(200, Course_ItemSchema(many=True))
    def get(self):
        return CourseItemModel.query.all()

    @blp.arguments(Course_ItemSchema)
    @blp.response(201, Course_ItemSchema)
    def post(self, course_item_data):
        # Accept specialization_id as UUID string; resolve to internal integer id
        spec_uuid = course_item_data.get("specialization_id")
        spec = SpecializationModel.query.filter_by(specialization_id=spec_uuid).first()
        if not spec:
            abort(400, message="Specialization not found.")

        # Prevent duplicate course item for the same specialization
        existing = CourseItemModel.query.filter_by(
            name=course_item_data.get("name"),
            specialization_id=spec.id,
        ).first()
        if existing:
            abort(400, message="Course_Item already exists for this specialization.")

        # Replace external specialization_id (UUID) with internal DB id
        course_item_data["specialization_id"] = spec.id

        course_item = CourseItemModel(**course_item_data)
        db.session.add(course_item)
        db.session.commit()
        return course_item
