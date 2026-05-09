from ..extensions import db
from datetime import datetime


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)

    # Basic info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Availability
    is_reserved = db.Column(db.Boolean, default=False)

    # Borrowing tracking
    borrowed_at = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    returned_at = db.Column(db.DateTime, nullable=True)

    # Relation to user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Timestamps (useful, not extra 🚀)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

