import os

import beanie
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from naomi.middlewares.auth import AuthenticationMiddleware
from naomi.models import document_models
from naomi.routes import mount_routers


class Naomi(Starlette):
    db: AsyncIOMotorClient

    def __init__(self) -> None:
        debug = bool(os.environ.get("DEBUG", False))
        super().__init__(debug=debug, routes=[Mount("/static", StaticFiles(directory="naomi/static"), name="static")])
        self.templates = Jinja2Templates(directory="naomi/templates")

        mount_routers(self)

        self.add_middleware(AuthenticationMiddleware)

        self.add_event_handler("startup", self.startup)
        self.add_event_handler("shutdown", self.shutdown)

        print(self.routes)

    async def startup(self) -> None:
        self.db = AsyncIOMotorClient(os.environ["MONGO_URI"])

        await beanie.init_beanie(database=self.db[os.environ["DATABASE_NAME"]], document_models=document_models)

    async def shutdown(self) -> None:
        self.db.close()


app = Naomi()
