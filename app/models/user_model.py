from datetime import datetime
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"   # ✅ IMPORTANT (fix your error)

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # roles: admin / user
    role = db.Column(db.String(20), nullable=False, default="user")

    # better naming than "crime"
    penalty_points = db.Column(db.Integer, default=0)

    # timestamps
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 🔗 relationship with books
    books = db.relationship("Book", backref="user", lazy=True)

    # 🔐 password helpers
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)