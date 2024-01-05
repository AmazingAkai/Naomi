from beanie import Document


class User(Document):
    name: str
    password: str
