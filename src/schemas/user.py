import uuid
from sqlmodel import SQLModel
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


class UsersPublic(SQLModel):
    data: list[UserPublic.from_orm]
    count: int
