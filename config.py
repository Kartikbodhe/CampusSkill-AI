import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "campusskill-dev-secret-key-389f41bce8a149f"
    
    # Database config with Postgres URL dialect compatibility
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url or f"sqlite:///{os.path.join(basedir, 'campusskill.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
    } if db_url and "sqlite" not in db_url else {}
    
    # File upload security configuration
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))  # 5 MB
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}

    # Security headers and cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
