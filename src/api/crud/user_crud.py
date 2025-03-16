import uuid
from typing import Optional
from sqlmodel import Session, select
from src.configs.security import get_hash_password, verify_password
from src.configs.config import logger
from src.models.users import User, UserCreate, UserUpdate
from src.schemas.user import UserPublic

from src.api.crud import role_crud


def create_user(*, session: Session, user_create: UserCreate):
    role = role_crud.get_role_by_name(session=session, role_name=user_create.role)
    db_obj = User.model_validate(
        user_create,
        update={
            "password": get_hash_password(user_create.password),
            "role_id": role.id,
            "role": role,
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user(*, session: Session, user_id: uuid) -> User:
    print("user_id", user_id)
    statement = select(User).where(User.id == user_id)
    print("statement", statement)
    user = session.exec(statement).first()
    return user


def get_users(*, session: Session, name_query: Optional[str] = None):
    statement = select(User)

    if name_query:
        statement = statement.where(User.name.like(f"%{name_query}%"))

    users = session.exec(statement).all()
    return [
        UserPublic(
            id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            role=user.role.name if user.role else None,
        )
        for user in users
    ]


def get_user_by_email(*, session: Session, email: str):
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def update_user(*, session: Session, user_update: UserUpdate, user: User):
    user_data = user.model_dump()
    update_data = user_update.model_dump(exclude_unset=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(*, session: Session, user_id: uuid.UUID):
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    session.delete(user)
    session.commit()
    return True


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session=session, email=email)
    if not user or not verify_password(password, user.password):
        return None
    return user
