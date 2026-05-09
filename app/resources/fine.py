from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..utils.decorators import role_required
from ..extensions import db

from ..models.book_model import Book
from ..models.fine_model import Fine
from ..models.user_model import User


# -------------------------------------------------------------
# INIT
# -------------------------------------------------------------
api = Namespace("fine", description="fine routes", security="Bearer")


# -------------------------------------------------------------
# MODELS
# -------------------------------------------------------------
fine_model = api.model("Fine", {
    "book_id": fields.Integer(required=True),
    "amount": fields.Float(required=True),
    "days_late": fields.Integer(required=False)
})

bulk_fine_model = api.model("BulkFine", {
    "books": fields.List(fields.Nested(fine_model), required=True)
})

fine_update_model = api.model("FineUpdate", {
    "user_id": fields.Integer(required=True),
    "book_id": fields.Integer(required=True),
    "amount": fields.Float(required=True)
})


# -------------------------------------------------------------
# ADMIN: ALL FINES
# -------------------------------------------------------------
@api.route("/all")
class AllFines(Resource):

    @jwt_required()
    @role_required(["admin"])
    def get(self):

        fines = Fine.query.all()

        result = []
        total = 0

        for fine in fines:
            total += fine.amount

            result.append({
                "user_id": fine.user_id,
                "book_id": fine.book_id,
                "amount": fine.amount,
                "days_late": fine.days_late,
                "is_paid": fine.is_paid
            })

        return {
            "total_fines": total,
            "count": len(result),
            "fines": result
        }, 200
    



# -------------------------------------------------------------
# USER: TOTAL FINES
# -------------------------------------------------------------



@api.route("/my-total")
class MyTotalFine(Resource):

    @jwt_required()
    def get(self):

        user_id = int(get_jwt_identity())

        fines = Fine.query.filter_by(user_id=user_id).all()

        total = sum(f.amount for f in fines)

        return {
            "user_id": user_id,
            "total_fine": total,
            "books_count": len(fines)
        }, 200


# -------------------------------------------------------------
# USER: MY FINES
# -------------------------------------------------------------
@api.route('/my-fines')
class MyFines(Resource):

    @jwt_required()
    def get(self):

        user_id = int(get_jwt_identity())

        fines = Fine.query.filter_by(user_id=user_id).all()
        total = sum(f.amount for f in fines)

        return {
            "fines": [
                {
                    "book_id": f.book_id,
                    "amount": f.amount,
                    "days_late": f.days_late,
                    "is_paid": f.is_paid
                } for f in fines
            ],
            "total": total
        }, 200


# -------------------------------------------------------------
# UPDATE SINGLE FINE
# -------------------------------------------------------------
@api.route('/update')
class UpdateFine(Resource):

    @jwt_required()
    @role_required(["admin"])
    @api.expect(fine_update_model)
    def put(self):

        data = request.get_json(silent=True) or {}

        user_id = data.get("user_id")
        book_id = data.get("book_id")

        if not user_id or not book_id:
            return {"msg": "user_id and book_id are required"}, 400

        fine = Fine.query.filter_by(
            user_id=user_id,
            book_id=book_id
        ).first()

        if not fine:
            return {"msg": "Fine not found"}, 404

        fine.amount = data.get("amount", fine.amount)

        db.session.commit()

        return {"msg": "Fine updated"}, 200


# -------------------------------------------------------------
# ADMIN: ADD / UPDATE MULTIPLE FINES
# -------------------------------------------------------------
@api.route('/<int:user_id>')
class AddMultipleFines(Resource):

    @jwt_required()
    @role_required(["admin"])
    @api.expect(bulk_fine_model, validate=True)
    def post(self, user_id):

        # ✅ check user exists
        user = User.query.get(user_id)
        if not user:
            return {"msg": "User not found"}, 404

        data = request.get_json(silent=True) or {}
        books = data.get("books", [])

        if not isinstance(books, list) or not books:
            return {"msg": "books must be a non-empty list"}, 400

        added = []
        updated = []
        invalid = []

        try:
            for item in books:

                book_id = item.get("book_id")
                amount = item.get("amount")

                # ✅ validation
                if not book_id or amount is None:
                    invalid.append(item)
                    continue

                # ✅ check book exists
                book = Book.query.get(book_id)
                if not book:
                    invalid.append({
                        "book_id": book_id,
                        "reason": "Book not found"
                    })
                    continue

                # ✅ find existing fine
                fine = Fine.query.filter_by(
                    user_id=user_id,
                    book_id=book_id
                ).first()

                if fine:
                    # UPDATE
                    fine.amount = amount
                    fine.days_late = item.get("days_late", fine.days_late)

                    updated.append({
                        "book_id": book_id,
                        "amount": amount
                    })
                else:
                    # CREATE
                    new_fine = Fine(
                        user_id=user_id,
                        book_id=book_id,
                        amount=amount,
                        days_late=item.get("days_late", 0)
                    )

                    db.session.add(new_fine)

                    added.append({
                        "book_id": book_id,
                        "amount": amount
                    })

            db.session.commit()

            return {
                "msg": "Process completed",
                "added": added,
                "updated": updated,
                "invalid": invalid,
                "total_added": len(added),
                "total_updated": len(updated)
            }, 200

        except Exception as e:
            db.session.rollback()
            return {
                "msg": "DB error",
                "error": str(e)
            }, 500

