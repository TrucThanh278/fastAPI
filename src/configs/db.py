from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import create_engine, SQLModel, Session
from src.models.users import User
from src.configs.config import settings
from src.seeds import seed_database

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI()), echo=True)


# def initDB():
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         seed_database(session)

#     yield


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tạo tat ca cac bang
    SQLModel.metadata.create_all(engine)

    # Seed dữ liệu
    with Session(engine) as session:
        seed_database(session)

    yield
