from backend.app.models import Person
from .visitor import Visitor


def get_person(user_id: str) -> Person:
    return Person(user_id=user_id)
