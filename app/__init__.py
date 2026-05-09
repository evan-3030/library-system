from flask import Flask
from .extensions import db, jwt
from flask_restx import Api

def create_app():
    app = Flask(__name__)

    # -----------------------------
    # CONFIG
    # -----------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "super-secret-key"

    # -----------------------------
    # AUTHORIZATION (Swagger)
    # -----------------------------
    authorizations = {
        "Bearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add: Bearer <your_token>"
        }
    }

    # ✅ CREATE API (ONLY ONCE)
    api = Api(
        app,
        authorizations=authorizations,
        security="Bearer"
    )

    # -----------------------------
    # INIT EXTENSIONS
    # -----------------------------
    db.init_app(app)
    jwt.init_app(app)

    # -----------------------------
    # REGISTER NAMESPACES
    # -----------------------------
    from app.resources.auth import api as auth_ns
    from app.resources.book import api as book_ns
    from app.resources.fine import api as fine_ns

    api.add_namespace(auth_ns)
    api.add_namespace(book_ns)
    api.add_namespace(fine_ns)

    # -----------------------------
    # CREATE TABLES
    # -----------------------------
    with app.app_context():
        db.create_all()

    return app