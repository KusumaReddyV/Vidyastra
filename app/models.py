from dataclasses import dataclass
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from flask_login import UserMixin

from app import extensions


@dataclass
class User(UserMixin):
    id: str
    email: str
    name: str

    @staticmethod
    def from_document(doc: Optional[dict]):
        if not doc:
            return None
        return User(id=str(doc["_id"]), email=doc["email"], name=doc.get("name", "Student"))

    @staticmethod
    def get_by_id(user_id: str):
        if extensions.mongo_db is None:
            return None
        try:
            oid = ObjectId(user_id)
        except (InvalidId, TypeError):
            return None
        doc = extensions.mongo_db.users.find_one({"_id": oid})
        return User.from_document(doc)

    @staticmethod
    def get_by_email(email: str):
        if extensions.mongo_db is None:
            return None
        doc = extensions.mongo_db.users.find_one({"email": email.lower()})
        return User.from_document(doc)
