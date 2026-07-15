import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "celebratehub-secret-key-change-in-prod")
    JWT_SECRET = os.getenv("JWT_SECRET", "jwt-secret-change-in-prod")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = 24

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "celebratehub")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "")
    AWS_BUCKET = os.getenv("AWS_BUCKET", "celebratehub-uploads")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
