from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from backend.app.models import Invite, Person
from backend.app import views


class Visitor:
    """Represents web app visitor and their actions"""

    def __init__(self, user: User):
        try:
            self.id = user.id
            self.person = Person.objects.get(user=user)
        except Person.DoesNotExist as ex:
            raise LookupError(f"User with id {user.id} not in DB") from ex


    @staticmethod
    def register(username: str, password: str, invite: str):
        try:
            code_to_check = Invite.objects.get(code=invite)
            if not code_to_check.used_by:
                user = User.objects.create(username=username, password=password)
                person = Person.objects.create(user=user)
                user.save()
                person.save()
                code_to_check.used_by = user
                code_to_check.save()
                return views.render_homepage()
            else:
                return views.render_register_visitor({"invalid_code": True})
        except Invite.DoesNotExist:
            return views.render_register_visitor({"invalid_code": True})


    @staticmethod
    def login(username: str, password: str):
        user = authenticate(username=username, password=password)
        if not user:
            return views.render_login_visitor({"invalid_credentials": True})
        person = Person.objects.get(user=user)
        assert person
        views.connect_person_to_session(person)
        return views.login_visitor()


    def logout(self):
        return views.logout_visitor()


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
