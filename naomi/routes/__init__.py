from __future__ import annotations

from .admin import router as admin_router
from .challenges import router as challenges_router

__all__ = ("routers",)


routers = (challenges_router, admin_router)
