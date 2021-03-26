from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Person, Invite, TestStep, Question, Answer
from .models import TestSummary
from backend import core


SAMPLE_TESTQUESTION_TEXT = "How many characters are there in ASCII?"
SAMPLE_QUESTION_TEXT = "What is a callable?"
SAMPLE_EXPLANATION_TEXT = "Function"
SAMPLE_TOPIC_TEXT = "git"


def create_person():
    User = get_user_model()
    user = User.objects.create_user(  # type: ignore
        username="exampleperson",
        password="bar")
    person = Person.objects.create(user=user)
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


def do_start_test_for_user(visitor, answer_bool):
    test_steps_to_show = TestStep.objects.filter(topic="start")
    for test_step in test_steps_to_show:
        TestSummary(
            user=visitor.user,
            topic="start",
            test_question=test_step,
            is_correct=answer_bool).save()


def do_final_test_for_user(visitor, answer_bool):
    test_steps_to_show = TestStep.objects.filter(topic="final")
    for test_step in test_steps_to_show:
        TestSummary(
            user=visitor.user,
            topic="final",
            test_question=test_step,
            is_correct=answer_bool).save()


def save_questions_and_answers_to_db():
    for _ in range(5):
        Question(
            question_text=SAMPLE_QUESTION_TEXT,
            explanation_text=SAMPLE_EXPLANATION_TEXT,
            topic=SAMPLE_TOPIC_TEXT).save()
    all_questions = Question.objects.all()
    for question in all_questions:
        for _ in range(4):
            Answer(question=question, answer_text="No", correct=False).save()
        for _ in range(1):
            Answer(question=question, answer_text="Yes", correct=True).save()


class PersonModelTests(TestCase):
    def test_create_person(self):
        person = create_person()
        self.assertEqual(person.user.username, "exampleperson")
        self.assertTrue(person.user.is_active)
        self.assertFalse(person.user.is_staff)
        self.assertFalse(person.user.is_superuser)
        try:
            self.assertIsNotNone(person.user.email)
        except AttributeError:
            pass


    def test_create_superuser(self):
        user = get_user_model()
        admin_user = user.objects.create_superuser(
            'superuser', 'super@user.com', 'foo')
        self.assertEqual(admin_user.username, 'superuser')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        with self.assertRaises(ValueError):
            user.objects.create_superuser(
                username='superuser',
                email='super@user.com',
                password='foo',
                is_superuser=False)

    def test_save_invite_to_db(self):
        user = get_user_model()
        invited_user = user.objects.create_user(  # type: ignore
               username="itperson",
               password="foo")
        invited_user.save()
        invited_person = core.Person()
        invited_person.user = invited_user
        invited_person.save()

        Invite(code="grihts65hoijr",
               inviter=create_person().user,
               used_by=invited_person.user,
               comment="IvanIvanov").save()
        invite = Invite.objects.get(comment="IvanIvanov")
        self.assertEqual(invite.code, "grihts65hoijr")
        self.assertEqual(invite.inviter.username, "exampleperson")
        self.assertEqual(invite.used_by.username, "itperson")


class UserTestModelTests(TestCase):
    def test_start_testquestions_are_written_into_db_for_user(self):
        visitor = create_person()
        save_test_questions_to_db()
        start_question_count = len(TestStep.objects.filter(topic="start"))

        backend.core.visitor.set_test_steps(visitor=visitor, topic="start")
        user_start_question_count = len(TestSummary.objects.filter(
            user=visitor, topic="start"))
        self.assertEqual(start_question_count, user_start_question_count)


class ChallengeModelTests(TestCase):
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
