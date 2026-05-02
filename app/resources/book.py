from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..utils.decorators import admin_required, role_required  # ✅ FIXED
from ..extensions import db
from ..models.book_model import Book

api = Namespace(
    "books",
    description="Book routes for user and admin",
    security="Bearer"   # ✅ ADD THIS
)
# -------------------------------------------------------------
# 📌 Swagger Model
# -------------------------------------------------------------
book_model = api.model("Book", {
    "title": fields.String(required=True),
    "description": fields.String(required=True),
    "price": fields.Float(required=True),
    "author": fields.String(required=True),
    "is_reserve": fields.Boolean(default=False)
})

# -------------------------------------------------------------
# 📌 1) TEST ROUTES (ROLE BASED)
# -------------------------------------------------------------

@api.route('/test-user')
class TestUser(Resource):
    @role_required(["user", "admin"])  # ✅ both can access
    def get(self):
        return {"msg": "Hello User or Admin"}


@api.route('/test-admin')
class TestAdmin(Resource):
    @role_required(["admin"])  # ✅ only admin
    def get(self):
        return {"msg": "Hello Admin only"}


# -------------------------------------------------------------
# 📌 2) USER ROUTES
# -------------------------------------------------------------

@api.route("/user/list")
class UserBookList(Resource):
    @jwt_required()
    def get(self):
        books = Book.query.all()
        return [
            {
                "id": b.id,
                "title": b.title,
                "description": b.description,
                "price": b.price,
                "author": b.author,
                "is_reserve": b.is_reserve,
            }
            for b in books
        ], 200


@api.route("/user/<int:id>")
class UserBookDetail(Resource):
    @jwt_required()
    def get(self, id):
        book = Book.query.get_or_404(id)
        return {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "price": book.price,
            "author": book.author,
            "is_reserve": book.is_reserve,
        }, 200


# -------------------------------------------------------------
# 📌 3) ADMIN ROUTES
# -------------------------------------------------------------

@api.route("/admin/")
class AdminBookCreate(Resource):
    @admin_required  # ✅ no need for jwt_required again
    @api.expect(book_model)
    def post(self):
        data = api.payload or {}
        book = Book(**data)

        db.session.add(book)
        db.session.commit()

        return {"msg": "book created", "id": book.id}, 201


@api.route("/admin/<int:id>")
class AdminBookActions(Resource):
    @admin_required
    @api.expect(book_model)
    def put(self, id):
        book = Book.query.get_or_404(id)

        for k, v in (api.payload or {}).items():
            setattr(book, k, v)

        db.session.commit()
        return {"msg": "book updated", "id": book.id}, 200

    @admin_required
    def delete(self, id):
        book = Book.query.get_or_404(id)

        db.session.delete(book)
        db.session.commit()

        return {"msg": "book removed"}, 200