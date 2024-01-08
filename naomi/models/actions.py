from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import TYPE_CHECKING, Literal

from beanie import Document

if TYPE_CHECKING:
    from starlette.requests import Request


class Action(Document):
    id: int
    data: bytes
    type: Literal["hug", "pat", "slap", "kiss", "bite", "tickle", "cuddle", "poke"]
    created_at: datetime

    class Settings:
        name = "actions"

    def to_dict(self, request: Request) -> dict:
        return {
            "id": self.id,
            "url": str(request.base_url) + f"api/actions/r/{self.id}",
            "type": self.type,
            "created_at": self.created_at,
        }
