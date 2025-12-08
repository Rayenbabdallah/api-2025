from marshmallow import Schema, fields, validate

class PlainCourse_ItemSchema(Schema):
    course_item_id=fields.Str(dump_only=True, attribute="course_item_id")
    name=fields.Str(required=True)
    type=fields.Str(required=True)
    #specialization_id=fields.Str(required=True)

class Course_ItemUpdateSchema(Schema):
    name=fields.Str(required=True)
    type=fields.Str(required=True)
   
class PlainSpecialization_Schema(Schema):
    specialization_id=fields.Str(dump_only=True, attribute="specialization_id")
    name=fields.Str(required=True)

class Course_ItemSchema(PlainCourse_ItemSchema):
    specialization_id=fields.Str(required=True,load_only=True)
    specialization=fields.Nested(lambda:PlainSpecialization_Schema(),dump_only=True)
    owner_user_id = fields.Str(load_only=True)


class CourseItemOwnerSchema(Schema):
    owner_user_id = fields.Str(required=True)

class Specialization_Schema(PlainSpecialization_Schema):
    course_items=fields.List(fields.Nested(lambda:PlainCourse_ItemSchema()),dump_only=True)


class RegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class RoleUpdateSchema(Schema):
    role = fields.Str(
        required=True,
        validate=validate.OneOf(["student", "professor", "admin"])
    )
