from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from schemas import Course_ItemSchema, Course_ItemUpdateSchema, CourseItemOwnerSchema
from models.course_item import CourseItemModel
from models.specialization import SpecializationModel
from db import db, user_course_item_ownership, users
from resources.user import require_role


blp = Blueprint("Course_Items", __name__, description="Operations on course_items")


def _ensure_professor_owns(course_item):
    claims = get_jwt()
    if claims.get("role") != "professor":
        return

    owner_id = user_course_item_ownership.get(course_item.course_item_id)
    current_user = get_jwt_identity()
    if owner_id != current_user:
        abort(403, message="You can only modify course items you created.")


@blp.route("/course_item/<string:course_item_id>")
class Course_Item(MethodView):
    @blp.response(200, Course_ItemSchema)
    @jwt_required()
    def get(self, course_item_id):
        course_item = CourseItemModel.query.filter_by(course_item_id=course_item_id).first()
        if not course_item:
            abort(404, message="Course_Item not found.")
        return course_item

    @blp.response(200)
    @jwt_required()
    def delete(self, course_item_id):
        require_role("admin", "professor")
        course_item = CourseItemModel.query.filter_by(course_item_id=course_item_id).first()
        if not course_item:
            abort(404, message="Course_Item not found.")
        _ensure_professor_owns(course_item)
        db.session.delete(course_item)
        db.session.commit()
        user_course_item_ownership.pop(course_item.course_item_id, None)
        return {"message": "Course_item deleted."}

    @blp.arguments(Course_ItemUpdateSchema)
    @blp.response(200, Course_ItemSchema)
    @jwt_required()
    def put(self, course_item_data, course_item_id):
        require_role("admin", "professor")
        course_item = CourseItemModel.query.filter_by(course_item_id=course_item_id).first()
        if not course_item:
            abort(404, message="Course_Item not found.")
        _ensure_professor_owns(course_item)

        for key, value in course_item_data.items():
            setattr(course_item, key, value)

        db.session.commit()
        return course_item


@blp.route("/course_item/<string:course_item_id>/owner")
class CourseItemOwnership(MethodView):
    @jwt_required()
    @blp.arguments(CourseItemOwnerSchema)
    @blp.response(200)
    def put(self, owner_data, course_item_id):
        require_role("admin")
        course_item = CourseItemModel.query.filter_by(course_item_id=course_item_id).first()
        if not course_item:
            abort(404, message="Course_Item not found.")

        owner_user_id = owner_data["owner_user_id"]
        owner_user = users.get(owner_user_id)
        if not owner_user or owner_user.get("role") != "professor":
            abort(400, message="Owner must be an existing professor user.")

        user_course_item_ownership[course_item.course_item_id] = owner_user_id
        return {
            "message": "Owner assigned successfully.",
            "course_item_id": course_item_id,
            "owner_user_id": owner_user_id,
        }


@blp.route("/course_item")
class ItemList(MethodView):
    @blp.response(200, Course_ItemSchema(many=True))
    @jwt_required()
    def get(self):
        return CourseItemModel.query.all()

    @blp.arguments(Course_ItemSchema)
    @blp.response(201, Course_ItemSchema)
    @jwt_required()
    def post(self, course_item_data):
        require_role("admin", "professor")
        owner_user_id = course_item_data.pop("owner_user_id", None)
        if owner_user_id:
            claims_role = get_jwt().get("role")
            if claims_role != "admin":
                abort(403, message="Only admins can assign ownership to other users.")
            owner_user = users.get(owner_user_id)
            if not owner_user or owner_user.get("role") != "professor":
                abort(400, message="Owner must be an existing professor user.")
        spec_uuid = course_item_data.get("specialization_id")
        spec = SpecializationModel.query.filter_by(specialization_id=spec_uuid).first()
        if not spec:
            abort(400, message="Specialization not found.")

        existing = CourseItemModel.query.filter_by(
            name=course_item_data.get("name"),
            specialization_id=spec.id,
        ).first()
        if existing:
            abort(400, message="Course_Item already exists for this specialization.")

        course_item_data["specialization_id"] = spec.id

        course_item = CourseItemModel(**course_item_data)
        db.session.add(course_item)
        db.session.commit()
        if owner_user_id:
            user_course_item_ownership[course_item.course_item_id] = owner_user_id
        elif get_jwt().get("role") == "professor":
            user_course_item_ownership[course_item.course_item_id] = get_jwt_identity()
        return course_item
