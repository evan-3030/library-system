from flask import Flask
from .extensions import db, jwt
from .routes import api

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-1234567890123456'

    db.init_app(app)
    jwt.init_app(app)   # ✅ VERY IMPORTANT

    api.init_app(app)

    return app