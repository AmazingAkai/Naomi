from __future__ import annotations

from typing import TYPE_CHECKING

from naomi.utils.limiter import limiter
from naomi.utils.router import Router

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response


router = Router()


@router.get("/")
@limiter.exempt
async def home(request: Request) -> Response:
    return request.app.templates.TemplateResponse(request, "index.html")


@router.get("/challenges", requires_auth=True)
@limiter.exempt
async def challenges(request: Request) -> Response:
    return request.app.templates.TemplateResponse(request, "challenges.html")


@router.get("/actions", requires_auth=True)
@limiter.exempt
async def actions(request: Request) -> Response:
    return request.app.templates.TemplateResponse(request, "actions.html")
