from datetime import datetime
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    # ✅ NEW FIELDS
    crime = db.Column(db.Integer, default=0)  # default 0

    created_at = db.Column(
        db.DateTime,
        default=datetime   # auto set on create
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime,
        onupdate=datetime # auto update on change
    )

    # password helpers
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)