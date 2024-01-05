from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar

from starlette.routing import Route

if TYPE_CHECKING:
    from naomi import Naomi


__all__ = ("Router",)

T = TypeVar("T", bound=Callable[..., Any])


class Router:
    def __init__(self, base_route: str) -> None:
        self.base_route = base_route
        self.routes: list[Route] = []

    def route(self, path: str, methods: list[str] | None = None) -> Callable[[T], T]:
        def decorator(func: T) -> T:
            full_path = f"{self.base_route}/{path[1:] if path.startswith('/') else path}"
            route = Route(
                path=full_path,
                endpoint=func,
                methods=methods,
            )
            self.routes.append(route)
            return func

        return decorator

    def get(self, path: str) -> Callable[[T], T]:
        return self.route(path, methods=["GET"])

    def post(self, path: str) -> Callable[[T], T]:
        return self.route(path, methods=["POST"])

    def put(self, path: str) -> Callable[[T], T]:
        return self.route(path, methods=["PUT"])

    def delete(self, path: str) -> Callable[[T], T]:
        return self.route(path, methods=["DELETE"])

    def patch(self, path: str) -> Callable[[T], T]:
        return self.route(path, methods=["PATCH"])

    def head(self, path: str) -> Callable[[T], T]:
        return self.route(path, methods=["HEAD"])

    def mount(self, app: Naomi) -> None:
        app.add_route
        app.router.routes.extend(self.routes)
