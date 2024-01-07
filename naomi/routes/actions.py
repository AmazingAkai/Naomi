from __future__ import annotations

import random
from typing import TYPE_CHECKING

from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from naomi.models.actions import Action
from naomi.utils.responses import ORJSONResponse
from naomi.utils.router import Router

if TYPE_CHECKING:
    from starlette.requests import Request

ALLOWED_TYPES = ("hug", "pat", "slap", "kiss", "bite", "tickle", "cuddle", "poke")

router = Router(base_route="/api")


@router.get("/actions/{type}")
async def get_action(request: Request) -> Response:
    type = request.path_params.get("type")
    if type not in ALLOWED_TYPES:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="400: Bad Request")

    documents = await Action.find_many(Action.type == type).to_list()

    if not documents:
        return Response(status_code=HTTP_204_NO_CONTENT)

    document = random.choice(documents)

    return ORJSONResponse(document.to_dict(request))


@router.get("/actions/r/{id}")
async def get_raw_action_from_id(request: Request) -> Response:
    id = int(request.path_params["id"])

    document = await Action.find_one(Action.id == id)

    if document is None:
        return Response(status_code=HTTP_204_NO_CONTENT)

    return Response(content=document.data, media_type="image/gif")


@router.get("/actions", requires_auth=True)
async def get_all_actions(request: Request) -> Response:
    documents = await Action.find().to_list()

    if not documents:
        return Response(status_code=HTTP_204_NO_CONTENT)

    return ORJSONResponse([document.to_dict(request) for document in documents])


@router.post("/actions/{type}", requires_auth=True)
async def add_action(request: Request) -> Response:
    type = request.path_params["type"]
    if type not in ALLOWED_TYPES:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="400: Bad Request")

    form_data = await request.form(max_fields=1, max_files=1)
    file = form_data.get("file")

    if not isinstance(file, UploadFile):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="400: Bad Request")

    if file.content_type != "image/gif" or not file.size or file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="400: Bad Request")

    total = await Action.find().max(Action.id)  # type: ignore
    id = int(total) + 1 if total else 1

    content = await file.read()
    document = await Action(id=id, type=type, data=content).create()

    return ORJSONResponse(document.to_dict(request), status_code=HTTP_201_CREATED)


@router.delete("/actions/{id}", requires_auth=True)
async def delete_action(request: Request) -> Response:
    id = int(request.path_params["id"])

    deleted = await Action.find_one(Action.id == id).delete_one()

    if deleted is None or deleted.deleted_count < 1:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="404: Not Found")

    return Response(status_code=HTTP_204_NO_CONTENT)
