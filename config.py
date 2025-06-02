from dotenv import load_dotenv
import os

load_dotenv()  # Tải biến môi trường từ .env

class Config:
    # Cấu hình khóa bí mật
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    # Cấu hình session
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"

    # Cấu hình cơ sở dữ liệu
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DATABASE_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "Social_Network")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        if DB_PASS  # Kiểm tra DB_PASS để tránh lỗi nếu None
        else None
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cấu hình email
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER_NAME"),
        os.getenv("MAIL_DEFAULT_SENDER_EMAIL")
    )
