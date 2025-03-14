import jwt
from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src.api.crud import user_crud
from src.deps import SessionDep
from src.configs.config import settings
from src.configs.security import create_access_token
from src.configs.config import logger
from src.utils.oauth2_form import OAuth2PasswordRequestEmailForm
from src.deps import SessionDep
from src.models.users_model import User, RefreshTokenRequest

from src.deps import get_current_user, SessionDep

router = APIRouter(prefix="/auth", tags=["login"])


@router.post("/login")
async def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestEmailForm, Depends()]
):
    user = user_crud.authenticate(
        session=session, email=form_data.email, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(str(user.id), expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        str(user.id), expires_delta=refresh_token_expires
    )

    user.refresh_token = refresh_token
    session.add(user)
    session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user(["user"]))],
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
        user_id = payload.get("subject")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user = user_crud.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if user.refresh_token != request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        str(user.id), expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = create_access_token(
        str(user.id), expires_delta=refresh_token_expires
    )

    user.refresh_token = new_refresh_token
    session.add(user)
    session.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
