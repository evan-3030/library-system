from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from ..extensions import db
from app.models.user import User
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

api = Namespace('auth', description="Authentication routes")

# -----------------------------
# 📌 Swagger Models
# -----------------------------
register_model = api.model('Register', {
    "username": fields.String(required=True),
    "password": fields.String(required=True),
    "role": fields.String(
        required=True,
        enum=["user", "admin"],
        description="user role"
    )
})

login_model = api.model('Login', {
    "username": fields.String(required=True),
    "password": fields.String(required=True)
})

# -----------------------------
# 📌 Register
# -----------------------------
@api.route('/register')
class Register(Resource):
    @api.expect(register_model)
    def post(self):
        data = api.payload or {}

        # ✅ validate input
        if not data.get("username") or not data.get("password") or not data.get("role"):
            return {"msg": "Missing required fields"}, 400

        # ✅ prevent duplicate user
        if User.query.filter_by(username=data['username']).first():
            return {"msg": "Username already exists"}, 409

        # ✅ create user
        user = User(
            username=data['username'],
            role=data['role']
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # ✅ safe datetime serialization
        return {
            "msg": "registered",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "crime": user.crime,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
        }, 201


# -----------------------------
# 📌 Login
# -----------------------------
@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = api.payload or {}

        if not data.get("username") or not data.get("password"):
            return {"msg": "Missing username or password"}, 400

        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return {"msg": "invalid credentials"}, 401

        # ✅ Create tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        refresh_token = create_refresh_token(
            identity=str(user.id)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }, 200
    


# -----------------------------
# 📌 refresh
# -----------------------------



@api.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)  # ✅ ONLY refresh token allowed
    def post(self):
        user_id = get_jwt_identity()

        # (optional) you can reload user from DB
        user = User.query.get(user_id)

        new_access_token = create_access_token(
            identity=str(user_id),
            additional_claims={"role": user.role}
        )

        return {
            "access_token": new_access_token
        }, 200