from src.models import User
from sqlmodel import create_engine, SQLModel
from src.configs.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI()), echo=True)


def initDB():
    SQLModel.metadata.create_all(engine)
