import uuid
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict
from src.models.users import UserBase
from src.models.users import User


class UserPublic(UserBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, user: User):
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            role=user.role.name if user.role else None,
        )


class UserUpdate(SQLModel):
    email: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)
    role: str = Field(default="user")
