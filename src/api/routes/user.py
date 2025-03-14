import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from src.models.users_model import UserCreate
from src.api.deps import SessionDep
from src.api.crud import user_crud
from src.models.users_model import User, UserPublic, UserUpdate, UserRegister
from src.configs.config import logger


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(user_id: uuid.UUID, session: SessionDep) -> Any:
    # user = session.get(User, user_id)
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
async def get_users(*, session: SessionDep):
    logger.debug(f"Gọi database để lấy user")
    users = user_crud.get_users(session=session)
    return users


@router.put("/{user_id}")
async def update_user(user_id: uuid.UUID, user_update: UserUpdate, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    user = user_crud.update_user(session=session, user=user, user_update=user_update)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    user_crud.delete_user(session=session, user_id=user_id)
    return {"detail": "User deleted"}
