import uuid
from typing import Optional
from pydantic import EmailStr, BaseModel, ConfigDict
from sqlmodel import SQLModel, Field, Relationship

from src.models.base import CustomBaseModel
from src.models.roles import Role
from src.models.tokens import RefreshToken


class UserBase(CustomBaseModel):
    name: str | None = Field(primary_key=True, max_length=255)
    email: str
    is_active: bool = True
    role: str


class User(CustomBaseModel, table=True):
    name: str
    email: EmailStr = Field(max_length=255)
    password: str
    is_active: bool = True
    delete_at: str | None = Field(default=None, nullable=True)

    role_id: uuid.UUID | None = Field(default=None, foreign_key="role.id")
    role: Role | None = Relationship(back_populates="users")
    refresh_tokens: list[RefreshToken] | None = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)
    role: str = Field(default="user")


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserRegister(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str
