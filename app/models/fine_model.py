from ..extensions import db
from datetime import datetime


class Fine(db.Model):
    __tablename__ = "fines"

    id = db.Column(db.Integer, primary_key=True)

    # ✅ FIXED foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    amount = db.Column(db.Float, default=0.0, nullable=False)
    days_late = db.Column(db.Integer, default=0)

    is_paid = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ✅ prevent duplicate fine per user per book
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='unique_user_book'),
    )

    def __repr__(self):
        return f"<Fine user={self.user_id} book={self.book_id} amount={self.amount}>"