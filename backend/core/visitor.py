from collections import namedtuple
import os
import random
import urllib
from uuid import uuid4

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from threadlocals.threadlocals import get_current_request

from backend.app.models import Invite, Person
from backend.app.models import ChallengeSummary, CurrentAnswers
from backend.app.models import TestSummary, TestStep, Answer, Question
from backend.app import views


class Visitor:
    """Represents web app visitor and their actions"""

    def __init__(self, user: User):
        try:
            self.person = Person.objects.get(user=user)
        except Person.DoesNotExist as ex:
            raise LookupError(f"No person for {user} in DB") from ex


    @staticmethod
    def register(username: str, password: str, invite: str):
        try:
            code_to_check = Invite.objects.get(code=invite)
            if not code_to_check.used_by:
                user = User.objects.create_user(
                    username, email := None, password)
                person = Person.objects.create(user=user)
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

        Invite.objects.create(
            inviter=self.person.user,
            comment=comment,
            code=uuid4().hex)

        return self.show_invites()


    def logout(self):
        views.disconnect_person_from_session(self.person)
        return redirect("/")


    def show_test_explanation_before_test(self):
        user_challenges_count = self.count_user_challenges()
        countdown = self.get_countdown_to_final_test()

        start_test_score, final_test_score = self.count_test_score()
        Explanation = namedtuple('Explanation', 'text page_to_go_to')

        if not user_challenges_count and not self.visitor_did_start_test():
            text = ("We recommend that you take our test before you start" +
                " Python drills.")
            page_to_go_to = "/test"
        elif countdown > 0:
            text = (f"Your start test score: {start_test_score}.\nAfter " +
                f"doing {countdown} drills you will be able to take the " +
                "test again.\nGo and practice!")
            page_to_go_to = "/select_topic"
        elif self.visitor_did_final_test():
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

        if self.visitor_did_final_test():
            return (start_score, final_score,)
        if self.visitor_did_start_test():
            return (start_score, None,)
        else:
            return (None, None)


    def visitor_did_start_test(self):
        start_question_count = len(TestStep.objects.filter(topic="start"))
        start_question_user_count = len(TestSummary.objects.filter(
            person=self.person, topic="start"))
        test_was_started = start_question_count == start_question_user_count

        unanswered_questions = len(TestSummary.objects.filter(
            person=self.person, is_user_answer_correct=None))
        all_answered = unanswered_questions == 0

        return test_was_started and all_answered


    def visitor_did_final_test(self):
        test_question_count = len(TestStep.objects.all())
        test_question_user_count = len(
            TestSummary.objects.filter(person=self.person))
        tests_were_started = test_question_count == test_question_user_count

        unanswered_questions = len(TestSummary.objects.filter(
            person=self.person, is_user_answer_correct=None))
        all_answered = unanswered_questions == 0

        return tests_were_started and all_answered


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
        elif self.visitor_did_final_test():
            return None
        elif final_question_user_count == 0 and countdown <= 0:
            set_test_steps(visitor, topic='final')
        return next(iter(not_answered_test_steps), None)


    def set_test_steps(self, topic):
        test_questions_to_show = TestStep.objects.filter(topic=topic)

        if len(test_questions_to_show) == 0:
            raise Exception("500 internal server error")

        # Test steps are to be taken only once each and their quantity
        # in a test is defined, so all test steps are written into db
        # at once so that user is sure to take all obligatory test steps.
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
        user_answer_not_long = \
            len(test_answer) <= (len(correct_test_answer) + 5)

        if is_correct_user_answer and user_answer_not_long:
            test_step.is_user_answer_correct = True
        else:
            test_step.is_user_answer_correct = False
        test_step.user_answer = test_answer
        test_step.save()
        return self.show_test_step()


    def want_to_drill(self, topic: str):
        self.person.challenge_topic = topic
        self.person.save()
        return redirect("/drill_topic")


    def show_challenge(self):
        challenge = get_current_challenge(self)
        if not challenge:
            challenge = get_next_challenge(self)
            # write into db 4 answers belonging to the last question shown
            # to user to get back to the question if user makes a pause
            set_current_challenge(self, challenge)
        return views.render_challenge(challenge)


def get_current_challenge(visitor):
    saved_answers = CurrentAnswers.objects.filter(person=visitor.person)
    if not saved_answers:
        return None

    challenge = Challenge(visitor)
    # Don't keep question in DB, infer it from answer
    first_answer = next(iter(saved_answers))
    challenge.question = Answer.objects.get(pk=first_answer.answer_id).question
    challenge.answers = [
        Answer.objects.get(pk=answer.answer_id) for answer in saved_answers
    ]
    challenge.disclose_answers = visitor.person.disclose_answers

    return challenge


def get_next_challenge(visitor):
    challenge = Challenge(visitor)
    topic = visitor.person.challenge_topic
    user_topic_challenges = ChallengeSummary.objects.filter(
            person=visitor.person, question__topic=topic)

    # When a new topic is chosen by the user, all questions in this topic
    # are written into ChallengSummary db table for this user, and can
    # then be answered by the user many times (times are counted).
    if len(user_topic_challenges) == 0:
        set_topic_challenges(visitor, topic=topic)

    # Select next question based on challenge history: the one that was
    # asked less number of times.
    asked_counts: list[int] = \
        [challenge.asked_count for challenge in user_topic_challenges]
    min_asked_count = min(asked_counts, default=0)
    challenges_to_show = [challenge for challenge in user_topic_challenges
        if challenge.asked_count == min_asked_count]
    challenge.question = next(iter(challenges_to_show)).question

    # choose four random answers frim the question answer set
    answers_to_question = list(challenge.question.answer_set.all())
    answers_on_screen = 4
    challenge.answers = random.sample(answers_to_question, answers_on_screen)

    # increment the number of times asked for the question
    record = ChallengeSummary.objects.get(
        person=visitor.person,
        question=challenge.question)
    record.asked_count += 1
    record.save()

    return challenge


def set_current_challenge(visitor, challenge):
    # Write into db 4 answers belonging to the last question shown to user.
    # But in the beginning delete old answers if there are any.
    CurrentAnswers.objects.filter(person=visitor.person).delete()
    for answer in challenge.answers:
        CurrentAnswers(person=visitor.person, answer=answer).save()
    visitor.person.disclose_answers = challenge.disclose_answers
    visitor.person.save()


def set_topic_challenges(visitor, topic):
    topic_questions = Question.objects.filter(topic=topic)

    if len(topic_questions) == 0:
        raise Exception("500 internal server error")

    for question in topic_questions:
        ChallengeSummary(person=visitor.person, question=question).save()


def submit_drill_answer(visitor, answer_id=None, no_correct_answer=None):
    challenge = get_current_challenge(visitor)

    if not challenge:
        raise AssertionError("Answer submit without challenge")

    if no_correct_answer is not None:
        challenge.disclose_answers = True
        if any(v.is_correct for v in challenge.answers):
            set_current_challenge(visitor, challenge)
            return views.render_challenge(challenge, is_failure=True)
        else:
            return views.render_challenge(challenge, is_failure=False)

    else:
        is_specified = lambda v: v.pk == answer_id
        answer = next(filter(is_specified, challenge.answers), None)
        if not answer:
            return views.render_challenge(challenge,
                with_error="The submitted answer does not match current \
                    question. Try again on this page with actual answers.")
        challenge.disclose_answers = True
        if answer.is_correct:
            return views.render_challenge(challenge, is_failure = False)
        else:
            set_current_challenge(visitor, challenge)
            return views.render_challenge(challenge, is_failure = True)


def give_up_drill(visitor):
    challenge = get_current_challenge(visitor)
    if not challenge:
        raise AssertionError("Answer submit without challenge")

    challenge.disclose_answers = True
    return views.render_challenge(challenge, is_failure = True)


class Challenge:

    def __init__(self, visitor):
        self.visitor = visitor
        self.question: Question = None
        self.answers: list[Answer] = []
        # If True, show correct/wrong answers after user answers wrongly
        # or issued the "don't know" command
        self.disclose_answers = False
