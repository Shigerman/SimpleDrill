from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from backend.app.models import Invite, Person
from backend.app import views


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
        # TODO: check invite
        code_to_check = Invite.objects.get(code=invite)
        try:
            if not code_to_check.used_by:
                code_to_check.used_by = user.db
                code_to_check.save()
            user = Person.objects.create_user(name, password)
            person = User.objects.create(user=user)
            user.save()
            person.save()
            return Person
        except DoesNotExist:  # check exception
            return views.render_register_user(context, {"invalid_code": True})
        

    @staticmethod
    def login(username: str, password: str) -> Person:
        user = authenticate(username=username, password=password)
        if not user:
            return # TODO: do something
        person = Person.objects.get(user=user)
        assert person
        views.connect_person_to_session(person)
        return # TODO: logged in
    

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
