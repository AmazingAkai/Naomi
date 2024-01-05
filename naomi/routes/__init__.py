from __future__ import annotations

from typing import TYPE_CHECKING

from .truthordare import router as truthordare_router

if TYPE_CHECKING:
    from naomi import Naomi

__all__ = ("mount_routers",)


def mount_routers(app: Naomi) -> None:
    routers = (truthordare_router,)

    for router in routers:
        router.mount(app)
