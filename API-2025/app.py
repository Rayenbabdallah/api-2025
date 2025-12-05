from flask import Flask
from flask_smorest import Api
from db import db
import os
import models  # Ensure models are imported for SQLAlchemy
from resources.course_item import blp as CourseItemBlueprint
from resources.specialization import blp as SpecializationBlueprint


def create_app(db_url=None):


    app = Flask(__name__)


# Flask-Smorest / Swagger configuration
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Specialization REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"                  
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui/" 
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")


# Initialize API
    # Initialize extensions with app
    db.init_app(app)
    api = Api(app)

    # Create tables immediately within the app context so callers
    # of `create_app()` (and the CLI) don't need the decorator support
    # which may not be available in some environments.
    with app.app_context():
        db.create_all()


# Register blueprints
    api.register_blueprint(CourseItemBlueprint)
    api.register_blueprint(SpecializationBlueprint)

    return app


# Minimal test route to verify container is working
#@app.route("/ping")
#def ping():
#   return {"message": "pong"}


# Run the app directly (works reliably in Docker)
#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000)
