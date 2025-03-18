import uuid
from sqlmodel import SQLModel, Field
from sqlalchemy import BIGINT


class OTP(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    email: str
    otp: str = Field(max_length=6)
    expires_at: int = Field(sa_type=BIGINT)

    class Config:
        arbitrary_types_allowed = True
