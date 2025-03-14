from fastapi import Form
from fastapi.security import OAuth2


class OAuth2PasswordRequestEmailForm:
    def __init__(
        self,
        email: str = Form(...),
        password: str = Form(...),
    ):
        self.email = email
        self.password = password
