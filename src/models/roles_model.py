from sqlmodel import Field, Relationship, Session, SQLModel, create_engine
from src.models.base_model import CustomBaseModel


class Role(CustomBaseModel, table=True):
    name: str
    description: str | None = None
    users: list["User"] = Relationship(
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin"}
    )
