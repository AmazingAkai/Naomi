from __future__ import annotations

import os
from typing import TYPE_CHECKING

from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from naomi.utils.router import Router

if TYPE_CHECKING:
    from typing import TypedDict

    from httpx import AsyncClient
    from starlette.requests import Request
    from starlette.responses import Response

    class User(TypedDict):
        id: int
        avatar: str
        name: str


router = Router()
BASE_CDN = "https://cdn.discordapp.com"
BASE_API = "https://discord.com/api"


def format_avatar(id: int, discriminator: str, avatar: str | None) -> str:
    if avatar is not None:
        animated = avatar.startswith("a_")
        format = "gif" if animated else "png"

        return f"{BASE_CDN}/avatars/{id}/{avatar}.{format}?size=1024"

    avatar_id = (id >> 22) % 6 if discriminator == "0" else int(discriminator) % 5

    return f"{BASE_CDN}/embed/avatars/{avatar_id}.png"


async def fetch_user(client: AsyncClient, token: str) -> User | None:
    response = await client.get(BASE_API + "/users/@me", headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        raise HTTPException(response.status_code)

    data = response.json()

    if data["id"] != os.environ["ADMIN_DISCORD_ID"]:
        return None
    avatar = format_avatar(data["id"], data["discriminator"], data["avatar"])
    user: User = {"id": data["id"], "name": data["global_name"], "avatar": avatar}
    return user


@router.get("/login")
async def login(request: Request) -> Response:
    redirect_uri = request.url_for("/login/callback")
    return await request.app.discord.authorize_redirect(request, redirect_uri)


@router.get("/login/callback")
async def login_callback(request: Request) -> Response:
    token = await request.app.discord.authorize_access_token(request)
    user = await fetch_user(request.app.client, token["access_token"])
    if user is not None:
        request.session["user"] = user
    return RedirectResponse(url="/")


@router.get("/logout")
async def logout(request: Request) -> Response:
    request.session.pop("user", None)
    return RedirectResponse(url="/")
