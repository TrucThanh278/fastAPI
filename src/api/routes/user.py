import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from src.models import UserCreate
from src.api.deps import SessionDep
from src import crud
from src.models import User, UserPublic, UserUpdate, UserRegister
from src.configs.config import logger


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(user_id: uuid.UUID, session: SessionDep) -> Any:
    # user = session.get(User, user_id)
    user = crud.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    return user
    # if not user:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="The user doesn't have enough privileges",
    #     )
    # return user


@router.post("/")
async def create_user(*, session: SessionDep, user_data: UserCreate):
    user = crud.get_user_by_email(session=session, email=user_data.email)

    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(session=session, user_create=user_data)
    return user


@router.get("/")
async def get_users(*, session: SessionDep):
    logger.debug(f"Gọi database để lấy user")
    users = crud.get_users(session=session)
    return users


@router.put("/{user_id}")
async def update_user(user_id: uuid.UUID, user_update: UserUpdate, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    user = crud.update_user(session=session, user=user, user_update=user_update)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    crud.delete_user(session=session, user_id=user_id)
    return {"detail": "User deleted"}
