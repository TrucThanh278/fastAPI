import uuid
from typing import Optional
from pydantic import EmailStr, BaseModel
import time

from sqlmodel import SQLModel, Field


class CustomBaseModel(SQLModel):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    created_at: str = Field(default_factory=lambda: str(int(time.time())))
    updated_at: str = Field(default_factory=lambda: str(int(time.time())))


class UserBase(CustomBaseModel):
    name: str | None = Field(primary_key=True, max_length=255)
    email: str
    is_active: bool = True
    is_superuser: bool = False


class User(CustomBaseModel, table=True):
    name: str
    email: EmailStr = Field(max_length=255)
    refresh_token: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserRegister(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr
    password: str


class TokenData(BaseModel):
    user_id: str | None = None


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None
