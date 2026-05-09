from app import create_app
from app.extensions import db
from app.models.fine_setting_model import FineSetting   # ✅ ADD THIS

app = create_app()

with app.app_context():

    # ✅ Ensure default fine setting exists
    setting = FineSetting.query.first()

    if not setting:
        setting = FineSetting(fine_per_day=2)
        db.session.add(setting)
        db.session.commit()   # ✅ ONLY COMMIT (NO create_all here)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)