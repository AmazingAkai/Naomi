from __future__ import annotations

from typing import TYPE_CHECKING

from .challenges import router as challenges_router

if TYPE_CHECKING:
    from naomi import Naomi

__all__ = ("mount_routers",)


def mount_routers(app: Naomi) -> None:
    routers = (challenges_router,)

    for router in routers:
        router.mount(app)
