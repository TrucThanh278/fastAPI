import jwt
from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src import crud
from src.api.deps import SessionDep
from src.configs.config import settings
from src.configs.security import create_access_token
from src.configs.config import logger
from src.utils.oauth2_form import OAuth2PasswordRequestEmailForm
from src.api.deps import SessionDep
from src.models import User, BaseModel

router = APIRouter(tags=["login"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/login")
async def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestEmailForm, Depends()]
):
    user = crud.authenticate(
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
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("subject")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = crud.get_user(session=SessionDep, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user


@router.get("/auth/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
