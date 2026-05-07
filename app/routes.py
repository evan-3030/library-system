from flask_restx import Api
from .resources.auth import api as auth_ns
from .resources.book import api as book_ns
from .resources.fine import api as fine_ns
from .resources.user import api as user_ns


authorizations = {
    "Bearer": {   # ✅ FIXED NAME
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Format: Bearer <your_token>"
    }
}

api = Api(
    title="Library API",
    version="1.0",
    description="Library Management System",
    doc="/swagger",
    authorizations=authorizations,
    security="Bearer"   # ✅ MUST MATCH KEY ABOVE
)

# Namespaces
api.add_namespace(auth_ns, path="/auth")
api.add_namespace(book_ns, path="/books")
api.add_namespace(fine_ns, path="/fine")
api.add_namespace(user_ns, path="/users")