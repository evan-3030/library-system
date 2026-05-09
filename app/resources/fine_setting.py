from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from ..models.fine_setting_model import FineSetting
from ..extensions import db
from ..utils.decorators import admin_required

api = Namespace("fine-setting", description="Fine settings")

fine_model = api.model("FineSetting", {
    "fine_per_day": fields.Float(required=True)
})


@api.route("/")
class FineSettingResource(Resource):

    @jwt_required()
    @admin_required
    def get(self):
        setting = FineSetting.query.first()
        return {
            "fine_per_day": setting.fine_per_day
        }, 200

    @jwt_required()
    @admin_required
    @api.expect(fine_model, validate=True)
    def put(self):
        data = api.payload

        setting = FineSetting.query.first()

        if not setting:
            setting = FineSetting()

        setting.fine_per_day = data["fine_per_day"]

        db.session.add(setting)
        db.session.commit()

        return {
            "msg": "Fine updated",
            "fine_per_day": setting.fine_per_day
        }, 200