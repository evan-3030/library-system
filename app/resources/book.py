from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..utils.decorators import admin_required, role_required
from ..extensions import db
from ..models.book_model import Book

api = Namespace(
    "books",
    description="Book routes for user and admin",
    security="Bearer"
)

# -------------------------------------------------------------
# 📌 Swagger Model
# -------------------------------------------------------------
book_model = api.model("Book", {
    "title": fields.String(required=True),
    "description": fields.String(required=True),
    "price": fields.Float(required=True),
    "author": fields.String(required=True),
    # "is_reserve": fields.Boolean(default=True, required=False)
})

# -------------------------------------------------------------
# 📌 Helper (serialize)
# -------------------------------------------------------------
def serialize_book(book):
    return {
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "price": book.price,
        "author": book.author,
        "is_reserve": book.is_reserve,
    }

# -------------------------------------------------------------
# 📌 1) TEST ROUTES (ROLE BASED)
# -------------------------------------------------------------
@api.route('/test-user')
class TestUser(Resource):
    @jwt_required()
    @role_required(["user", "admin"])
    def get(self):
        return {"msg": "Hello User or Admin"}, 200


@api.route('/test-admin')
class TestAdmin(Resource):
    @jwt_required()
    @role_required(["admin"])
    def get(self):
        return {"msg": "Hello Admin only"}, 200


# -------------------------------------------------------------
# 📌 2) USER ROUTES
# -------------------------------------------------------------
@api.route("/list")
class UserBookList(Resource):
    @jwt_required()
    def get(self):
        books = Book.query.all()
        return [serialize_book(b) for b in books], 200


@api.route("/<int:id>")
class UserBookDetail(Resource):
    @jwt_required()
    def get(self, id):
        book = Book.query.get_or_404(id)
        return serialize_book(book), 200


# -------------------------------------------------------------
# 📌 3) ADMIN ROUTES
# -------------------------------------------------------------
@api.route("/")
class AdminBookCreate(Resource):
    @jwt_required()
    @admin_required
    @api.expect(book_model, validate=True)
    def post(self):
        data = api.payload or {}

        book = Book(
            title=data.get("title"),
            description=data.get("description"),
            price=data.get("price"),
            author=data.get("author"),
            is_reserve=data.get("is_reserve",),
        )
        book.is_reserve = True

        db.session.add(book)
        db.session.commit()

        return {"msg": "Book created", "id": book.id}, 201


@api.route("/<int:id>")
class AdminBookActions(Resource):

    @jwt_required()
    @admin_required
    @api.expect(book_model, validate=True)
    def put(self, id):
        book = Book.query.get_or_404(id)
        data = api.payload or {}

        # update only allowed fields
        for field in ["title", "description", "price", "author", "is_reserve"]:
            if field in data:
                setattr(book, field, data[field])

        db.session.commit()

        return {"msg": "Book updated", "id": book.id}, 200

    @jwt_required()
    @admin_required
    def delete(self, id):
        book = Book.query.get_or_404(id)

        db.session.delete(book)
        db.session.commit()

        return {"msg": "Book removed"}, 200
    


    @api.route("/book/reserve")
    class ReserveBook(Resource):
        @admin_required
        @api.expect(api.model('ReservBook', {
            "id": fields.Integer(required=True),
            "is_reserve": fields.Boolean(required=True, description="True or False")

        }))
        def put(self):
            data = api.payload
            book = Book.query.get_or_404(data['id'])
            book.is_reserve = data['is_reserve']
            db.session.commit()
            return {"msg": f"Book {book.id} reserve status updated to {book.is_reserve}"}, 200