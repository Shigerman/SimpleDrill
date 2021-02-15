from backend.app.models import Person
from .. import core


class User:
    """Represents logged-in user and their actions"""

    def __init__(self, user_id: str):
        try:
            self.id = user_id
            self.db = Person.objects.get(session__exact=user_id)
        except Person.DoesNotExist as ex:
            raise LookupError(f"User with id {user_id} not in DB") from ex

    @staticmethod
    def register(username: str, password: str, invite: str) -> Person:
        pass


    @staticmethod
    def login(username: str, password: str) -> Person:
        pass
    

    def logout(self):
        pass


    def want_test(self):
        pass


    def submit_test_answer(self, answer: str):
        pass


    def want_drill(self):
        pass


    def select_drill_topic(self, topic: str):
        pass


    def submit_drill_answer(self, answer: str):
        pass


    def give_up_drill(self):
        pass
