from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Person, Invite, TestStep, TestSummary, Question
from .models import CurrentAnswers
from backend import core

def create_person():
    User = get_user_model()
    user = User.objects.create_user(
               username="middlemanperson",
               password="bar")
    person = core.user.Person()
    person.user = user
    user.save()
    person.save()
    return person


def save_test_questions_to_db():
    for _ in range(5):
        TestStep(
            topic="start",
            test_question=SAMPLE_TESTQUESTION_TEXT,
            test_answer="128").save()
        TestStep(
            topic="final",
            test_question=SAMPLE_TESTQUESTION_TEXT,
            test_answer="128").save()


def save_questions_and_answers_to_db():
    for _ in range(5):
        Question(
            question_text=SAMPLE_QUESTION_TEXT,
            theory_text=SAMPLE_THEORY_TEXT,
            topic=SAMPLE_TOPIC_TEXT).save()
    all_questions = Question.objects.all()
    for question in all_questions:
        for _ in range(4):
            Answer(question=question, answer_text="No", correct=False).save()
        for _ in range(1):
            Answer(question=question, answer_text="Yes", correct=True).save()


SAMPLE_QUESTION_TEXT = "What is a callable?"
SAMPLE_TESTQUESTION_TEXT = "How many characters are there in ASCII?"
SAMPLE_EXPLANATION_TEXT = "Function"
SAMPLE_TOPIC_TEXT = "git"


class PersonTests(TestCase):
    def test_create_person(self):
        person = create_person()
        self.assertEqual(person.user.username, "middlemanperson")
        self.assertTrue(person.user.is_active)
        self.assertFalse(person.user.is_staff)
        self.assertFalse(person.user.is_superuser)
        try:
            self.assertIsNotNone(person.user.email)
        except AttributeError:
            pass


    def test_save_invite_to_db(self):
        User = get_user_model()
        invited_user = User.objects.create_user(
               username="itperson",
               password="foo")
        invited_user.save()
        invited_person = core.user.Person()
        invited_person.user = invited_user
        invited_person.save()

        Invite(code="grihts65hoijr",
               inviter=create_person(),
               used_by=invited_person,
               comment="IvanIvanov").save()
        invite = Invite.objects.get(comment="IvanIvanov")
        self.assertEqual(invite.code, "grihts65hoijr")
        self.assertEqual(invite.inviter.user.username, "middlemanperson")
        self.assertEqual(invite.used_by.user.username, "itperson")


class UserTests(TestCase):
    def test_save_teststep_to_db(self):
        TestStep(
            topic=SAMPLE_TOPIC_TEXT,
            test_question=SAMPLE_TESTQUESTION_TEXT,
            test_answer='128').save()
        test_step = TestStep.objects.get(
            topic=SAMPLE_TOPIC_TEXT,
            test_question=SAMPLE_TESTQUESTION_TEXT)
        self.assertEqual(test_step.test_answer, "128")
        self.assertIsNotNone(test_step)


class Challengetests(TestCase):
    def test_save_question_to_db(self):
        Question(
            question_text=SAMPLE_QUESTION_TEXT,
            explanation_text=SAMPLE_EXPLANATION_TEXT,
            topic=SAMPLE_TOPIC_TEXT).save()
        question = Question.objects.get(question_text=SAMPLE_QUESTION_TEXT)
        self.assertIsNotNone(question)
        self.assertTrue(question.question_text == SAMPLE_QUESTION_TEXT)
        self.assertTrue(question.explanation_text == SAMPLE_EXPLANATION_TEXT)
        self.assertTrue(question.topic == SAMPLE_TOPIC_TEXT)
