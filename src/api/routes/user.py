import uuid
from typing import Any, Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_pagination import paginate
from src.deps import SessionDep, get_current_user
from src.api.crud import user_crud
from src.models.users import UserCreate
from src.models.users import (
    User,
    UserUpdate,
)
from src.schemas.user import UserPublic
from src.utils.pagination import CustomPage


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(user_id: uuid.UUID, session: SessionDep) -> Any:
    user = user.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    return user


@router.post("/", response_model=UserPublic)
async def create_user(*, session: SessionDep, user_data: UserCreate):
    user = user.get_user_by_email(session=session, email=user_data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = user.create_user(session=session, user_create=user_data)
    rs = UserPublic.from_orm(user)
    return rs


@router.get("/")
async def get_users(
    *,
    session: SessionDep,
    name: Optional[str] = Query(default=None, description="Search users by name")
) -> CustomPage[UserPublic]:
    users = user_crud.get_users(session=session, name_query=name)
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
    user = user.update_user(session=session, user=user, user_update=user_update)
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
    user.delete_user(session=session, user_id=user_id)
    return {"detail": "User deleted"}
