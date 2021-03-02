import urllib
from uuid import uuid4

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from threadlocals.threadlocals import get_current_request

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
                user = User.objects.create_user(
                    username, email := None, password)
                person = Person.objects.create(user=user)
                user.save()
                person.save()
                code_to_check.used_by = user
                code_to_check.save()
                views.connect_person_to_session(person)
                return redirect("/")
            else:
                return views.render_register_visitor(
                    empty_field=False, invalid_code=True)
        except Invite.DoesNotExist:
            return views.render_register_visitor(
                    empty_field=False, invalid_code=True)


    @staticmethod
    def login(username: str, password: str):
        user = authenticate(username=username, password=password)
        if not user:
            return views.render_login_visitor(invalid_credentials=True)
        person = Person.objects.get(user=user)
        assert person
        views.connect_person_to_session(person)
        return redirect("/")


    def show_invites(self):
        if not self.person.user.is_staff:
            return redirect("/login_visitor")

        invites = Invite.objects.all()
        return views.render_invites(invites)


    def add_invite(self, comment):
        if not self.person.user.is_staff:
            return redirect("/login_visitor")

        invite = Invite.objects.create(
            inviter = self.person.user,
            comment = comment,
            code = uuid4().hex).save()

        return self.show_invites()


    def logout(self):
        views.disconnect_person_from_session(self.person)
        return redirect("/")


    def want_test(self):
        pass


    def show_test_explanation(self):
        user_challenges_count = count_user_challenges(self)
        countdown = get_countdown_to_final_test(self)

        start_test_score, final_test_score = count_test_score(self)
        Explanation = namedtuple('Explanation', 'text page_to_go_to')

        if not user_challenges_count and not user_did_start_test(self):
            text = ("We recommend that you take our test before you start" +
                " Python drills.")
            page_to_go_to = "/test"
        elif countdown > 0:
            text = (f"Your start test score: {start_test_score}.\nAfter doing " +
                f"{countdown} drills you will be able to take the test again."
                +"\nGo and practice!")
            page_to_go_to = "/select_topic"
        elif user_did_final_test(self):
            text = ("Congratulations!\nYou have completed all the tests."
                + f"\nYour start test score: {start_test_score}.\nYour final "
                +f"test score: {final_test_score}.\nGo and practice more!")
            page_to_go_to = "/select_topic"
        else:
            text = ("You have done a lot of drilling.\n" +
                "It is time to take your final test.")
            page_to_go_to = "/test"
        test_explanation = Explanation(text,page_to_go_to)
        return views.render_explain_test(test_explanation)


    def count_user_challenges(self):
        challenges = ChallengeSummary.objects.filter(user=self.person.user)
        challenges = [challenge.asked_count for challenge in challenges]
        return sum(challenges)


    def get_target_repetitions_count(self):
        load_dotenv()
        return int(os.environ['REPETITION_TARGET'])


    def get_countdown_to_final_test(self):
        pass


    def count_test_score(self):
        pass


    def user_did_start_test(self):
        pass


    def user_did_final_test(self):
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
