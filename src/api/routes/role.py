from typing import Any, Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import paginate

from src.deps import SessionDep, get_current_user
from src.api.crud import role_crud
from src.models.roles import Role
from src.models.users import User
from src.utils.pagination import CustomPage


router = APIRouter(prefix="/role", tags=["role"])


@router.post("/")
async def create_role(
    session: SessionDep,
    role_create: Role,
    current_user: Annotated[User, Depends(get_current_user(["admin"]))],
) -> Any:
    role = role.get_role(session=session, role_create=role_create)
    if not role:
        raise HTTPException(status_code=400, detail="Role already registered")
    role = role.create_role(session=session, role_create=role_create)
    return role


@router.get("/{role_name}")
async def get_role(
    session: SessionDep,
    role_name: str,
    current_user: Annotated[User, Depends(get_current_user(["admin"]))],
) -> Role:
    role = role.get_role_by_name(session=session, role_name=role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.get("/")
async def get_role(
    session: SessionDep,
) -> CustomPage[Role]:
    roles = role_crud.get_roles(session=session)
    return paginate(roles)
