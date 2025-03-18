import time
import jwt
import secrets
from typing import Any
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from src.core.config import settings
from src.core.config import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_pw: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_pw, hashed_pw)


def create_token(
    subject: str | Any,
    expires_delta: timedelta,
    created_at: str = str(int(time.time())),
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": int(expire.timestamp()),
        "sub": str(subject),
        "iat": created_at,
    }
    encode_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encode_jwt


def create_otp() -> str:
    return "".join(
        secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(6)
    )
