import uuid
from src.models import User, UserCreate, UserUpdate
from sqlmodel import Session, select
from src.configs.security import get_hash_password, verify_password
from src.configs.config import logger


def create_user(*, session: Session, user_create: UserCreate):
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_hash_password(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user(*, session: Session, user_id: str):
    user_ids = uuid.UUID(user_id.hex)
    statement = select(User).where(User.id == user_ids)
    logger.info(">>>>>>>>>>>>>>>>>> Equal: ", User.id == user_ids)
    user = session.exec(statement).first()
    return user


def get_users(*, session: Session):
    statement = select(User)
    users = session.exec(statement).all()
    return users


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
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
