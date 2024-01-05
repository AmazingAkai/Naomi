from __future__ import annotations

from random import randint
from typing import TYPE_CHECKING

from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from naomi.models.challenges import Challenge, ChallengePydantic
from naomi.utils.responses import ORJSONResponse
from naomi.utils.router import Router

if TYPE_CHECKING:
    from typing import Literal

    from starlette.requests import Request
    from starlette.responses import Response

router = Router(base_route="/api")


@router.get("/challenges/{type}")
async def challenges_get(request: Request) -> Response:
    challenge_type = request.path_params.get("type")
    if challenge_type not in ("truth", "dare"):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="404: Not Found")

    total_challenges = await Challenge.find_many(Challenge.type == challenge_type).count()
    if total_challenges < 1:
        return ORJSONResponse(content=None)

    random_id = randint(1, total_challenges)

    challenge = await Challenge.find_one(Challenge.type == challenge_type, Challenge.id == random_id)

    if challenge is None:
        return ORJSONResponse(content=None)

    return ORJSONResponse(content=challenge.to_dict())


@router.post("/challenges/{type}")
async def add_challenge(request: Request) -> Response:
    challenge_type: Literal["truth", "dare"] = request.path_params.get("type")  # type: ignore
    if challenge_type not in ("truth", "dare"):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="404: Not Found")

    try:
        data = await request.json()
        challenge_data = ChallengePydantic(**data)
    except Exception:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="400: Bad Request")

    total_challenges = await Challenge.find_many(Challenge.type == challenge_type).count()
    challenge = await Challenge(id=total_challenges + 1, challenge=challenge_data.challenge, type=challenge_type).create()

    return ORJSONResponse(content=challenge.to_dict())
