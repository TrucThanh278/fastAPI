import uuid
from typing import Optional
from pydantic import EmailStr, BaseModel, ConfigDict
from sqlmodel import SQLModel, Field, Relationship

from src.models.base_model import CustomBaseModel
from src.models.roles_model import Role


class UserBase(CustomBaseModel):
    name: str | None = Field(primary_key=True, max_length=255)
    email: str
    is_active: bool = True
    role: str


class User(CustomBaseModel, table=True):
    name: str
    email: EmailStr = Field(max_length=255)
    refresh_token: Optional[str] = None
    hashed_password: str
    is_active: bool = True

    role_id: uuid.UUID | None = Field(default=None, foreign_key="role.id")
    role: Role | None = Relationship(back_populates="users")


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)
    role: str = Field(default="user")


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


class UsersPublic(SQLModel):
    data: list[UserPublic.from_orm]
    count: int


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
