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
# @api.route('/my-fines')
# class MyFines(Resource):

#     @jwt_required()
#     def get(self):

#         user_id = int(get_jwt_identity())

#         fines = Fine.query.filter_by(user_id=user_id).all()
#         total = sum(f.amount for f in fines)

#         return {
#             "fines": [
#                 {
#                     "book_id": f.book_id,
#                     "amount": f.amount,
#                     "days_late": f.days_late,
#                     "is_paid": f.is_paid
#                 } for f in fines
#             ],
#             "total": total
#         }, 200

