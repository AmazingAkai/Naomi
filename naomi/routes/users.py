from __future__ import annotations

from typing import TYPE_CHECKING

from naomi.utils.router import Router

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

router = Router()


@router.get("/login")
async def login(request: Request) -> Response:
    return request.app.templates.TemplateResponse(request, "index.html")
