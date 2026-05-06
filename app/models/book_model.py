from ..extensions import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    author = db.Column(db.String(120))
    price = db.Column(db.Float)
    is_reserve = db.Column(db.Boolean, default=False)
    reserved_by = db.Column(db.Integer, nullable=True)  
