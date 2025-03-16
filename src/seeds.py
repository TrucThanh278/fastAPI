from sqlmodel import Session, select
from src.api.crud import role_crud, user_crud
from src.models.users import UserCreate
from src.models.roles import Role
from src.configs.security import get_hash_password


def seed_database(session: Session):
    admin_role = role_crud.get_role_by_name(session=session, role_name="admin")
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator role")
        session.add(admin_role)
        session.commit()
        session.refresh(admin_role)
        print("Created default role: admin")

    user_role = role_crud.get_role_by_name(session=session, role_name="user")
    if not user_role:
        user_role = Role(name="user", description="Regular user role")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
        print("Created default role: user")

    admin_email = "admin@gmail.com"
    admin_user = user_crud.get_user_by_email(session=session, email=admin_email)
    if not admin_user:
        admin_user_create = UserCreate(
            name="Admin",
            email=admin_email,
            password="admin@123",
            role="admin",
        )
        user_crud.create_user(session=session, user_create=admin_user_create)
        print(f"Created default admin user: {admin_email}")
