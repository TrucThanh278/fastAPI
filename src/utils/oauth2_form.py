from fastapi import Form
from fastapi.security import OAuth2


class OAuth2PasswordRequestEmailForm:
    def __init__(
        self,
        email: str = Form(...),  # Đổi từ username -> email
        password: str = Form(...),
    ):
        self.email = email
        self.password = password
