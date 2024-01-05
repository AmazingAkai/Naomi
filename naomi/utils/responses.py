from __future__ import annotations

from typing import TYPE_CHECKING

import orjson
from starlette.responses import Response

if TYPE_CHECKING:
    from typing import Any, Mapping

    from starlette.background import BackgroundTask

__all__ = ("ORJSONResponse",)


class ORJSONResponse(Response):
    media_type = "application/json"

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content, option=orjson.OPT_INDENT_2)
