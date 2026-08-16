"""
Application configuration.

All values are read from environment variables (see .env.example).
Never hardcode secrets or credentials here.
"""

import os
from dataclasses import dataclass, field


def _env_list(key: str, default: str = "http://localhost:5173") -> list[str]:
    raw = os.environ.get(key, default)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass
class BaseConfig:
    ENV: str = os.environ.get("FLASK_ENV", "development")
    DEBUG: bool = False
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    MYSQL_HOST: str = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_USER: str = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.environ.get("MYSQL_DATABASE", "xai_loan_db")

    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        f"mysql+pymysql://{os.environ.get('MYSQL_USER', 'root')}:"
        f"{os.environ.get('MYSQL_PASSWORD', '')}@"
        f"{os.environ.get('MYSQL_HOST', 'localhost')}:"
        f"{os.environ.get('MYSQL_PORT', '3306')}/"
        f"{os.environ.get('MYSQL_DATABASE', 'xai_loan_db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    MODEL_PATH: str = os.environ.get("MODEL_PATH", "../ml/models/saved/model.joblib")

    CORS_ORIGINS: list[str] = field(default_factory=lambda: _env_list("CORS_ORIGINS"))


@dataclass
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True


@dataclass
class TestingConfig(BaseConfig):
    DEBUG: bool = True
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"


@dataclass
class ProductionConfig(BaseConfig):
    DEBUG: bool = False


_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None):
    name = name or os.environ.get("FLASK_ENV", "development")
    return _CONFIGS.get(name, DevelopmentConfig)()
