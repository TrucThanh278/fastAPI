import uuid
import time

from sqlmodel import SQLModel, Field


class CustomBaseModel(SQLModel):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    created_at: str = Field(default_factory=lambda: str(int(time.time())))
    updated_at: str = Field(default_factory=lambda: str(int(time.time())))
