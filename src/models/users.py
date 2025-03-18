import uuid
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import BIGINT

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
    email: EmailStr = Field(max_length=255, unique=True)
    password: str
    is_active: bool = True
    delete_at: str | None = Field(default=None, nullable=True)

    role_id: uuid.UUID | None = Field(default=None, foreign_key="role.id")
    role: Role | None = Relationship(back_populates="users")
    refresh_tokens: list[RefreshToken] | None = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
