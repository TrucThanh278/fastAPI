from sqlmodel import Session, select
from src.models.roles_model import Role


def create_role(*, session: Session, role_create: Role):
    db_obj = Role.model_validate(role_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_role(*, session: Session, role_create: Role):
    statement = select(Role).where(Role.name == role_create.name)
    role = session.exec(statement)
    return role


def get_role_by_name(*, session: Session, role_name: str):
    statement = select(Role).where(Role.name == role_name)
    role = session.exec(statement).first()
    return role


def get_roles(*, session: Session):
    statement = select(Role)
    roles = session.exec(statement).all()
    return roles
