import uuid
from sqlmodel import Field, Relationship
from src.models.base import CustomBaseModel


class RefreshToken(CustomBaseModel, table=True):
    token: str = Field()
    is_revoked: bool = False

    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="refresh_tokens")
