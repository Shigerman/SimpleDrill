import os
import urllib
from uuid import uuid4
from collections import namedtuple

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from threadlocals.threadlocals import get_current_request
from dotenv import load_dotenv

from backend.app.models import Invite, Person, ChallengeSummary
from backend.app.models import TestStep, TestSummary
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


    def show_test_explanation_before_test(self):
        user_challenges_count = self.count_user_challenges()
        countdown = self.get_countdown_to_final_test()

        start_test_score, final_test_score = self.count_test_score()
        Explanation = namedtuple('Explanation', 'text page_to_go_to')

        if not user_challenges_count and not self.user_did_start_test():
            text = ("We recommend that you take our test before you start" +
                " Python drills.")
            page_to_go_to = "/test"
        elif countdown > 0:
            text = (f"Your start test score: {start_test_score}.\nAfter doing " +
                f"{countdown} drills you will be able to take the test again."
                +"\nGo and practice!")
            page_to_go_to = "/select_topic"
        elif self.user_did_final_test():
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
        challenges = ChallengeSummary.objects.filter(person=self.person)
        challenges = [challenge.asked_count for challenge in challenges]
        return sum(challenges)


    def get_target_repetitions_count(self):
        load_dotenv()
        return int(os.environ['REPETITION_TARGET'])


    def get_countdown_to_final_test(self):
        target_challenges = self.get_target_repetitions_count()
        user_challenges = self.count_user_challenges()
        return target_challenges - user_challenges


    def count_test_score(self):
        start_question_count = len(TestStep.objects.filter(topic="start"))
        final_question_count = len(TestStep.objects.filter(topic="final"))

        correct_answers_start = len(TestSummary.objects.filter(
            person=self.person, is_user_answer_correct=True, topic="start"))
        correct_answers_final = len(TestSummary.objects.filter(
            person=self.person, is_user_answer_correct=True, topic="final"))

        start_score = f"{correct_answers_start} of {start_question_count}"
        final_score = f"{correct_answers_final} of {final_question_count}"

        if self.user_did_final_test():
            return (start_score, final_score,)
        if self.user_did_start_test():
            return (start_score, None,)
        else:
            return (None, None)


    def user_did_start_test(self):
        start_question_count = len(TestStep.objects.filter(topic="start"))
        start_question_user_count = len(TestSummary.objects.filter(
            person=self.person, topic="start"))
        not_answered_user_test_steps_count = len(TestSummary.objects.filter(
            person=self.person, is_user_answer_correct=None))

        if start_question_count == start_question_user_count and \
            not not_answered_user_test_steps_count:
            return True
        else:
            return False


    def user_did_final_test(self):
        test_question_count = len(TestStep.objects.all())
        test_question_user_count = len(
            TestSummary.objects.filter(person=self.person))
        not_answered_user_test_steps_count = len(TestSummary.objects.filter(
            person=self.person, is_user_answer_correct=None))

        if test_question_count == test_question_user_count and \
            not not_answered_user_test_steps_count:
            return True
        else:
            return False


    def show_test_step(self):
        test_step = self.get_test_step()
        if not test_step:
            test_score = self.count_test_score()
            return views.render_test_score(test_score)
        return views.render_test_step(test_step)


    def get_test_step(self):
        # User takes the start test before doing drills.
        # After doing the target number of drills, they can take final test.
        user_test_step_count = len(TestSummary.objects.filter(
            person=self.person))
        final_question_user_count = len(TestSummary.objects.filter(
            person=self.person, topic="final"))
        not_answered_test_steps = TestSummary.objects.filter(
            person=self.person, is_user_answer_correct=None)
        countdown = self.get_countdown_to_final_test()

        if not user_test_step_count:
            self.set_test_steps(topic='start')
        elif self.user_did_final_test():
            return None
        elif final_question_user_count == 0 and countdown <= 0:
            set_test_steps(visitor, topic='final')
        return next(iter(not_answered_test_steps), None)


    def set_test_steps(self, topic):
        test_questions_to_show = TestStep.objects.filter(topic=topic)

        if len(test_questions_to_show) == 0:
            raise Exception("500 internal server error")

        # Unlike challenges, test steps are supposed to be taken only
        # once each and their quantity in a test is defined, so all test
        # steps are written into db at once so that user is sure to take
        # all obligatory test steps.
        for test_question in test_questions_to_show:
            TestSummary(
                person=self.person,
                test_question=test_question,
                topic=topic).save()


    def submit_test_answer(self, test_answer: str):
        if not test_answer:
            raise AssertionError("Test answer submit without a test question")
        return self.check_test_answer(test_answer)
    

    def check_test_answer(self, test_answer=None):
        # Save True/False into db depending on answer correctness.
        # Also save the actual user answer to check our check correctness.
        test_step = self.get_test_step()
        test_answer = test_answer.lower()
        correct_test_answer = test_step.test_question.test_answer

        is_correct_user_answer = correct_test_answer in test_answer
        # 5 is taken here to omit unneseccary symbols, spaces, dots, etc
        user_answer_not_long = len(test_answer) <= (len(correct_test_answer) + 5)

        if is_correct_user_answer and user_answer_not_long:
            test_step.is_user_answer_correct = True
        else:
            test_step.is_user_answer_correct = False
        test_step.user_answer = test_answer
        test_step.save()
        return self.show_test_step()


    def want_drill(self):
        pass


    def select_drill_topic(self, topic: str):
        pass


    def submit_drill_answer(self, answer: str):
        pass


    def give_up_drill(self):
        pass
