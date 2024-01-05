from datetime import datetime
from typing import Literal

from beanie import Document
from pydantic import BaseModel


class Challenge(Document):
    id: int
    type: Literal["truth", "dare"]
    challenge: str
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "challenges"

    def to_dict(self) -> dict:
        return {"id": self.id, "type": self.type, "challenge": self.challenge, "created_at": self.created_at}


class ChallengePydantic(BaseModel):
    challenge: str
