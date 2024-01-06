from __future__ import annotations

import os
from typing import TYPE_CHECKING

import beanie
from authlib.integrations.starlette_client import OAuth
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from naomi.models import document_models
from naomi.routes import routers

if TYPE_CHECKING:
    from authlib.integrations.starlette_client import StarletteOAuth2App


class Naomi(Starlette):
    db: AsyncIOMotorClient
    discord: StarletteOAuth2App
    client: AsyncClient

    def __init__(self) -> None:
        debug = bool(os.environ.get("DEBUG", False))
        super().__init__(debug=debug, routes=[Mount("/static", StaticFiles(directory="naomi/static"), name="static")])
        self.templates = Jinja2Templates(directory="naomi/templates")

        self.mount_routers()
        self.setup_oauth()

        self.add_middleware(SessionMiddleware, secret_key=os.environ["SESSION_SECRET"])

        self.add_event_handler("startup", self.startup)
        self.add_event_handler("shutdown", self.shutdown)

    async def startup(self) -> None:
        self.db = AsyncIOMotorClient(os.environ["MONGO_URI"])

        await beanie.init_beanie(database=self.db[os.environ["DATABASE_NAME"]], document_models=document_models)
        self.client = AsyncClient()

    async def shutdown(self) -> None:
        self.db.close()
        await self.client.aclose()

    def mount_routers(self) -> None:
        for router in routers:
            router.mount(self)

    def setup_oauth(self) -> None:
        self.discord = OAuth().register(  # type: ignore
            name="discord",
            client_id=os.environ["DISCORD_CLIENT_ID"],
            client_secret=os.environ["DISCORD_CLIENT_SECRET"],
            authorize_url="https://discord.com/api/oauth2/authorize",
            access_token_url="https://discord.com/api/oauth2/token",
            server_metadata_url=None,
            client_kwargs={"scope": "identify"},
        )


app = Naomi()
