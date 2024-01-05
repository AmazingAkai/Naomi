from datetime import datetime

from beanie import Document


class Truth(Document):
    id: int
    truth: str
    created_at: datetime = datetime.utcnow()
