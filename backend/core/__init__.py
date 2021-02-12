from .user import Person


def get_user(user_id: str) -> Person:
    return Person(user_id=user_id)