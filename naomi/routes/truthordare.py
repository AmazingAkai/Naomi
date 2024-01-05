from __future__ import annotations

from typing import TYPE_CHECKING

from naomi.utils.responses import ORJSONResponse
from naomi.utils.router import Router

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

router = Router(base_route="/api")


@router.get("/truth")
async def truth(request: Request) -> Response:
    truth = {"truth": "Hello World"}
    return ORJSONResponse(content=truth)
