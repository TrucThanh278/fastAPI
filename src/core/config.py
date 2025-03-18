import secrets
import logging
from typing import ClassVar
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_HOST: str = "http://localhost:8000"
    FORGET_PASSWORD_URL: str = "/auth/forget-password/otp"
    RESET_PASSWORD_URL: str = "/auth/reset-password"

    PROJECT_NAME: str = "FastAPI"
    DEBUG: bool = True

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB_NAME: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str

    PGADMIN_DEFAULT_EMAIL: str = "admin@gmail.com"
    PGADMIN_DEFAULT_PASSWORD: str = "admin@123"
    PGADMIN_PORT: int = 50

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5  # 5 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60 * 24 * 14  # 14 days
    SECRET_KEY: str = secrets.token_urlsafe(32)
    FORGET_PWD_SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    OTP_EXPIRE_MINUTES: int = 1
    OTP_COOLDOWN_SECONDS: int = 2

    MAIL_FROM_NAME: str = "fastApi"
    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int = 5

    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    MAIL_USERNAME: str = "trucnguyendev2708@gmail.com"
    MAIL_PASSWORD: str = "bcpb xmww fvjy zlhb"
    MAIL_FROM: str = "trucnguyendev2708@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAM: str = "trucnt@atom"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: ClassVar[Path] = Path(__file__).parent.parent / "templates"

    def SQLALCHEMY_DATABASE_URI(self):
        uri = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB_NAME}"
        return uri


settings = Settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_project")
