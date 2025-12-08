from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

# Simple in-memory stores used for JWT auth and course-item ownership.
DEFAULT_ADMIN_ID = "admin-id"
users = {
    DEFAULT_ADMIN_ID: {
        "id": DEFAULT_ADMIN_ID,
        "username": "admin",
        "password": generate_password_hash("admin123"),
        "role": "admin",
        "protected": True,
    }
}
user_course_item_ownership = {}
