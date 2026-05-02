from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from ..utils.decorators import admin_required
from ..extensions import db
from ..models.user import User

api = Namespace('users')

@api.route('/crime/<int:user_id>')
class CrimeUser(Resource):

    @jwt_required()
    @admin_required
    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        user.crime = True
        db.session.commit()
        return {"msg": "user has been punished"}
