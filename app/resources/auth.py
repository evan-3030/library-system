from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from ..extensions import db
from ..models.user import User   # ✅ fixed import path

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

    @api.expect(register_model, validate=True)
    def post(self):
        data = api.payload or {}

        # Validate role strictly
        if data["role"] not in ["user", "admin"]:
            return {"msg": "Invalid role"}, 400

        # Check duplicate username
        if User.query.filter_by(username=data['username']).first():
            return {"msg": "Username already exists"}, 409

        try:
            user = User(
                username=data['username'],
                role=data['role']
            )
            user.set_password(data['password'])

            db.session.add(user)
            db.session.commit()

            return {
                "msg": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"msg": "Error registering user", "error": str(e)}, 500


# -----------------------------
# 📌 Login
# -----------------------------
@api.route('/login')
class Login(Resource):

    @api.expect(login_model, validate=True)
    def post(self):
        data = api.payload or {}

        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return {"msg": "Invalid credentials"}, 401

        # Create tokens
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
# 📌 Refresh Token
# -----------------------------
@api.route('/refresh')
class Refresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()

        user = User.query.get(user_id)
        if not user:
            return {"msg": "User not found"}, 404

        new_access_token = create_access_token(
            identity=str(user_id),
            additional_claims={"role": user.role}
        )

        return {
            "access_token": new_access_token
        }, 200