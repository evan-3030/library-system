from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from ..utils.decorators import admin_required, role_required
from ..extensions import db

from ..models.book_model import Book
from ..models.fine_model import Fine
from ..models.fine_setting_model import FineSetting

from datetime import datetime, timedelta


api = Namespace("books", description="Book routes", security="Bearer")


# -------------------------------------------------------------
# Swagger Models
# -------------------------------------------------------------
book_model = api.model("Book", {
    "title": fields.String(required=True),
    "description": fields.String(required=True),
    "price": fields.Float(required=True),
    "author": fields.String(required=True)
})


# -------------------------------------------------------------
# Serialize
# -------------------------------------------------------------
def serialize_book(book):
    return {
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "price": book.price,
        "author": book.author,
        "is_reserved": book.is_reserved,
        "user_id": book.user_id
    }


# -------------------------------------------------------------
# USER ROUTES
# -------------------------------------------------------------
@api.route("/list")
class UserBookList(Resource):

    @jwt_required()
    def get(self):
        books = Book.query.all()
        return [serialize_book(book) for book in books], 200


@api.route("/detail/<int:id>")
class UserBookDetail(Resource):

    @jwt_required()
    def get(self, id):
        book = Book.query.get_or_404(id)
        return serialize_book(book), 200


# -------------------------------------------------------------
# ADMIN ROUTES
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
            is_reserved=False,
            user_id=None
        )

        try:
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"msg": "DB error", "error": str(e)}, 500

        return {"msg": "Book created", "book_id": book.id}, 201


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

        return {"msg": "Book updated", "book_id": book.id}, 200

    @jwt_required()
    @admin_required
    def delete(self, id):

        book = Book.query.get_or_404(id)

        db.session.delete(book)
        db.session.commit()

        return {"msg": "Book removed"}, 200


# -------------------------------------------------------------
# RESERVE BOOK
# -------------------------------------------------------------
@api.route('/reserve/<int:id>')
class BookReserve(Resource):

    @jwt_required()
    @role_required(["user", "admin"])
    def put(self, id):

        user_id = int(get_jwt_identity())
        book = Book.query.get_or_404(id)

        if book.is_reserved:
            return {"msg": "Book not available"}, 400

        try:
            now = datetime.utcnow()

            book.is_reserved = True
            book.user_id = user_id
            book.borrowed_at = now
            book.due_date = now - timedelta(days=7)
            book.returned_at = None

            db.session.commit()

            return {
                "msg": "Book reserved successfully",
                "book_id": book.id,
                "due_date": book.due_date.isoformat()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"msg": "Error reserving book", "error": str(e)}, 500


# -------------------------------------------------------------
# RETURN BOOK
# -------------------------------------------------------------
@api.route('/return/<int:id>')
class BookReturn(Resource):

    @jwt_required()
    @role_required(["user", "admin"])
    def put(self, id):

        user_id = int(get_jwt_identity())
        role = get_jwt().get("role", "user")

        book = Book.query.get_or_404(id)

        if not book.is_reserved:
            return {"msg": "Book is not reserved"}, 400

        if role != "admin" and book.user_id != user_id:
            return {"msg": "Not allowed"}, 403

        try:
            now = datetime.utcnow()
            borrower_id = book.user_id

            # ✅ Fine calculation
            if book.due_date and now > book.due_date:

                days_late = max((now - book.due_date).days, 0)

                if days_late > 0:

                    setting = FineSetting.query.first()
                    fine_per_day = setting.fine_per_day if setting else 2

                    amount = days_late * fine_per_day

                    existing_fine = Fine.query.filter_by(
                        user_id=borrower_id,
                        book_id=book.id
                    ).first()

                    if existing_fine:
                        existing_fine.amount += amount
                        existing_fine.days_late += days_late
                    else:
                        fine = Fine(
                            user_id=borrower_id,
                            book_id=book.id,
                            amount=amount,
                            days_late=days_late
                        )
                        db.session.add(fine)

            # ✅ Reset book
            book.is_reserved = False
            book.user_id = None
            book.borrowed_at = None
            book.due_date = None
            book.returned_at = now

            db.session.commit()

            return {"msg": "Book returned successfully"}, 200

        except Exception as e:
            db.session.rollback()
            return {"msg": "Error returning book", "error": str(e)}, 500