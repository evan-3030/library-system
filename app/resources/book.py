from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import admin_required, role_required
from ..extensions import db
from ..models.book_model import Book

api = Namespace("books", description="Book routes", security="Bearer")

# -------------------------------------------------------------
# 📌 Swagger Model (NO is_reserve here!)
# -------------------------------------------------------------
book_model = api.model("Book", {
    "title": fields.String(required=True),
    "description": fields.String(required=True),
    "price": fields.Float(required=True),
    "author": fields.String(required=True),
})

# -------------------------------------------------------------
# 📌 Serialize
# -------------------------------------------------------------
def serialize_book(book):
    return {
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "price": book.price,
        "author": book.author,
        "is_reserve": book.is_reserve,
        "reserved_by": book.reserved_by
    }

# -------------------------------------------------------------
# 📌 USER ROUTES
# -------------------------------------------------------------
@api.route("/list")
class UserBookList(Resource):
    @jwt_required()
    def get(self):
        books = Book.query.all()
        return [serialize_book(b) for b in books], 200


@api.route("/detail/<int:id>")
class UserBookDetail(Resource):
    @jwt_required()
    def get(self, id):
        book = Book.query.get_or_404(id)
        return serialize_book(book), 200


# -------------------------------------------------------------
# 📌 ADMIN ROUTES
# -------------------------------------------------------------
@api.route("/")
class AdminBookCreate(Resource):

    @jwt_required()
    @role_required(["admin"])
    @api.expect(book_model, validate=True)
    def post(self):
        data = api.payload or {}

        book = Book(
            title=data["title"],
            description=data["description"],
            price=data["price"],
            author=data["author"],
            is_reserve=False,   # ✅ ALWAYS default
            reserved_by=None    # ✅ ALWAYS None
        )

        db.session.add(book)
        db.session.commit()

        return {"msg": "Book created", "id": book.id}, 201


@api.route("/admin/<int:id>")
class AdminBookActions(Resource):

    @jwt_required()
    @admin_required
    @api.expect(book_model, validate=True)
    def put(self, id):
        book = Book.query.get_or_404(id)
        data = api.payload or {}

        for field in ["title", "description", "price", "author"]:
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


# -------------------------------------------------------------
# 📌 RESERVE BOOK
# -------------------------------------------------------------
@api.route('/reserve/<int:id>')
class BookReserve(Resource):

    @jwt_required()
    @role_required(["user", "admin"])
    def put(self, id):
        user_id = int(get_jwt_identity())
        book = Book.query.get_or_404(id)

        # Already reserved
        if book.is_reserve is True:
            return {"msg": "Book not available"}, 400

        try:
            book.is_reserve = True
            book.reserved_by = user_id

            db.session.commit()

            return {
                "msg": "Book reserved successfully",
                "book_id": book.id
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"msg": "Error reserving book", "error": str(e)}, 500


# -------------------------------------------------------------
# 📌 RETURN BOOK
# -------------------------------------------------------------
@api.route('/return/<int:id>')
class BookReturn(Resource):

    @jwt_required()
    @role_required(["user", "admin"])
    def put(self, id):
        user_id = int(get_jwt_identity())
        role = get_jwt().get("role", "user")

        book = Book.query.get_or_404(id)

        # Not reserved
        if book.is_reserve is False:
            return {"msg": "Book is not reserved"}, 400

        if book.reserved_by is None:
            return {"msg": "Invalid state"}, 500

        # Authorization
        if role != "admin" and book.reserved_by != user_id:
            return {"msg": "Not allowed"}, 403

        try:
            book.is_reserve = False
            book.reserved_by = None

            db.session.commit()

            return {
                "msg": "Book returned successfully",
                "book_id": book.id
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"msg": "Error returning book", "error": str(e)}, 500