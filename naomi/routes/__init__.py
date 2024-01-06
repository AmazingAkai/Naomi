from __future__ import annotations

from .admin import router as admin_router
from .challenges import router as challenges_router
from .pages import router as pages_router

__all__ = ("routers",)


routers = (
    challenges_router,
    admin_router,
    pages_router,
)
