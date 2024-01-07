from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar

from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.status import HTTP_401_UNAUTHORIZED

if TYPE_CHECKING:
    from starlette.requests import Request

    from naomi import Naomi


__all__ = ("Router",)

T = TypeVar("T", bound=Callable[..., Any])


class Router:
    def __init__(self, base_route: str | None = None) -> None:
        self.base_route = base_route or ""
        self.routes: list[Route] = []

    def route(self, path: str, requires_auth: bool = False, methods: list[str] | None = None) -> Callable[[T], T]:
        def decorator(func: T) -> T:
            async def wrapped_func(request: Request, *args: Any, **kwargs: Any) -> T:
                if requires_auth and not request.session.get("user"):
                    if request.method != "GET":
                        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Authentication required")
                    return RedirectResponse("/")  # type: ignore

                return await func(request, *args, **kwargs)

            full_path = f"{self.base_route}/{path[1:] if path.startswith('/') else path}"
            route = Route(
                path=full_path,
                name=full_path,
                endpoint=wrapped_func,
                methods=methods,
            )
            self.routes.append(route)
            return func

        return decorator

    def get(self, path: str, requires_auth: bool = False) -> Callable[[T], T]:
        return self.route(path, requires_auth=requires_auth, methods=["GET"])

    def post(self, path: str, requires_auth: bool = False) -> Callable[[T], T]:
        return self.route(path, requires_auth=requires_auth, methods=["POST"])

    def put(self, path: str, requires_auth: bool = False) -> Callable[[T], T]:
        return self.route(path, requires_auth=requires_auth, methods=["PUT"])

    def delete(self, path: str, requires_auth: bool = False) -> Callable[[T], T]:
        return self.route(path, requires_auth=requires_auth, methods=["DELETE"])

    def patch(self, path: str, requires_auth: bool = False) -> Callable[[T], T]:
        return self.route(path, requires_auth=requires_auth, methods=["PATCH"])

    def head(self, path: str, requires_auth: bool = False) -> Callable[[T], T]:
        return self.route(path, requires_auth=requires_auth, methods=["HEAD"])

    def mount(self, app: Naomi) -> None:
        app.router.routes.extend(self.routes)
