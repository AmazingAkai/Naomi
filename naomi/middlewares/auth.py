from __future__ import annotations

import base64
import binascii
from typing import TYPE_CHECKING

import bcrypt
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend as StarletteAuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.middleware.authentication import AuthenticationMiddleware as StarletteAuthenticationMiddleware

from naomi.models.users import User

if TYPE_CHECKING:
    from starlette.requests import HTTPConnection

    from naomi import Naomi

__all__ = ("AuthenticationBackend", "AuthenticationMiddleware")


class AuthenticationBackend(StarletteAuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, SimpleUser] | None:
        if "Authorization" not in conn.headers:
            return None

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "Bearer":
                return None
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid credentials")

        name, _, password = decoded.partition(":")
        user = await User.find_one(User.name == name)

        if user and bcrypt.checkpw(password, user.password):  # type: ignore
            return AuthCredentials(["authenticated"]), SimpleUser(name)


class AuthenticationMiddleware(StarletteAuthenticationMiddleware):
    def __init__(self, app: Naomi) -> None:
        super().__init__(app=app, backend=AuthenticationBackend())
