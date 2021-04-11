from itertools import cycle
import os
import random
from uuid import uuid4
from dataclasses import dataclass

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse

from backend.app.models import Person, Invite, TestStep, Question, Answer
from backend.app.models import ChallengeSummary, CurrentAnswers, TestSummary
from backend.app import views


@dataclass
class TestExplanationPage:
    foreword: str
    page_to_go_to: str
    btn_text: str


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
                user = User.objects.create_user(  # type: ignore
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
            return redirect(reverse("login-visitor"))

        invites = Invite.objects.all()
        return views.render_invites(invites) # type: ignore


    def add_invite(self, comment: str):
        if not self.person.user.is_staff:
            return redirect(reverse("login-visitor"))

        Invite.objects.create(
            inviter=self.person.user,
            comment=comment,
            code=uuid4().hex)

        return self.show_invites()


    def logout(self):
        views.disconnect_person_from_session(self.person)
        return redirect("/")


    def get_button_test_info(self):
        user_challenges = self.count_user_challenges()
        countdown = self.get_countdown_to_final_test()

        if not user_challenges and not self.visitor_did_start_test():
            button_test_info = "Take the start test"
        elif countdown > 0:
            button_test_info = f"{countdown} drills until final test"
        elif self.visitor_did_final_test():
            button_test_info = "View test scores"
        else:
            button_test_info = "Take the final test"
        return views.render_homepage(button_test_info)


    def show_test_explanation(self):
        countdown: int = self.get_countdown_to_final_test()
        start_test_score, final_test_score = self.count_test_score()

        if not self.visitor_did_start_test():
            return self._offer_test_before_start()
        elif countdown > 0:
            return self._tell_countdown_to_final_test(
                countdown, start_test_score)
        elif self.visitor_did_final_test():
            return self._tell_results_of_two_tests(
                start_test_score, final_test_score)
        else:
            return self._offer_final_test()


    def _offer_test_before_start(self):
        return views.render_explain_test(TestExplanationPage(
            foreword="We recommend that you take our test before you " +
                    "start Python drills.",
            page_to_go_to="/test",
            btn_text="Take the start test",
        ))


    def _tell_countdown_to_final_test(_, countdown, start_test_score):
        return views.render_explain_test(TestExplanationPage(
            foreword=f"Your start test score: {start_test_score}.\n" +
                    f"After doing {countdown} drills you will be able " +
                    "to take the test again.\nGo and practice!",
            page_to_go_to="/select_topic",
            btn_text="Go and practice!",
        ))


    def _tell_results_of_two_tests(_, start_test_score, final_test_score):
        return views.render_explain_test(TestExplanationPage(
            foreword="Congratulations!\n" +
                    "You have completed all the tests.\n" +
                    f"Your start test score: {start_test_score}.\n" +
                    f"Your final test score: {final_test_score}.",
            page_to_go_to="/select_topic",
            btn_text="Go and practice!",
        ))


    def _offer_final_test(self):
        return views.render_explain_test(TestExplanationPage(
            foreword="You have done a lot of drilling.\n" +
                    "It is time to take your final test.",
            page_to_go_to = "/test",
            btn_text = "Take the final test",
        ))


    def count_user_challenges(self) -> int:
        challenges = ChallengeSummary.objects.filter(person=self.person)
        challenges = [challenge.asked_count for challenge in challenges]
        return sum(challenges)


    def get_target_repetitions_count(self):
        return int(os.environ['REPETITION_TARGET'])


    def get_countdown_to_final_test(self) -> int:
        target_challenges = self.get_target_repetitions_count()
        user_challenges = self.count_user_challenges()
        return target_challenges - user_challenges


    def count_test_score(self) -> tuple:
        start_question_count = len(TestStep.objects.filter(topic="start"))
        final_question_count = len(TestStep.objects.filter(topic="final"))

        correct_answers_start = len(TestSummary.objects.filter(
            person=self.person, is_correct=True, topic="start"))
        correct_answers_final = len(TestSummary.objects.filter(
            person=self.person, is_correct=True, topic="final"))

        start_score = f"{correct_answers_start} of {start_question_count}"
        final_score = f"{correct_answers_final} of {final_question_count}"

        if self.visitor_did_final_test():
            return (start_score, final_score,)
        if self.visitor_did_start_test():
            return (start_score, None,)
        else:
            return (None, None)


    def visitor_did_start_test(self) -> bool:
        start_question_count = len(TestStep.objects.filter(topic="start"))
        start_question_user_count = len(TestSummary.objects.filter(
            person=self.person, topic="start"))
        test_was_started = start_question_count == start_question_user_count

        unanswered_questions = len(TestSummary.objects.filter(
            person=self.person, is_correct=None))
        all_answered = unanswered_questions == 0

        return test_was_started and all_answered


    def visitor_did_final_test(self) -> bool:
        test_question_count = len(TestStep.objects.all())
        test_question_user_count = len(
            TestSummary.objects.filter(person=self.person))
        tests_were_started = test_question_count == test_question_user_count

        unanswered_questions = len(TestSummary.objects.filter(
            person=self.person, is_correct=None))
        all_answered = unanswered_questions == 0

        return tests_were_started and all_answered


    def show_test_step(self):
        test_step: TestSummary = self.get_test_summary_step()
        countdown: str = self.get_test_steps_countdown()
        if not test_step:
            test_score = self.count_test_score()
            return views.render_test_score(test_score)
        # return a question and countdown line: e.g. "3 of 10"
        return views.render_test_step(test_step, countdown)  # type: ignore


    def get_test_summary_step(self) -> TestSummary:
        # User takes the start test before doing drills.
        # After doing the target number of drills, they can take final test.
        user_test_step_count = len(TestSummary.objects.filter(
            person=self.person))
        final_question_user_count = len(TestSummary.objects.filter(
            person=self.person, topic="final"))
        countdown = self.get_countdown_to_final_test()
        not_answered_test_steps = TestSummary.objects.filter(
            person=self.person, is_correct=None)

        if not user_test_step_count:
            self.set_test_steps(topic='start')
        elif self.visitor_did_final_test():
            return None  # type: ignore
        elif final_question_user_count == 0 and countdown <= 0:
            self.set_test_steps(topic='final')
        return next(iter(not_answered_test_steps), None)  # type: ignore


    def get_test_steps_countdown(self) -> str:
        # find out how many test steps are there in start/final tests
        not_answered_steps = TestSummary.objects.filter(
            person=self.person, is_correct=None)
        if self.visitor_did_start_test():
            steps_to_do = len(TestStep.objects.filter(topic="final"))
        else:
            steps_to_do = len(TestStep.objects.filter(topic="start"))

        # we need to get a number user is currently doing, so we add 1
        sequential_step_number = steps_to_do - len(not_answered_steps) + 1
        return f"{sequential_step_number} of {steps_to_do}"


    def set_test_steps(self, topic: str):
        test_questions_to_show = TestStep.objects.filter(topic=topic)

        if len(test_questions_to_show) == 0:
            raise Exception("Error: There are no test questions to display")

        # Test steps are to be taken only once each and their quantity
        # in a test is defined, so all test steps are written into db
        # at once so that user is sure to take all obligatory test steps.
        for test_question in test_questions_to_show:
            TestSummary(
                person=self.person,
                test_question=test_question,
                topic=topic).save()


    def submit_test_answer(self, test_answer: str = None):
        if not test_answer:
            raise AssertionError("Test answer submit without a test question")
        return self.check_test_answer(test_answer)
    

    def check_test_answer(self, test_answer: str = None):
        # Save True/False into db depending on answer correctness.
        # Also save the actual user answer to check our check correctness.
        test_summary_step = self.get_test_summary_step()
        test_answer = test_answer.lower()
        correct_test_answer = test_summary_step.test_question.test_answer

        is_correct_user_answer = correct_test_answer in test_answer
        # 5 is taken here to omit unneseccary symbols, spaces, dots, etc
        answer_not_long = len(test_answer) <= (len(correct_test_answer) + 5)

        if is_correct_user_answer and answer_not_long:
            test_summary_step.is_correct = True
        else:
            test_summary_step.is_correct = False
        test_summary_step.user_answer = test_answer
        test_summary_step.save()
        return self.show_test_step()


    def want_to_drill(self, topic: str):
        # if topic is new, delete answers saved for previous topic
        if self.person.challenge_topic != topic:
            CurrentAnswers.objects.filter(person=self.person).delete()
            self.person.challenge_topic = topic
            self.person.save()
        return redirect(reverse("drill-topic"))


    def show_challenge(self):
        challenge = get_current_challenge(self)
        if not challenge:
            return self.get_next_challenge()
        return views.render_challenge(challenge)


    def get_next_challenge(self):
        challenge = get_new_challenge(self)
        set_new_challenge(self, challenge)
        return views.render_challenge(challenge)


class Challenge:

    def __init__(self, visitor):
        self.visitor = visitor
        self.question: Question = None  # type: ignore
        self.answers: list[Answer] = []
        # If True, show correct/wrong answers after user answers wrongly
        # or issued the "don't know" command
        self.disclose_answers: bool = False


def get_current_challenge(visitor: Visitor) -> Challenge:
    saved_answers = CurrentAnswers.objects.filter(person=visitor.person)
    if not saved_answers:
        return None  # type: ignore

    challenge = Challenge(visitor)
    # Don't keep question in DB, infer it from answer
    any_answer = next(iter(saved_answers))
    challenge.question = Answer.objects.get(pk=any_answer.answer_id).question
    challenge.answers = [
        Answer.objects.get(pk=answer.answer_id) for answer in saved_answers
    ]
    challenge.disclose_answers = visitor.person.disclose_answers

    return challenge


def get_new_challenge(visitor: Visitor):
    challenge = Challenge(visitor)
    topic = visitor.person.challenge_topic
    topic_challenges = ChallengeSummary.objects.filter(
            person=visitor.person, question__topic=topic)

    # When a new topic is chosen by the user, all questions in this topic
    # are written into ChallengSummary db table for this user.
    if len(topic_challenges) == 0:
        set_topic_challenges(visitor, topic=topic)
        topic_challenges = ChallengeSummary.objects.filter(
            person=visitor.person, question__topic=topic)

    # Select the question that was asked less number of times.
    asked_counts: list[int] = \
        [challenge.asked_count for challenge in topic_challenges]
    min_asked_count = min(asked_counts, default=0)

    challenges_to_show = cycle([challenge for challenge in topic_challenges
        if challenge.asked_count == min_asked_count])
    challenge.question = next(challenges_to_show).question

    # choose four random answers from the question answer set
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


def set_new_challenge(visitor: Visitor, challenge: Challenge):
    # Save 4 answers belonging to the last question shown to user to
    # retrieve it if user makes a pause. Delete old answers before that.
    CurrentAnswers.objects.filter(person=visitor.person).delete()
    for answer in challenge.answers:
        CurrentAnswers(person=visitor.person, answer=answer).save()
    visitor.person.disclose_answers = challenge.disclose_answers
    visitor.person.save()


def set_topic_challenges(visitor: Visitor, topic: str):
    topic_questions = Question.objects.filter(topic=topic)

    if len(topic_questions) == 0:
        raise Exception("Error: There are no questions to display")

    for question in topic_questions:
        ChallengeSummary(person=visitor.person, question=question).save()


def submit_drill_answer(visitor: Visitor, answer_id: int = None,
        no_correct_answer: bool = None):
    challenge = get_current_challenge(visitor)

    if not challenge:
        raise AssertionError("Answer submit without challenge")

    if no_correct_answer is not None:
        challenge.disclose_answers = True
        if any(v.is_correct for v in challenge.answers):
            set_new_challenge(visitor, challenge)
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
            set_new_challenge(visitor, challenge)
            return views.render_challenge(challenge, is_failure = True)


def give_up_drill(visitor: Visitor):
    challenge = get_current_challenge(visitor)
    if not challenge:
        raise AssertionError("Answer submit without challenge")

    challenge.disclose_answers = True
    return views.render_challenge(challenge, is_failure = True)
