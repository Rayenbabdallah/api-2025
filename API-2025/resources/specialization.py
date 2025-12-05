import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from schemas import Specialization_Schema, PlainSpecialization_Schema
from models.specialization import SpecializationModel


blp = Blueprint("specializations", __name__, description="Operations on specializations")



@blp.route("/specialization/<string:specialization_id>")
class Specialization(MethodView):
    @blp.response(200, Specialization_Schema)
    def get(self, specialization_id):
        specialization = SpecializationModel.query.filter_by(specialization_id=specialization_id).first()
        if not specialization:
            abort(404, message="Specialization not found.")
        return specialization

    @blp.response(200)
    def delete(self, specialization_id):
        specialization = SpecializationModel.query.filter_by(specialization_id=specialization_id).first()
        if not specialization:
            abort(404, message="Specialization not found.")
        db.session.delete(specialization)
        db.session.commit()
        return {"message": "Specialization deleted."}

    @blp.arguments(PlainSpecialization_Schema)
    @blp.response(200, Specialization_Schema)
    def put(self, specialization_data, specialization_id):
        specialization = SpecializationModel.query.filter_by(specialization_id=specialization_id).first()
        if not specialization:
            abort(404, message="Specialization not found.")

        for key, value in specialization_data.items():
            setattr(specialization, key, value)

        db.session.commit()
        return specialization


@blp.route("/specialization")
class SpecializationList(MethodView):
    @blp.response(200, Specialization_Schema(many=True))
    def get(self):
        return SpecializationModel.query.all()


    @blp.arguments(Specialization_Schema)
    @blp.response(201, Specialization_Schema)
    def post(self, specialization_data):
        # Prevent duplicate specialization names (unique constraint)
        existing = SpecializationModel.query.filter_by(name=specialization_data.get("name")).first()
        if existing:
            abort(400, message="Specialization already exists.")

        specialization = SpecializationModel(**specialization_data)
        db.session.add(specialization)
        db.session.commit()
        return specialization