from flask_restx import Namespace, Resource

api = Namespace("users", description="User routes")

@api.route("/")
class UserTest(Resource):
    def get(self):
        return {"msg": "User route working"}