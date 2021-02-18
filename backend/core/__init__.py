from .visitor import Person


def get_person(user_id: str) -> Person:
    return Person(user_id=user_id)