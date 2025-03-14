import uuid
from typing import Any, Annotated
from sqlmodel import col, delete, func, select
from fastapi import APIRouter, HTTPException, Depends
from src.models.users_model import UserCreate
from src.deps import SessionDep, get_current_user
from src.api.crud import user_crud
from src.models.users_model import (
    User,
    UserPublic,
    UserUpdate,
    UsersPublic,
    UserRegister,
)
from fastapi_pagination import Page, paginate


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(user_id: uuid.UUID, session: SessionDep) -> Any:
    user = user_crud.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    return user


@router.post("/", response_model=UserPublic)
async def create_user(*, session: SessionDep, user_data: UserCreate):
    user = user_crud.get_user_by_email(session=session, email=user_data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = user_crud.create_user(session=session, user_create=user_data)
    rs = UserPublic.from_orm(user)
    return rs


@router.get("/")
async def get_users(*, session: SessionDep) -> Page[UserPublic]:
    users = user_crud.get_users(session=session)
    return paginate(users)


# @router.get(
#     "/",
#     # dependencies=[Depends(get_current_active_superuser)],
#     response_model=UsersPublic,
# )
# def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:

#     count_statement = select(func.count()).select_from(User)
#     count = session.exec(count_statement).one()

#     statement = select(User).offset(skip).limit(limit)
#     users = session.exec(statement).all()

#     return UsersPublic(data=users, count=count)


@router.put("/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user(["admin"]))],
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    user = user_crud.update_user(session=session, user=user, user_update=user_update)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user(["admin"]))],
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    user_crud.delete_user(session=session, user_id=user_id)
    return {"detail": "User deleted"}
