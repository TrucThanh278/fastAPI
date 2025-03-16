import jwt
from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src.api.crud import user_crud
from src.deps import SessionDep
from src.configs.config import settings
from src.configs.security import create_token
from src.configs.config import logger
from src.utils.oauth2_form import OAuth2PasswordRequestEmailForm
from src.deps import SessionDep
from sqlmodel import select
from src.models.users import User, RefreshTokenRequest
from src.api.crud import refresh_token_crud


from src.deps import get_current_user, SessionDep

router = APIRouter(prefix="/auth", tags=["login"])


@router.post("/login")
async def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestEmailForm, Depends()]
):
    user_db = user_crud.authenticate(
        session=session, email=form_data.email, password=form_data.password
    )
    if not user_db:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    exist_refresh_token = refresh_token_crud.get_refresh_token_active(
        session=session, user_id=user_db.id
    )

    if exist_refresh_token is not None:
        refresh_token_crud.revoke_refresh_token(
            session=session, refresh_token=exist_refresh_token.token, user_id=user_db.id
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(str(user_db.id), expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_token(str(user_db.id), expires_delta=refresh_token_expires)

    new_refresh_token = refresh_token_crud.create_refresh_token(
        user_id=user_db.id, token=refresh_token, session=session
    )

    session.add(new_refresh_token)
    session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user(["user", "admin"]))],
):
    return current_user


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user(["user"]))],
    session: SessionDep,
):
    current_user.refresh_token = None
    session.add(current_user)
    session.commit()
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest, session: SessionDep):
    try:
        payload = jwt.decode(
            request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token 2",
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token 3"
        )

    exist_user = user_crud.get_user(session=session, user_id=user_id)
    if not exist_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    refresh_token_db = refresh_token_crud.get_refresh_token(
        session=session, user_id=user_id, refresh_token=request.refresh_token
    )

    if (
        refresh_token_db.token != request.refresh_token
        and not refresh_token_db.is_revoked
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token 1",
        )

    # revoked old token
    refresh_token_crud.revoke_refresh_token(
        session=session, user_id=user_id, refresh_token=request.refresh_token
    )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_token(
        str(exist_user.id), expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = create_token(
        str(exist_user.id), expires_delta=refresh_token_expires
    )

    refresh_token_crud.create_refresh_token(
        session=session, token=new_refresh_token, user_id=exist_user.id
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
