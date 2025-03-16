from sqlmodel import Relationship
from src.models.base import CustomBaseModel


class Role(CustomBaseModel, table=True):
    name: str
    description: str | None = None
    users: list["User"] = Relationship(
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin"}
    )
