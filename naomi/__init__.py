from __future__ import annotations

import os
from json import JSONDecodeError
from typing import TYPE_CHECKING

import beanie
from authlib.integrations.starlette_client import OAuth
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from orjson import JSONDecodeError as ORJSONDecodeError
from pydantic_core import ValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from starlette.templating import Jinja2Templates

from naomi.models import document_models
from naomi.routes import routers
from naomi.utils.limiter import limiter
from naomi.utils.responses import ORJSONResponse

if TYPE_CHECKING:
    from authlib.integrations.starlette_client import StarletteOAuth2App
    from starlette.requests import Request
    from starlette.responses import Response


class Naomi(Starlette):
    db: AsyncIOMotorClient
    discord: StarletteOAuth2App
    client: AsyncClient

    def __init__(self) -> None:
        debug = bool(os.environ.get("DEBUG", False))
        super().__init__(
            debug=debug,
            routes=[Mount("/static", StaticFiles(directory="naomi/static"), name="static")],
            exception_handlers={
                HTTP_404_NOT_FOUND: self.handle_not_found,
                HTTP_500_INTERNAL_SERVER_ERROR: self.handle_internal_server_error,
            },
        )
        self.templates = Jinja2Templates(directory="naomi/templates")

        self.state.limiter = limiter
        self.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

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

    def handle_not_found(self, request: Request, exception: Exception) -> Response:
        if request.method != "GET":
            return ORJSONResponse({"error": "404: Not Found"}, status_code=HTTP_404_NOT_FOUND)
        return self.templates.TemplateResponse(request, "not-found.html", status_code=HTTP_404_NOT_FOUND)

    def handle_internal_server_error(self, request: Request, exception: Exception) -> Response:
        if isinstance(
            exception,
            (
                JSONDecodeError,
                ORJSONDecodeError,
                ValidationError,
                KeyError,
                ValueError,
                TypeError,
            ),
        ):
            return ORJSONResponse({"error": "400: Bad Request"}, HTTP_400_BAD_REQUEST)
        else:
            if request.method != "GET":
                return ORJSONResponse({"error": "500: Internal Server Error"}, HTTP_500_INTERNAL_SERVER_ERROR)
            return self.templates.TemplateResponse(request, "error.html", status_code=HTTP_500_INTERNAL_SERVER_ERROR)


app = Naomi()
