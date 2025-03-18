import jwt
from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi_mail import FastMail, MessageSchema, MessageType
from jwt.exceptions import InvalidTokenError
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from src.deps import SessionDep
from src.api.crud import otp_crud, user_crud, refresh_token_crud
from src.configs import mail
from src.configs.config import settings
from src.configs.security import (
    create_token,
    create_reset_password_token,
    decode_reset_password_token,
    pwd_context,
    create_otp,
    get_hash_password,
)
from src.configs.config import logger
from src.models.users import User
from src.schemas.request import RefreshTokenRequest, ForgetPasswordRequest, LoginRequest
from src.schemas.user import UserPublic, UserUpdate
from src.schemas.reset_password import SuccessMessage, ResetForgetPassword


from src.deps import get_current_user, SessionDep

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory=str(settings.TEMPLATE_FOLDER))


@router.post("/login")
async def login(session: SessionDep, user_login: LoginRequest):
    user_db = user_crud.authenticate(
        session=session, email=user_login.email, password=user_login.password
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


@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user(["all"]))],
):
    return UserPublic.from_orm(current_user)


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


@router.post("/forget-password")
async def forget_password(
    background_tasks: BackgroundTasks,
    forget_password_req: ForgetPasswordRequest,
    session: SessionDep,
):
    try:
        user = user_crud.get_user_by_email(
            session=session, email=forget_password_req.email
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Email address",
            )
        otp = create_otp()
        otp_rec = otp_crud.create_otp(email=user.email, otp=otp, session=session)
        if otp_rec:
            email_body = {
                "company_name": settings.MAIL_FROM_NAME,
                "otp": otp,
                "expiry_min": settings.OTP_EXPIRE_MINUTES,
            }
            message = MessageSchema(
                subject="Password Reset OTP",
                recipients=[forget_password_req.email],
                template_body=email_body,
                subtype=MessageType.html,
            )
            template_name = "mail/otp.html"

            fm = FastMail(mail.conf)
            background_tasks.add_task(fm.send_message, message, template_name)
            url = f"{settings.APP_HOST}{settings.FORGET_PASSWORD_URL}?email={forget_password_req.email}"
            print(">>>>> url: ", url)

            return RedirectResponse(
                url=f"{settings.APP_HOST}{settings.FORGET_PASSWORD_URL}?email={forget_password_req.email}",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": "Please wait before requesting a new OTP!"},
            )

    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something Unexpected, Server Error!",
        )


@router.get("/forget-password/otp", response_class=HTMLResponse)
async def get_opt_page(email: str):
    print(">>>> Path: ", templates.env)
    return templates.TemplateResponse("otp.html", {"request": {}, "email": email})


@router.post("/forget-password/verify-otp", response_class=HTMLResponse)
async def verify_otp(session: SessionDep, email: str = Form(...), otp: str = Form(...)):
    if otp_crud.verify_otp(email=email, otp=otp, session=session):
        return RedirectResponse(
            url=f"{settings.APP_HOST}{settings.RESET_PASSWORD_URL}?email={email}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(
        "otp.html", {"request": {}, "email": email, "error": "Invalid or expired OTP"}
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def get_reset_password_page(email: str):
    return templates.TemplateResponse(
        "reset_password.html", {"request": {}, "email": email}
    )


@router.post("/reset-password")
async def reset_password(
    session: SessionDep,
    email: str = Form(...),
    new_password: str = Form(...),
):
    hash_password = get_hash_password(new_password)
    user_update = UserUpdate(email=email, password=hash_password)
    user_db = user_crud.get_user_by_email(session=session, email=email)
    user = user_crud.update_user(session=session, user=user_db, user_update=user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password reset successfully"},
    )
