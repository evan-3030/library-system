from ..extensions import db

class FineSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fine_per_day = db.Column(db.Float, default=2.0)