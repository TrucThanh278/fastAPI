from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgetPasswordRequest(BaseModel):
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str
