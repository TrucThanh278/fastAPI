from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import create_engine, SQLModel, Session
from src.models.users import User
from src.core.config import settings
from src.seeds import seed_database

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI()), echo=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        seed_database(session)

    yield
