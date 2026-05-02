from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps

def role_required(allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role")

            if role not in allowed_roles:
                return {"msg": "Access forbidden"}, 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper


# ✅ ADD THIS (missing part causing your error)
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()

        if claims.get("role") != "admin":
            return {"msg": "Admins only"}, 403

        return fn(*args, **kwargs)
    return wrapper