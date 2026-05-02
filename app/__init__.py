from flask import Flask
from .extensions import db, jwt
from .config import Config
from .routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    api.init_app(app)

    with app.app_context():
        db.create_all()

    return app