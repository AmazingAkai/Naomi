from __future__ import annotations

import random
from datetime import datetime
from typing import TYPE_CHECKING

import orjson
from beanie.operators import In
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from naomi.models.challenges import Challenge, ChallengePydantic
from naomi.utils.responses import ORJSONResponse
from naomi.utils.router import Router

if TYPE_CHECKING:
    from starlette.requests import Request

router = Router(base_route="/api")


@router.get("/challenges/{type}")
async def challenges_get(request: Request) -> Response:
    challenge_type = request.path_params.get("type")
    if challenge_type not in ("truth", "dare", "wyr"):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="400: Bad Request")

    ratings = orjson.loads(request.query_params.get("rating", '["PG", "PG13"]'))
    for rating in ratings:
        if not rating in ("PG", "PG13", "R"):
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="400: Bad Request")

    challenges = await Challenge.find_many(Challenge.type == challenge_type, In(Challenge.rating, ratings)).to_list()

    if not challenges:
        return Response(status_code=HTTP_204_NO_CONTENT)

    challenge = random.choice(challenges)

    return ORJSONResponse(challenge.to_dict())


@router.get("/challenges", requires_auth=True)
async def challenges_get_all(request: Request) -> Response:
    challenges = await Challenge.find().to_list()

    if not challenges:
        return Response(status_code=HTTP_204_NO_CONTENT)

    return ORJSONResponse([challenge.to_dict() for challenge in challenges])


@router.post("/challenges/{type}", requires_auth=True)
async def add_challenge(request: Request) -> Response:
    challenge_type = request.path_params.get("type")
    if not challenge_type or challenge_type not in ("truth", "dare", "wyr"):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="400: Bad Request")

    data = await request.json()
    ChallengePydantic(**data)

    total_challenges = await Challenge.find().max(Challenge.id)  # type: ignore
    id = int(total_challenges) + 1 if total_challenges else 1
    challenge = await Challenge(id=id, type=challenge_type, created_at=datetime.utcnow(), **data).create()

    return ORJSONResponse(challenge.to_dict(), status_code=HTTP_201_CREATED)


@router.delete("/challenges/{challenge_id}", requires_auth=True)
async def delete_challenge(request: Request) -> Response:
    challenge_id = int(request.path_params["challenge_id"])

    deleted = await Challenge.find_one(Challenge.id == challenge_id).delete_one()

    if deleted is None or deleted.deleted_count < 1:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="404: Not Found")

    return Response(status_code=HTTP_204_NO_CONTENT)


@router.patch("/challenges/{challenge_id}", requires_auth=True)
async def update_challenge(request: Request) -> Response:
    challenge_id = int(request.path_params["challenge_id"])

    challenge = await Challenge.find_one(Challenge.id == challenge_id)
    if challenge is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="404: Not Found")

    data = await request.json()
    challenge_data = ChallengePydantic(**data, rating=challenge.rating)

    await challenge.set({Challenge.challenge: challenge_data.challenge})
    return Response(status_code=HTTP_204_NO_CONTENT)
