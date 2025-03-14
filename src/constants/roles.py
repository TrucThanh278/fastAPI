from sqlmodel import Session
from src.models.roles_model import Role


def create_role(*, session: Session, role_create: Role):
    db_obj = Role.model_validate(role_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
