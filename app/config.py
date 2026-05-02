class Config:
    JWT_SECRET_KEY = "super-secret-key" 
    JWT_SECRET_KEY = "jwt-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///library.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "super-secret-key"

    # ✅ Access token expires (short)
    JWT_ACCESS_TOKEN_EXPIRES = 900   # 15 minutes

    # ✅ Refresh token expires (long)
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # 1 day