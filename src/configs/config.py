import secrets
import logging
from logging.config import dictConfig
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Project settings
    PROJECT_NAME: str = "FastAPI"
    DEBUG: bool = True

    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str

    # Security settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5  # 5 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60 * 24 * 14  # 14 days
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"

    # Logging settings
    LOG_LEVEL: str = "DEBUG"  # Đọc từ `.env`
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# ✅ Cấu hình Logging **chỉ chạy một lần**
def setup_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,  # Không tắt logger gốc
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
        },
    }

    # Kiểm tra nếu logging chưa được cấu hình, thì mới set up
    if not logging.getLogger().hasHandlers():
        dictConfig(logging_config)


# ✅ Khởi tạo settings & chỉ cấu hình logging một lần
settings = Settings()
setup_logging()

# ✅ Tạo logger dùng chung
logger = logging.getLogger("fastapi_project")
