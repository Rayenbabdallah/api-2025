import uuid

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import generate_password_hash, check_password_hash

from db import users
from schemas import RegisterSchema, LoginSchema, RoleUpdateSchema


blp = Blueprint("Users", __name__, description="User authentication and authorization")


def _find_user_by_username(username):
    return next((user for user in users.values() if user["username"] == username), None)


def require_role(*roles):
    """Ensures the caller's JWT role claim matches one of the allowed roles."""
    claims = get_jwt()
    role = claims.get("role")
    if role not in roles:
        abort(403, message="You do not have permission to perform this action.")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(RegisterSchema)
    @blp.response(201)
    def post(self, user_data):
        if _find_user_by_username(user_data["username"]):
            abort(400, message="Username already exists.")

        user_id = uuid.uuid4().hex
        users[user_id] = {
            "id": user_id,
            "username": user_data["username"],
            "password": generate_password_hash(user_data["password"]),
            "role": "student",
            "protected": False,
        }
        return {"message": "User registered successfully.", "user_id": user_id, "role": "student"}


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(LoginSchema)
    @blp.response(200)
    def post(self, credentials):
        user = _find_user_by_username(credentials["username"])
        if not user or not check_password_hash(user["password"], credentials["password"]):
            abort(401, message="Invalid credentials.")

        claims = {"role": user["role"]}
        access_token = create_access_token(identity=user["id"], additional_claims=claims)
        refresh_token = create_refresh_token(identity=user["id"], additional_claims=claims)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "role": user["role"],
        }


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200)
    def post(self):
        identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")
        access_token = create_access_token(identity=identity, additional_claims={"role": role})
        return {"access_token": access_token}


@blp.route("/user/<string:user_id>/role")
class UserRole(MethodView):
    @jwt_required()
    @blp.arguments(RoleUpdateSchema)
    @blp.response(200)
    def put(self, role_data, user_id):
        require_role("admin")
        user = users.get(user_id)
        if not user:
            abort(404, message="User not found.")

        user["role"] = role_data["role"]
        return {"message": "Role updated successfully.", "user_id": user_id, "role": user["role"]}
