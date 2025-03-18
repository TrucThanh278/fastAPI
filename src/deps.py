import jwt
from jwt import DecodeError, ExpiredSignatureError, MissingRequiredClaimError
from sqlmodel import Session
from src.core.db import engine
from typing import Annotated
from fastapi import Depends, HTTPException, status
from typing import Callable
from src.core.config import settings
from src.api.crud import user_crud
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from src.models.users import User

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
security = HTTPBearer()


def get_session():

    with Session(engine) as session:

        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(required_roles: list[str] = []) -> Callable[[], User]:

    async def current_user(
        session: SessionDep,
        token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    ) -> User:
        try:
            payload = jwt.decode(
                token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            print(">>> TOKEN: ", token.credentials)
            print(">>> SECRET_KEY: ", settings.SECRET_KEY)
            print(">>> ALGORITHM: ", settings.ALGORITHM)

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your token has expired. Please log in again.",
            )
        except DecodeError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Error when decoding the token. Please check your request.",
            )
        except MissingRequiredClaimError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="There is no required field in your token. Please contact the administrator.",
            )

        user_id = payload["sub"]

        user: User = user_crud.get_user(user_id=user_id, session=session)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        if required_roles:
            is_valid_role = False

            if "all" in required_roles:
                is_valid_role = True
            else:
                for role in required_roles:
                    if role == user.role.name:
                        is_valid_role = True

            if not is_valid_role:
                raise HTTPException(
                    status_code=403,
                    detail=f"""Role "{required_roles}" is required for this action""",
                )

        return user

    return current_user
