from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # If user answered challenge wrongly or issued the "I don't know"
    # command, disclose answers until the "next challenge" command.
    disclose_answers = models.BooleanField(null=True)
    challenge_topic = models.TextField(null=True)

    def __str__(self):
        return f"{self.user.username} admin {self.user.is_staff}"


class Invite(models.Model):
    code = models.TextField(default="")
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invite_issuer')
    used_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invite_taker', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    comment = models.TextField(default="", null=True)

    def __str__(self):
        return f"\"{self.comment}\" used by {self.used_by}"


class TestStep(models.Model):
    topic = models.TextField(default="")
    test_question = models.TextField()
    test_answer = models.TextField(default="")


class TestSummary(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    test_question = models.ForeignKey(TestStep, on_delete=models.CASCADE)
    topic = models.TextField(default="")
    user_answer = models.CharField(max_length=50)
    is_user_answer_correct = models.BooleanField(null=True)


class Question(models.Model):
    question_text = models.TextField()
    explanation_text = models.TextField(default="")
    topic = models.TextField(default="")


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)


class CurrentAnswers(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)


class ChallengeSummary(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    asked_count = models.IntegerField(default=1)
